"""Runner infrastructure tests with a fake process; these do not verify app behaviour."""
import contextlib, io, json, pathlib, runpy, shutil, subprocess, sys, tempfile, unittest
from unittest.mock import patch

class RunnerTest(unittest.TestCase):
    def execute(self, with_cases):
        with tempfile.TemporaryDirectory() as temp:
            root = pathlib.Path(temp) / 'contracts'
            root.mkdir()
            script = root / 'scripts/run.py'
            script.parent.mkdir()
            shutil.copyfile(pathlib.Path(__file__).resolve().parents[1] / 'scripts/run.py', script)
            contract = root / 'contracts/kotlin/com/drivemate/app/nav/GpsAcceptanceTest.kt'
            contract.parent.mkdir(parents=True)
            contract.write_text('// Synthetic infrastructure fixture; no app execution')
            app = pathlib.Path(temp) / 'private-app'
            app.mkdir()
            def fake_process(*args, **kwargs):
                if with_cases:
                    xml = app / 'app/build/test-results/testDebugUnitTest/TEST-GpsAcceptanceTest.xml'
                    xml.parent.mkdir(parents=True)
                    xml.write_text('<testsuite>' + ''.join('<testcase classname="test.GpsAcceptanceTest" name="synthetic%s"/>' % i for i in range(19)) + '</testsuite>')
                return subprocess.CompletedProcess([], 0)
            argv = [str(script), '--app', str(app), '--phase', 'baseline', '--production-base', 'synthetic-tool-fixture']
            with patch.object(sys, 'argv', argv), patch('subprocess.run', side_effect=fake_process), contextlib.redirect_stdout(io.StringIO()):
                with self.assertRaises(SystemExit) as result:
                    runpy.run_path(str(script), run_name='__main__')
            report = json.loads((root / 'results/baseline.json').read_text())
            return result.exception.code, report
    def test_fresh_checkout_creates_missing_results_directory(self):
        code, report = self.execute(True)
        self.assertEqual(0, code)
        self.assertEqual(19, report['total'])
    def test_missing_executed_cases_cannot_pass(self):
        code, report = self.execute(False)
        self.assertEqual(1, code)
        self.assertEqual(0, report['total'])

if __name__ == '__main__': unittest.main()
