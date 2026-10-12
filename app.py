"""Postcard Scout — live place discovery and AI illustrated postcards, stdlib only."""
import json, os, time, uuid, threading, urllib.parse, urllib.request
from pathlib import Path
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from planner import optimize
ROOT=Path(__file__).parent
SEARCHES={}; JOBS={}; LOCK=threading.Lock()

def load_env():
    p=ROOT/'.env'
    if p.exists():
        for line in p.read_text().splitlines():
            if '=' in line and not line.startswith('#'):
                k,v=line.split('=',1);os.environ.setdefault(k.strip(),v.strip().strip('"\''))

def request_json(url,body=None,key=None):
    headers={'Content-Type':'application/json'}
    if key: headers['Authorization']='Key '+key
    req=urllib.request.Request(url,data=json.dumps(body).encode() if body is not None else None,headers=headers)
    with urllib.request.urlopen(req,timeout=45) as r: return json.load(r)

def discover(city,interest):
    key=os.environ.get('SERPAPI_API_KEY')
    if not key: raise ValueError('Configure SERPAPI_API_KEY in .env')
    q=f'{interest} places in {city}'
    data=request_json('https://serpapi.com/search.json?'+urllib.parse.urlencode({'engine':'google_maps','q':q,'type':'search','hl':'en','api_key':key}))
    if data.get('error'): raise ValueError('SerpApi could not return results.')
    places=[]
    for i,r in enumerate(data.get('local_results',[])[:6]):
        if not r.get('title') or not r.get('place_id'):continue
        place={k:r.get(k) for k in ('title','place_id','rating','reviews','address','description','type','open_state','website','gps_coordinates')}
        place['maps_url']='https://www.google.com/maps/search/?api=1&query='+urllib.parse.quote(r['title']+' '+city)+'&query_place_id='+urllib.parse.quote(r['place_id'])
        places.append(place)
    sid=str(uuid.uuid4());result={'id':sid,'city':city,'interest':interest,'query':q,'fetched_at':datetime.now(timezone.utc).isoformat(),'places':places,'searches_used':1,'search_id':data.get('search_metadata',{}).get('id')}
    with LOCK:SEARCHES[sid]=result
    return result

def make_prompt(search,place):
    description=(place.get('description') or place.get('type') or 'local attraction')[:600]
    trail = search.get('plan')
    if trail:
        names = ', '.join(p['title'] for p in trail['stops'])
        return f"An illustrated triptych travel postcard inspired by a heritage trail in {search['city']}: {names}. Three distinct scenic panels, one for each named landmark. Gouache, warm terracotta and deep indigo, cream paper, editorial art, no text. Conceptual illustration, not documentary evidence."
    return f"An illustrated travel postcard inspired by {place['title']} in {search['city']}. Visual inspiration from this live place listing: {description}. Hand painted gouache, warm terracotta, cream paper texture, deep indigo accents, elegant editorial composition, no text, no lettering. This is conceptual illustration, not a documentary photograph."

def generate(jid,search,place):
    try:
        key=os.environ.get('FAL_KEY') or os.environ.get('FAL_API_KEY')
        if not key:raise ValueError('Configure FAL_KEY in .env')
        prompt=make_prompt(search,place)
        handle=request_json('https://queue.fal.run/fal-ai/flux/schnell',{'prompt':prompt,'image_size':'landscape_4_3','num_images':1,'num_inference_steps':4,'enable_safety_checker':True},key)
        JOBS[jid].update(status='Generating illustration',request_id=handle['request_id'],prompt=prompt)
        deadline=time.monotonic()+180
        while time.monotonic()<deadline:
            state=request_json(handle['status_url'],key=key)
            if state['status']=='COMPLETED':
                if state.get('error'):raise ValueError('fal generation failed')
                result=request_json(handle['response_url'],key=key)
                if any(result.get('has_nsfw_concepts',[])):raise ValueError('Image was blocked by the safety checker')
                JOBS[jid].update(status='Complete',image_url=result['images'][0]['url'],seed=result.get('seed'),completed_at=datetime.now(timezone.utc).isoformat());return
            time.sleep(1)
        raise TimeoutError('Generation timed out. Check fal request '+handle['request_id'])
    except Exception:
        JOBS[jid].update(status='Failed',error='Image generation failed. Check your fal key, credits and endpoint availability.')

class Handler(BaseHTTPRequestHandler):
    def send_json(self,result,code=200):
        self.send_response(code);self.send_header('Content-Type','application/json');self.end_headers();self.wfile.write(json.dumps(result).encode())
    def do_GET(self):
        if self.path=='/':
            self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.end_headers();self.wfile.write((ROOT/'index.html').read_bytes())
        elif self.path.startswith('/api/jobs/'):
            job=JOBS.get(self.path.split('/')[-1]); self.send_json(job or {'error':'Unknown job'},200 if job else 404)
        else:self.send_error(404)
    def do_POST(self):
        try:
            n=int(self.headers.get('Content-Length',0))
            if n>5000:raise ValueError('Request too large')
            data=json.loads(self.rfile.read(n))
            if self.path=='/api/discover':
                city=str(data.get('city','')).strip();interest=str(data.get('interest','heritage')).strip()
                if not city or len(city)>100 or interest not in ('heritage','nature','art museums'):raise ValueError('Enter a city and choose an interest.')
                self.send_json(discover(city,interest))
            elif self.path=='/api/plan':
                search=SEARCHES.get(data.get('search_id'))
                weight=float(data.get('distance_weight',.15))
                if not search or not 0 <= weight <= 2: raise ValueError('Discover places first and choose a valid distance weight.')
                plan=optimize(search['places'],3,weight)
                if plan.get('error'):raise ValueError(plan['error'])
                search['plan']=plan;self.send_json(plan)
            elif self.path=='/api/postcard':
                search=SEARCHES.get(data.get('search_id'));place=next((p for p in search['places'] if p['place_id']==data.get('place_id')),None) if search else None
                if not place:raise ValueError('Choose a place from a live search first.')
                search=dict(search)
                if not data.get('trail'): search.pop('plan',None)
                jid=str(uuid.uuid4());JOBS[jid]={'id':jid,'status':'Queued','place':place,'city':search['city'],'fetched_at':search['fetched_at'],'model':'fal-ai/flux/schnell','art_label':'AI illustration; not a photograph of the location','plan':search.get('plan'),'serpapi_search_id':search.get('search_id')}
                threading.Thread(target=generate,args=(jid,search,place),daemon=True).start();self.send_json(JOBS[jid],202)
            else:self.send_error(404)
        except ValueError as e:self.send_json({'error':str(e)},400)
        except Exception:self.send_json({'error':'Live discovery failed. Check your SerpApi key, credits or connectivity.'},502)
    def log_message(self,*args):pass
if __name__=='__main__':
    load_env();print('Postcard Scout: http://127.0.0.1:8766',flush=True);ThreadingHTTPServer(('127.0.0.1',8766),Handler).serve_forever()
