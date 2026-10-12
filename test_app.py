import unittest
from unittest.mock import patch
import app
class PipelineTests(unittest.TestCase):
    def test_live_fields_and_provenance(self):
        raw={'local_results':[{'title':'Museum','place_id':'abc','rating':4.4,'address':'City','description':'Gallery'}]}
        with patch.dict(app.os.environ,{'SERPAPI_API_KEY':'test'}),patch.object(app,'request_json',return_value=raw):
            r=app.discover('Jaipur','heritage')
        self.assertEqual(r['searches_used'],1)
        self.assertEqual(r['places'][0]['rating'],4.4)
        self.assertIn('query_place_id=abc',r['places'][0]['maps_url'])
        self.assertIn('not a documentary photograph',app.make_prompt(r,r['places'][0]))
    def test_queue_result_and_safety_failure(self):
        search={'city':'Jaipur'};place={'title':'Museum','description':'Gallery'}
        handle={'request_id':'abc','status_url':'https://queue.fal.run/status','response_url':'https://queue.fal.run/result'}
        for blocked in (False,True):
            app.JOBS['test']={'status':'Queued'}
            with patch.dict(app.os.environ,{'FAL_KEY':'test'}),patch.object(app,'request_json',side_effect=[handle,{'status':'COMPLETED'},{'images':[{'url':'https://example.com/image.jpg'}],'has_nsfw_concepts':[blocked],'seed':12}]):
                app.generate('test',search,place)
            self.assertEqual(app.JOBS['test']['status'],'Failed' if blocked else 'Complete')
            if not blocked:self.assertEqual(app.JOBS['test']['request_id'],'abc')
if __name__=='__main__':unittest.main()
