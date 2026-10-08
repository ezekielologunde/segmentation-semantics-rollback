import pathlib,json,hashlib
R=pathlib.Path(__file__).resolve().parents[1];n=0
for d in sorted((R/'analysis').glob('feasibility-iptables-*-v*')):
 for f,h in json.loads((d/'manifest.json').read_text()).items():
  assert hashlib.sha256((d/f).read_bytes()).hexdigest()==h;n+=1
 for f,h in json.loads((d/'freeze.json').read_text())['sha256'].items():
  assert hashlib.sha256((R/f).read_bytes()).hexdigest()==h;n+=1
checks=0
for d in (R/'analysis').glob('feasibility-iptables-*-v2'):
 r=json.loads((d/'results.json').read_text());assert json.loads((d/'receipt.json').read_text())['exit_code']==0
 for k,v in dict(preflight=True,initial_fresh=False,allow_session=True,restored_session=True,restored_fresh=False,revocation_positive=True,revoked_session=False,revoked_fresh=False).items():assert r[k]['success']==v;checks+=1
 assert r['rules_identical'] and r['rules']['initial']==r['rules']['restored'];checks+=1
out=dict(status='passed',hash_checks=n,corrected_outcome_checks=checks,traces=2,scope='Known behavior, not novelty or CNI replication');(R/'analysis/verification-v0.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
