import tempfile,unittest
import numpy as np
import test_stress_transfer as fixtures
import stress_transfer as T
class CacheContentTests(unittest.TestCase):
    def test_changed_training_labels_cannot_reuse_reference(self):
        d=fixtures.StressTransferTests().rows();a=d[d.nfl_id<10].copy();b=d[d.nfl_id>=10].copy()
        with tempfile.TemporaryDirectory() as folder:
            a.pressure_event=0.;p=T.context_predict(a,b,'pressure_event',cache=folder)
            a.pressure_event=1.;q=T.context_predict(a,b,'pressure_event',cache=folder)
            np.testing.assert_array_equal(p,np.zeros(len(b)));np.testing.assert_array_equal(q,np.ones(len(b)))
    def test_held_out_labels_do_not_change_cache_identity(self):
        from pathlib import Path
        d=fixtures.StressTransferTests().rows();a=d[d.nfl_id<10].copy();b=d[d.nfl_id>=10].copy()
        with tempfile.TemporaryDirectory() as folder:
            p=T.context_predict(a,b,'pressure_event',cache=folder);b.pressure_event+=50
            q=T.context_predict(a,b,'pressure_event',cache=folder)
            self.assertEqual(len(list(Path(folder).glob('*.pkl'))),1);np.testing.assert_array_equal(p,q)
