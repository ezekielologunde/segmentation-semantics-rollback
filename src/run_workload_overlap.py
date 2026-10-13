"""Run a static census using the actual pinned Go template renderer."""
import hashlib
import json
import shutil
import subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
checkout = ROOT / ".local-review/kube-burner-native"
shutil.copyfile(ROOT / "src/workload_overlap.go", checkout / "research_workload_overlap.go")
image = "golang@sha256:8bee1901f1e530bfb4a7850aa7a479d17ae3a18beb6e09064ed54cfd245b7191"
cmd = ["docker","run","--rm","--network","none","--memory","1g","--cpus","1",
       "--mount",f"type=bind,source={checkout},target=/work,readonly",
       "--mount","type=volume,source=segmentation-go-modcache,target=/go/pkg/mod",
       "--mount","type=volume,source=segmentation-go-buildcache,target=/root/.cache/go-build",
       "-w","/work",image,"go","run","research_workload_overlap.go"]
run = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", timeout=120, check=True)
rows = json.loads(run.stdout)
template = checkout / "examples/workloads/network-policy/templates/ingress-np.yml"
result = {"scope":"Static rendered workload analysis; no cluster and no measured policy realization",
          "template_pin":"28f74ab467b212cb77e53881c7d34973f5b99a8d",
          "template_sha256_normalized_lf":hashlib.sha256(template.read_text(encoding="utf-8").encode()).hexdigest(),
          "parameters":"Upstream example uses nine namespaces and one policy per namespace. Controlled variant changes replicas and netpols_per_namespace to 20, preserving other example values.",
          "rows":rows}
(ROOT / "analysis/workload-overlap-results.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
print(json.dumps(rows))
