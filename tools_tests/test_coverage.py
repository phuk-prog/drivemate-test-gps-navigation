"""Coverage gates cannot pass by omitting a preference or inventing a test ID."""
import pathlib,sys,unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'scripts'))
from coverage_check import assess
from wiring import uncomment

class CoverageTest(unittest.TestCase):
    def fixture(self):
        prefs={k:{'requirement':k,'runtime':['C#t'],'wiring':['g']} for k in ('01.01','01.02','01.03','01.04')}
        return prefs,{'valid':True,'cases':[{'id':'C#t','passed':True}]},{'checks':[{'id':'g','passed':True,'disconnection_detected':True}]},{'final':[{'class':'C','tests':['t']}]}
    def test_all_four_preferences_need_real_ids(self): self.assertEqual(4,len(assess(*self.fixture())))
    def test_missing_preference_is_rejected(self):
        p,r,w,m=self.fixture();del p['01.03']
        with self.assertRaises(ValueError):assess(p,r,w,m)
    def test_invented_test_identity_is_rejected(self):
        p,r,w,m=self.fixture();p['01.04']['runtime']=['invented']
        with self.assertRaises(ValueError):assess(p,r,w,m)
    def test_disconnected_wiring_is_rejected(self):
        p,r,w,m=self.fixture();w['checks'][0]['passed']=False
        with self.assertRaises(ValueError):assess(p,r,w,m)
    def test_comments_cannot_satisfy_a_wiring_guard(self): self.assertNotIn('fakeBinding',uncomment('// fakeBinding\n/* fakeBinding */ actual'))
    def test_quoted_labels_remain_available_for_checks(self): self.assertIn('"Position uncertain"',uncomment('"Position uncertain" // comment'))
