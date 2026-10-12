"""Exact bounded multi-objective itinerary optimizer over live geocoded candidates."""
import itertools, math

def distance(a,b):
    a,b=a['gps_coordinates'],b['gps_coordinates']
    lat1,lat2=map(math.radians,(a['latitude'],b['latitude']))
    dlat=lat2-lat1;dlon=math.radians(b['longitude']-a['longitude'])
    return 6371*2*math.asin(min(1,math.sqrt(math.sin(dlat/2)**2+math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2)))

def score(p):
    # Shrink low-review scores toward a neutral 4-star prior of 50 reviews.
    n=max(0,int(p.get('reviews') or 0));r=float(p.get('rating') or 4)
    return (n*r+50*4)/(n+50)

def optimize(places,stops=3,distance_weight=.15):
    candidates=[p for p in places if p.get('gps_coordinates') and all(k in p['gps_coordinates'] for k in ('latitude','longitude'))][:6]
    k=min(stops,len(candidates))
    if k<2:return {'error':'At least two geocoded places are needed.'}
    matrix=[[distance(a,b) for b in candidates] for a in candidates]
    plans=[];evaluated=0
    # For each subset, evaluate every permutation: the true shortest open path.
    for subset in itertools.combinations(range(len(candidates)),k):
        routes=[]
        for order in itertools.permutations(subset):
            km=sum(matrix[a][b] for a,b in zip(order,order[1:]));routes.append((km,order));evaluated+=1
        km,order=min(routes);quality=sum(score(candidates[i]) for i in subset)/k
        plans.append({'indices':order,'distance_km':km,'quality':quality,'objective':quality-distance_weight*km})
    best=max(plans,key=lambda p:p['objective'])
    frontier=[p for p in plans if not any(other['quality']>=p['quality'] and other['distance_km']<=p['distance_km'] and (other['quality']>p['quality'] or other['distance_km']<p['distance_km']) for other in plans)]
    ordered=[candidates[i] for i in best['indices']]
    baseline=sorted(best['indices']);base_km=sum(matrix[a][b] for a,b in zip(baseline,baseline[1:]))
    legs=[{'from':a['title'],'to':b['title'],'straight_line_km':round(distance(a,b),3)} for a,b in zip(ordered,ordered[1:])]
    return {'stops':ordered,'legs':legs,'distance_km':round(best['distance_km'],3),'search_order_distance_km':round(base_km,3),'distance_saved_percent':round(100*(base_km-best['distance_km'])/base_km,1) if base_km else 0,'bayesian_quality':round(best['quality'],4),'objective':round(best['objective'],4),'objective_definition':f'mean Bayesian rating - {distance_weight} × straight-line kilometers','distance_weight':distance_weight,'prior':{'rating':4,'reviews':50},'candidates':len(candidates),'routes_evaluated':evaluated,'subsets_evaluated':len(plans),'pareto_plans':[{'places':[candidates[i]['title'] for i in p['indices']],'distance_km':round(p['distance_km'],3),'quality':round(p['quality'],4)} for p in sorted(frontier,key=lambda p:p['distance_km'])],'distance_matrix_km':[[round(x,3) for x in row] for row in matrix],'matrix_labels':[p['title'] for p in candidates],'method':'Exhaustive subset + permutation search; exact optimum for this candidate set and objective.','limitation':'Distances are geodesic, not road routes or travel-time estimates. Hours are shown but not modeled as constraints.'}
