import sys,unittest,copy
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
from repo_motion import signature3,descriptors
from test_analysis import trajectory
from vendor.pp import observable_machine as O
class RepoMotionTests(unittest.TestCase):
 def test_line_exponential(self):
  v=np.array([1.,2.,-1.,.5]);p=np.array([np.zeros(4),v*.3,v]);s=signature3(p);self.assertTrue(np.allclose(s[:4],v));self.assertTrue(np.allclose(s[4:20],np.outer(v,v).ravel()/2));self.assertTrue(np.allclose(s[20:],np.einsum('i,j,k->ijk',v,v,v).ravel()/6))
 def test_signature_translation(self):
  p=np.array([[0,0],[1,0],[1,1]],float);self.assertTrue(np.allclose(signature3(p),signature3(p+17)))
 def test_order_sensitive(self):
  a=signature3(np.array([[0,0],[1,0],[1,1]],float));b=signature3(np.array([[0,0],[0,1],[1,1]],float));self.assertFalse(np.allclose(a,b));self.assertTrue(np.allclose(a[:2],b[:2]))
 def test_exact_source_quotient(self):
  _,p=descriptors(trajectory());self.assertTrue(O.verify_machine(p))
  for k in range(20):self.assertEqual(O.power_outputs(p,k),O.power_outputs(p,k,original=True))
 def test_tamper_rejection(self):
  _,p=descriptors(trajectory());p=copy.deepcopy(p);p['seed_minimal']=tuple(x+1 for x in p['seed_minimal']);self.assertFalse(O.verify_machine(p))
 def test_feature_isometry(self):
  g=trajectory();f,_=descriptors(g);h=g.copy();xy=h[['x','y']].to_numpy();h[['x','y']]=xy@np.array([[0,-1],[1,0]])+30;k,_=descriptors(h)
  for name in f:self.assertAlmostEqual(f[name],k[name],places=6,msg=name)
if __name__=='__main__':unittest.main()

class ProspectBoundaryTests(unittest.TestCase):
 def fixture(self):
  import pandas as pd,repo_predict as R
  rows=[]
  for i in range(6):
   row={c:float(i+1) for c in R.PHYS+R.NUM};row.update({c:'A' for c in R.CAT});row.update(nfl_id=i,motion__D__f0=float(i),motion__D__f1=float(i*i));rows.append(row)
  return pd.DataFrame(rows)
 def test_physical_fit_ignores_repeated_routes(self):
  import pandas as pd,repo_predict as R
  x=self.fixture();a=R.ProspectEncoder(('motion__D__f0','motion__D__f1'),2).fit(x);b=R.ProspectEncoder(('motion__D__f0','motion__D__f1'),2).fit(pd.concat([x,x.iloc[[0]*30]],ignore_index=True));self.assertTrue(np.allclose(a.phys.named_steps['impute'].statistics_,b.phys.named_steps['impute'].statistics_));self.assertTrue(np.allclose(a.mi.statistics_,b.mi.statistics_));self.assertTrue(np.allclose(a.pca.components_,b.pca.components_))
 def test_test_player_cannot_change_fit(self):
  import repo_predict as R
  x=self.fixture();e=R.ProspectEncoder(('motion__D__f0','motion__D__f1'),2).fit(x);before=e.pca.components_.copy();z=x.iloc[[0]].copy();z['nfl_id']=999;z['motion__D__f0']=1e12;e.transform(z);self.assertNotIn(999,e.fit_player_ids_);self.assertTrue(np.array_equal(before,e.pca.components_))
 def test_route_drill_readout(self):
  import pandas as pd
  from route_matched import RouteEncoder
  cols=('motion__DAGGER_ROUTE_LEFT__f','motion__SPEED_OUT_ROUTE_LEFT__f','motion__SLANT_ROUTE_LEFT__f','motion__CURL_ROUTE_RIGHT__f','motion__COMEBACK_ROUTE_RIGHT__f');d=pd.DataFrame([{c:float(i+1) for i,c in enumerate(cols)}]);e=RouteEncoder(cols,1);self.assertEqual(e.vector(d,'IN')[0,0],1);self.assertEqual(e.vector(d,'OUT')[0,0],2);self.assertEqual(e.vector(d,'HITCH')[0,0],4.5)
