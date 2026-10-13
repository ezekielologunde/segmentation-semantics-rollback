"""Bounded allow/deny/restore check in the explicitly named research cluster."""
import json
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
K = ['kubectl', '--kubeconfig', str(ROOT / '.local-review/research-kubeconfig')]
NS = 'research-enforcement-gate'
IMAGE = 'python:3.11-alpine@sha256:d9368b3a5ac59afea7b5d4f2e2aea0941dbf9fdee9c369c5bec00b98244bc929'
events = []

def run(args, obj=None):
    p = subprocess.run(K + args, input=json.dumps(obj) if obj else None,
                       capture_output=True, text=True, timeout=100)
    events.append({'command': args, 'exit': p.returncode, 'stdout': p.stdout, 'stderr': p.stderr})
    return p

def apply(obj):
    p = run(['apply', '-f', '-'], obj)
    assert p.returncode == 0, p.stderr

def probe():
    return run(['exec', '-n', NS, 'client', '--', 'python', '-c',
                f'import urllib.request; print(urllib.request.urlopen("http://{ip}:8080",timeout=2).status)']).returncode == 0

try:
    context = run(['config', 'current-context']).stdout.strip()
    assert context == 'kind-segmentation-attribution', context
    apply({'apiVersion':'v1','kind':'Namespace','metadata':{'name':NS}})
    for name, command in [('server',['python','-m','http.server','8080']),
                          ('client',['python','-c','import time; time.sleep(3600)'])]:
        apply({'apiVersion':'v1','kind':'Pod','metadata':{'name':name,'namespace':NS,'labels':{'role':name}},
               'spec':{'containers':[{'name':name,'image':IMAGE,'command':command,
                   'resources':{'requests':{'cpu':'10m','memory':'24Mi'},'limits':{'cpu':'250m','memory':'128Mi'}}}]}})
    assert run(['wait','-n',NS,'--for=condition=Ready','pod','--all','--timeout=90s']).returncode == 0
    ip = run(['get','pod','server','-n',NS,'-o','jsonpath={.status.podIP}']).stdout
    allowed = probe()
    apply({'apiVersion':'networking.k8s.io/v1','kind':'NetworkPolicy',
           'metadata':{'name':'deny-server','namespace':NS},
           'spec':{'podSelector':{'matchLabels':{'role':'server'}},'policyTypes':['Ingress'],'ingress':[]}})
    time.sleep(3)
    denied = not probe()
    assert run(['delete','networkpolicy','deny-server','-n',NS]).returncode == 0
    time.sleep(3)
    restored = probe()
    result = {'allowed_before':allowed,'blocked_after_deny':denied,'allowed_after_delete':restored,
              'passed': allowed and denied and restored,
              'scope':'Single-node local reachability gate only. Not a latency or attribution experiment.'}
finally:
    (ROOT/'analysis/cluster-enforcement-events.json').write_text(json.dumps(events,indent=2),encoding='utf-8')
if 'result' in globals():
    (ROOT/'analysis/cluster-enforcement-result.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2))
    assert result['passed']
