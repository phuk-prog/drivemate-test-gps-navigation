#!/usr/bin/env python3
"""Execute public contracts privately and publish strict, sanitized outcomes."""
import argparse, hashlib, json, pathlib, subprocess, tempfile, shutil, sys, xml.etree.ElementTree as ET
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from reporting import validate
p = argparse.ArgumentParser()
p.add_argument('--app', type=pathlib.Path, required=True)
p.add_argument('--phase', choices=['baseline', 'after', 'final'], required=True)
p.add_argument('--production-base', required=True)
p.add_argument('--full-checks', action='store_true')
p.add_argument('--report', default=None)
a = p.parse_args()
root = pathlib.Path(__file__).resolve().parents[1]
app = a.app.resolve()
manifest = json.loads((root / 'contracts/manifest.json').read_text())
selected = manifest[a.phase]
expected_ids = [c['class'] + '#' + n for c in selected for n in c['tests']]
files = [root / c['file'] for c in selected]
def digest(paths):
    return hashlib.sha256(b''.join(f.relative_to(root).as_posix().encode() + b'\0' + f.read_bytes() for f in paths)).hexdigest()
report_path = (root / (a.report or ('results/' + a.phase + '.json'))).resolve()
if not report_path.is_relative_to(root / 'results'): raise SystemExit('Reports must stay under results/')
with tempfile.TemporaryDirectory(prefix='gps-contract-') as temp:
    source_root = pathlib.Path(temp) / 'kotlin'
    for source in files:
        target = source_root / source.relative_to(root / 'contracts/kotlin')
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    init = pathlib.Path(temp) / 'contracts.gradle'
    settings = 'allprojects { plugins.withId("com.android.application") { android.sourceSets.getByName("test").java.srcDir(' + json.dumps(str(source_root)) + ')'
    if any(c['class'].endswith('GpsSensorAdapterTest') for c in selected):
        settings += '; dependencies.add("testImplementation", "org.robolectric:robolectric:4.14.1"); dependencies.add("testImplementation", "org.mockito:mockito-core:5.14.2"); android.testOptions.unitTests.all { systemProperty "robolectric.dependency.repo.url", "https://repo.maven.apache.org/maven2" }'
    init.write_text(settings + ' } }\n')
    xml_dir = app / 'app/build/test-results/testDebugUnitTest'
    for f in xml_dir.glob('TEST-*.xml'): f.unlink()
    log = root / '.private-' / (report_path.stem + '.log')
    log.parent.mkdir(exist_ok=True)
    test_args = [v for c in selected for v in ('--tests', c['class'])]
    if a.full_checks: test_args = ['lintDebug', 'assembleDebug']
    with log.open('w') as output:
        proc = subprocess.run([str(app / 'gradlew'), '-I', str(init), 'testDebugUnitTest', *test_args, '--no-daemon', '--max-workers=3'], cwd=app, stdout=output, stderr=subprocess.STDOUT)
    cases, parse_errors = [], []
    for f in sorted(xml_dir.glob('TEST-*.xml')):
        try:
            for c in ET.parse(f).getroot().findall('testcase'):
                cls = c.get('classname', '')
                if not cls.startswith('com.drivemate.app.nav.Gps') and 'Gps' not in f.name: continue
                cases.append({'id': cls + '#' + c.get('name', ''), 'suite': cls.rsplit('.',1)[-1], 'case': c.get('name'), 'passed': all(c.find(k) is None for k in ('failure','error','skipped'))})
        except ET.ParseError: parse_errors.append('malformed JUnit XML')
    errors = validate(cases, expected_ids, proc.returncode, parse_errors)
    data = {'schema': 2, 'phase': a.phase, 'production_base': a.production_base,
        'app_commit': subprocess.check_output(['git','rev-parse','HEAD'],cwd=app,text=True).strip(),
        'app_source_tree': subprocess.check_output(['git','rev-parse','HEAD:app'],cwd=app,text=True).strip(),
        'contract_sha256': digest([root / 'contracts/kotlin/com/drivemate/app/nav/GpsAcceptanceTest.kt']),
        'executed_contract_sha256': digest(files), 'manifest_sha256': hashlib.sha256((root/'contracts/manifest.json').read_bytes()).hexdigest(),
        'expected_ids': expected_ids, 'cases': cases, 'total': len(cases), 'passed': sum(c['passed'] for c in cases),
        'gradle_exit': proc.returncode, 'validation_errors': errors, 'valid': not errors,
        'scope': 'Automated production Kotlin and Android simulation contracts'}
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(data, indent=2) + '\n')
    print(json.dumps({k:v for k,v in data.items() if k not in ('cases','expected_ids')}))
    raise SystemExit(0 if not errors else 1)
