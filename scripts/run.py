#!/usr/bin/env python3
"""Execute public contracts against private production code; emit sanitized case outcomes only."""
import argparse, hashlib, json, pathlib, subprocess, tempfile, shutil, xml.etree.ElementTree as ET
p = argparse.ArgumentParser()
p.add_argument('--app', type=pathlib.Path, required=True)
p.add_argument('--phase', choices=['baseline', 'after', 'final'], required=True)
p.add_argument('--production-base', required=True)
p.add_argument('--full-checks', action='store_true')
a = p.parse_args()
root = pathlib.Path(__file__).resolve().parents[1]
app = a.app.resolve()
files = [root / 'contracts/kotlin/com/drivemate/app/nav/GpsAcceptanceTest.kt']
hash_input = b''.join(f.relative_to(root).as_posix().encode() + b'\0' + f.read_bytes() for f in files)
with tempfile.TemporaryDirectory(prefix='gps-contract-') as temp:
    source_root = pathlib.Path(temp) / 'kotlin'
    selected = list(files)
    if a.phase == 'final': selected.append(root / 'contracts/kotlin/com/drivemate/app/nav/GpsIndependentTest.kt')
    for source in selected:
        target = source_root / source.relative_to(root / 'contracts/kotlin')
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    init = pathlib.Path(temp) / 'contracts.gradle'
    init.write_text('allprojects { plugins.withId("com.android.application") { android.sourceSets.getByName("test").java.srcDir(' + json.dumps(str(source_root)) + ') } }\n')
    xml_dir = app / 'app/build/test-results/testDebugUnitTest'
    for f in xml_dir.glob('TEST-*.xml'): f.unlink()
    log = root / '.private-' / (a.phase + '.log')
    log.parent.mkdir(exist_ok=True)
    test_args = ['--tests', 'com.drivemate.app.nav.GpsAcceptanceTest']
    if a.phase == 'final': test_args += ['--tests', 'com.drivemate.app.nav.GpsIndependentTest']
    if a.full_checks: test_args = ['lintDebug', 'assembleDebug']
    with log.open('w') as output:
        proc = subprocess.run([str(app / 'gradlew'), '-I', str(init), 'testDebugUnitTest', *test_args, '--no-daemon', '--max-workers=3'], cwd=app, stdout=output, stderr=subprocess.STDOUT)
    cases = []
    for f in xml_dir.glob('TEST-*Gps*Test.xml'):
        for c in ET.parse(f).getroot().findall('testcase'):
            cases.append({'suite': c.get('classname').split('.')[-1], 'case': c.get('name'), 'passed': c.find('failure') is None and c.find('error') is None and c.find('skipped') is None})
    expected = 43 if a.phase == 'final' else 19
    data = {'expected': expected, 'phase': a.phase, 'production_base': a.production_base, 'contract_sha256': hashlib.sha256(hash_input).hexdigest(), 'cases': cases, 'total': len(cases), 'passed': sum(c['passed'] for c in cases), 'gradle_exit': proc.returncode, 'scope': 'synthetic JVM production-domain contracts; Android UI and physical GPS unverified'}
    (root / 'results').mkdir(exist_ok=True)
    (root / 'results' / (a.phase + '.json')).write_text(json.dumps(data, indent=2) + '\n')
    print(json.dumps(data))
    raise SystemExit(0 if len(cases) == expected and proc.returncode == 0 else 1)
