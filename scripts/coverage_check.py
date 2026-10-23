"""Require explicit passing evidence for all four Category 1 preferences."""
import argparse,json
from pathlib import Path

def assess(preferences, report, wiring, manifest):
    all_ids={c['class']+'#'+n for c in manifest['final'] for n in c['tests']}
    passed={c['id'] for c in report['cases'] if c['passed'] is True}
    guards={x['id'] for x in wiring['checks'] if x['passed'] and x['disconnection_detected']}
    if set(preferences)!={'01.01','01.02','01.03','01.04'}: raise ValueError('Four exact preference IDs are required')
    if not report.get('valid'): raise ValueError('Runtime report failed strict validation')
    out={}
    for key,p in preferences.items():
        runtime=set(p['runtime']); static=set(p['wiring'])
        if not runtime or not static or not runtime<=all_ids or not runtime<=passed or not static<=guards:
            raise ValueError('Incomplete preference evidence: '+key)
        out[key]={'requirement':p['requirement'],'runtime_checks':len(runtime),'static_wiring_checks':len(static),'automated_checks_passed':True,'runtime_case_ids':sorted(runtime),'static_check_ids':sorted(static),'scope':'Production domain and Android sensor simulation tests plus static integration guards; no map rendering claim'}
    return out

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--report',default='results/reliability/final.json');p.add_argument('--out',default='results/reliability/coverage.json');a=p.parse_args()
    r=Path(__file__).resolve().parents[1]
    d=assess(json.loads((r/'contracts/preferences.json').read_text()),json.loads((r/a.report).read_text()),json.loads((r/'results/reliability/wiring.json').read_text()),json.loads((r/'contracts/manifest.json').read_text()))
    (r/a.out).write_text(json.dumps(d,indent=2)+'\n');print(json.dumps({k:{'runtime_checks':v['runtime_checks'],'static_wiring_checks':v['static_wiring_checks'],'passed':True} for k,v in d.items()}))
