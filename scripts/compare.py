#!/usr/bin/env python3
"""Verify an identical-contract comparison and a nonempty independent final suite."""
import json
from pathlib import Path
r = Path(__file__).resolve().parents[1] / 'results'
b, a, f = [json.loads((r / (p + '.json')).read_text()) for p in ('baseline', 'after', 'final')]
assert b['contract_sha256'] == a['contract_sha256'] == f['contract_sha256'], 'Baseline contract changed'
names = lambda d: {x['case']: x['passed'] for x in d['cases']}
bn, an, fn = map(names, (b, a, f))
assert len(bn) == len(an) == 19 and bn.keys() == an.keys(), 'Non-comparable case sets'
assert all(an[n] and fn.get(n) for n in bn), 'Unresolved acceptance case'
assert all(fn.values()) and len(fn.keys() - bn.keys()) == 24, 'Final independent checks incomplete'
data = {'baseline': {'passed': b['passed'], 'total': b['total']}, 'after': {'passed': a['passed'], 'total': a['total']}, 'final': {'passed': f['passed'], 'total': f['total']}, 'improved_cases': sorted(n for n in bn if not bn[n] and an[n]), 'independent_final_cases': 24, 'baseline_absent_feature_cases': 3, 'regressions': 0, 'device_verified': False}
(r / 'comparison.json').write_text(json.dumps(data, indent=2) + '\n')
print(json.dumps(data))
