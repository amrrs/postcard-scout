import unittest,itertools
from planner import optimize,distance,score

def place(name,lon,rating=4.5,reviews=100):
 return {'title':name,'gps_coordinates':{'latitude':26,'longitude':lon},'rating':rating,'reviews':reviews}
class OptimizerTests(unittest.TestCase):
 def test_exact_optimum_matches_independent_bruteforce(self):
  points=[place('A',75),place('B',75.03),place('C',75.01,4.8),place('D',75.02,4.9),place('Far',76,5,2)]
  result=optimize(points,3,.15)
  best=max(sum(score(points[i]) for i in order)/3-.15*sum(distance(points[a],points[b]) for a,b in zip(order,order[1:])) for order in itertools.permutations(range(5),3))
  self.assertAlmostEqual(result['objective'],best,places=4)
  self.assertEqual(result['routes_evaluated'],60)
  self.assertLessEqual(result['distance_km'],result['search_order_distance_km']+.001)
 def test_review_shrinkage_and_distance(self):
  self.assertLess(score(place('tiny',75,5,1)),score(place('trusted',75,4.6,1000)))
  self.assertEqual(distance(place('A',75),place('B',75)),0)
  self.assertAlmostEqual(distance(place('A',75),place('B',76)),distance(place('B',76),place('A',75)))
 def test_missing_geocodes_and_frontier(self):
  self.assertIn('error',optimize([{'title':'Unknown'}]))
  r=optimize([place('A',75),place('B',75.02),place('C',75.04),place('D',75.06,4.9)],3)
  self.assertTrue(r['pareto_plans'])
  self.assertEqual(len(r['distance_matrix_km']),4)
if __name__=='__main__':unittest.main()
