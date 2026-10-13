"""Run unique-name and corrected-binary controls in the existing isolated cluster."""
import json
import shutil
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
NODE='segmentation-attribution-control-plane'
K=['kubectl','--kubeconfig',str(ROOT/'.local-review/research-kubeconfig')]
assert subprocess.check_output(K+['config','current-context'],text=True).strip()=='kind-segmentation-attribution'
images=json.loads((ROOT/'analysis/cluster-attribution/image-identities.json').read_text(encoding='utf-8'))
for case in ['unique','fixed']:
    build=ROOT/'.local-review'/f'cluster-{case}'
    shutil.copytree(ROOT/'protocol/cluster-attribution',build,dirs_exist_ok=True)
    pod=build/'templates/pod.yml'
    text=pod.read_text()
    for tag,digest in images.items():
        text=text.replace(tag,digest)
    pod.write_text(text)
    if case=='unique':
        policy=build/'templates/ingress-np.yml'
        policy.write_text(policy.read_text().replace('name: allow','name: allow-{{.Iteration}}'))
    remote=f'/root/cluster-{case}'
    subprocess.run(['docker','cp',str(build),f'{NODE}:{remote}'],check=True)
    binary='/root/kube-burner-fixed' if case=='fixed' else '/root/kube-burner'
    p=subprocess.run(['docker','exec','-w',remote,NODE,binary,'init','--kubeconfig','/etc/kubernetes/admin.conf',
        '--config','config.yml','--timeout','3m','--log-level','debug'],capture_output=True,text=True,encoding='utf-8',timeout=240)
    dest=ROOT/'analysis/cluster-attribution'/case
    dest.mkdir(exist_ok=True)
    (dest/'console.log').write_text(p.stdout+p.stderr,encoding='utf-8')
    subprocess.run(['docker','cp',f'{NODE}:{remote}/.',str(dest)],check=True)
    policies=subprocess.check_output(K+['get','networkpolicies','-A','-o','json'],text=True)
    (dest/'policies.json').write_text(policies)
    (dest/'exit.json').write_text(json.dumps({'exit':p.returncode}))
    print(case,p.returncode,flush=True)
    if p.returncode:
        raise RuntimeError(p.stderr[-2000:])
