"""Infrastructure self-tests use a fake process; they do not verify app behaviour."""
import contextlib, io, json, pathlib, runpy, shutil, subprocess, sys, tempfile, unittest
from unittest.mock import patch
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'scripts'))
from reporting import validate

class ResultValidationTest(unittest.TestCase):
    def check(self, cases, expected=('a','b'), exit_code=0): return validate(cases, list(expected), exit_code)
    def test_exact_passing_results_pass(self): self.assertFalse(self.check([{'id':x,'passed':True} for x in ('a','b')]))
    def test_duplicate_cannot_replace_missing_case(self): self.assertTrue(self.check([{'id':'a','passed':True}]*2))
    def test_substituted_case_is_rejected(self): self.assertTrue(self.check([{'id':x,'passed':True} for x in ('a','wrong')]))
    def test_failed_case_with_successful_process_is_rejected(self): self.assertTrue(self.check([{'id':'a','passed':False}],('a',)))
    def test_missing_execution_is_rejected(self): self.assertTrue(self.check([]))
    def test_process_failure_is_rejected_even_if_cases_pass(self): self.assertTrue(self.check([{'id':'a','passed':True}],('a',),1))
    def test_empty_manifest_cannot_pass(self): self.assertTrue(self.check([],()))
    def test_invalid_xml_cannot_pass(self): self.assertTrue(validate([{'id':'a','passed':True}],['a'],0,['malformed JUnit XML']))
    def test_duplicate_expected_identity_cannot_pass(self): self.assertTrue(self.check([{'id':'a','passed':True}],('a','a')))

class RunnerTest(unittest.TestCase):
    def execute(self, mode):
        with tempfile.TemporaryDirectory() as temp:
            root = pathlib.Path(temp) / 'contracts'; (root/'scripts').mkdir(parents=True)
            source = pathlib.Path(__file__).resolve().parents[1]
            for n in ('run.py','reporting.py'): shutil.copyfile(source/'scripts'/n, root/'scripts'/n)
            contract = root/'contracts/kotlin/com/drivemate/app/nav/GpsAcceptanceTest.kt'
            contract.parent.mkdir(parents=True); contract.write_text('// Synthetic runner fixture')
            c={'file':contract.relative_to(root).as_posix(),'class':'com.drivemate.app.nav.GpsAcceptanceTest','tests':['synthetic']}
            (root/'contracts/manifest.json').write_text(json.dumps({'baseline':[c]}))
            app=pathlib.Path(temp)/'private-app'; app.mkdir()
            real_check_output=subprocess.check_output
            def fake_process(*args,**kwargs):
                xml=app/'app/build/test-results/testDebugUnitTest/TEST-GpsAcceptanceTest.xml'; xml.parent.mkdir(parents=True)
                case='<testcase classname="com.drivemate.app.nav.GpsAcceptanceTest" name="synthetic">'+('<skipped/>' if mode=='skipped' else '')+'</testcase>'
                xml.write_text('<testsuite>'+ (case*2 if mode=='duplicate' else '' if mode=='missing' else case)+'</testsuite>')
                return subprocess.CompletedProcess([],0)
            argv=[str(root/'scripts/run.py'),'--app',str(app),'--phase','baseline','--production-base','synthetic-tool-fixture']
            with patch.object(sys,'argv',argv), patch('subprocess.run',side_effect=fake_process), patch('subprocess.check_output',return_value='synthetic\n'), contextlib.redirect_stdout(io.StringIO()):
                with self.assertRaises(SystemExit) as result: runpy.run_path(str(root/'scripts/run.py'),run_name='__main__')
            return result.exception.code, json.loads((root/'results/baseline.json').read_text())
    def test_fresh_checkout_creates_results_directory(self): self.assertEqual(0,self.execute('pass')[0])
    def test_missing_results_fail(self): self.assertEqual(1,self.execute('missing')[0])
    def test_skipped_tests_fail_even_with_successful_process(self): self.assertEqual(1,self.execute('skipped')[0])
    def test_duplicates_fail_in_real_report_parser(self): self.assertEqual(1,self.execute('duplicate')[0])

if __name__=='__main__': unittest.main()
