"""Independently compare emitted policy metrics with API object identities."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'analysis/cluster-attribution'
results={}
for case in ['baseline','unique','fixed']:
    directory=BASE/case
    rows=json.loads((directory/'kube-burner/netpolLatencyMeasurement-network-policy-perf.json').read_text(encoding='utf-8-sig'))
    policies=json.loads((directory/'policies.json').read_text(encoding='utf-8-sig'))['items']
    objects=[p for p in policies if p['metadata'].get('labels',{}).get('kube-burner.io/job')=='network-policy-perf']
    ids=sorted(p['metadata']['namespace']+'/'+p['metadata']['name'] for p in objects)
    names=sorted(r['netpol'] for r in rows)
    results[case]={'policy_identities':ids,'metric_names':names,'policy_count':len(objects),
                   'metric_count':len(rows),'metrics':rows}
checks={
    'baseline_two_objects':results['baseline']['policy_count']==2,
    'baseline_one_metric':results['baseline']['metric_count']==1,
    'baseline_negative_minimum':any(r['minReady']<0 for r in results['baseline']['metrics']),
    'unique_two_objects_and_metrics':results['unique']['policy_count']==results['unique']['metric_count']==2,
    'unique_matching_names':results['unique']['metric_names']==sorted(x.split('/')[1] for x in results['unique']['policy_identities']),
    'fixed_two_objects_and_metrics':results['fixed']['policy_count']==results['fixed']['metric_count']==2,
    'fixed_matching_full_identity':results['fixed']['metric_names']==results['fixed']['policy_identities'],
    'fixed_nonnegative':all(r['minReady']>=0 and r['ready']>=0 for r in results['fixed']['metrics'])
}
out={'scope':'One deployed run per condition, correctness endpoints only, not a failure-rate estimate',
     'checks':checks,'results':results,
     'not_established':['Live false-pass threshold consequence','Cross-CNI prevalence','Novel research contribution'],
     'sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
               for case in results for p in (BASE/case).rglob('*') if p.is_file()}}
(BASE/'assessment.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps(checks,indent=2))
assert all(checks.values()), 'Observed result differs from expected reproduction; inspect evidence'
