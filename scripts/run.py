#!/usr/bin/env python3
"""Execute public contracts against private production code; emit sanitized case outcomes only."""
import argparse, hashlib, json, pathlib, subprocess, tempfile, xml.etree.ElementTree as ET
p = argparse.ArgumentParser()
p.add_argument('--app', type=pathlib.Path, required=True)
p.add_argument('--phase', choices=['baseline', 'after', 'final'], required=True)
p.add_argument('--production-base', required=True)
a = p.parse_args()
root = pathlib.Path(__file__).resolve().parents[1]
app = a.app.resolve()
files = sorted((root / 'contracts').rglob('*.kt'))
hash_input = b''.join(f.relative_to(root).as_posix().encode() + b'\0' + f.read_bytes() for f in files)
with tempfile.TemporaryDirectory(prefix='gps-contract-') as temp:
    init = pathlib.Path(temp) / 'contracts.gradle'
    init.write_text('allprojects { plugins.withId("com.android.application") { android.sourceSets.getByName("test").java.srcDir(' + json.dumps(str(root / 'contracts/kotlin')) + ') } }\n')
    xml_dir = app / 'app/build/test-results/testDebugUnitTest'
    for f in xml_dir.glob('TEST-*.xml'): f.unlink()
    log = root / '.private-' / (a.phase + '.log')
    log.parent.mkdir(exist_ok=True)
    with log.open('w') as output:
        proc = subprocess.run([str(app / 'gradlew'), '-I', str(init), 'testDebugUnitTest', '--tests', 'com.drivemate.app.nav.GpsAcceptanceTest', '--rerun-tasks', '--no-daemon', '--max-workers=3'], cwd=app, stdout=output, stderr=subprocess.STDOUT)
    cases = []
    for f in xml_dir.glob('TEST-*GpsAcceptanceTest.xml'):
        for c in ET.parse(f).getroot().findall('testcase'):
            cases.append({'case': c.get('name'), 'passed': c.find('failure') is None and c.find('error') is None and c.find('skipped') is None})
    data = {'phase': a.phase, 'production_base': a.production_base, 'contract_sha256': hashlib.sha256(hash_input).hexdigest(), 'cases': cases, 'total': len(cases), 'passed': sum(c['passed'] for c in cases), 'gradle_exit': proc.returncode, 'scope': 'synthetic JVM production-domain contracts; Android UI and physical GPS unverified'}
    (root / 'results' / (a.phase + '.json')).write_text(json.dumps(data, indent=2) + '\n')
    print(json.dumps(data))
    raise SystemExit(0 if cases and proc.returncode == 0 else 1)
