"""Compare the expanded frozen suite without replacing the original baseline evidence."""
import json
from pathlib import Path
from reporting import validate
r=Path(__file__).resolve().parents[1]
m=json.loads((r/'contracts/manifest.json').read_text())
expected=[c['class']+'#'+n for c in m['final'] for n in c['tests']]
b,a,f=[json.loads((r/'results/reliability'/(p+'.json')).read_text()) for p in ('before','after','final')]
if len({x['executed_contract_sha256'] for x in (b,a,f)})!=1: raise SystemExit('Expanded runtime contracts changed between runs')
for x in (b,a,f):
 ids=[c['id'] for c in x['cases']]
 if len(ids)!=len(set(ids)) or set(ids)!=set(expected): raise SystemExit('Non-comparable runtime identities')
for x in (a,f):
 if validate(x['cases'],expected,x['gradle_exit']) or not x['valid']: raise SystemExit('Candidate verification failed')
before={c['id']:c['passed'] for c in b['cases']}
after={c['id']:c['passed'] for c in a['cases']}
d={'before':{'passed':b['passed'],'total':b['total']},'after':{'passed':a['passed'],'total':a['total']},'final':{'passed':f['passed'],'total':f['total']},'improved_cases':[n for n in expected if not before[n] and after[n]],'regressions':[n for n in expected if before[n] and not after[n]],'same_runtime_contracts':True,'scope':'automated_only'}
(r/'results/reliability/comparison.json').write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(d))
