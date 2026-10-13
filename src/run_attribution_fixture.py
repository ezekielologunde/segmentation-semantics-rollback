"""Run extracted upstream aggregation against synthetic inputs without networking."""
import json
import subprocess
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
subprocess.run([sys.executable, str(root / "src/prepare_attribution_fixture.py")], check=True)
image = "golang@sha256:8bee1901f1e530bfb4a7850aa7a479d17ae3a18beb6e09064ed54cfd245b7191"
cmd = ["docker", "run", "--rm", "--network", "none", "--memory", "512m", "--cpus", "2",
       "--mount", f"type=bind,source={root / '.local-review/attribution'},target=/work,readonly",
       "-w", "/work", image, "go", "run", "main.go"]
run = subprocess.run(cmd, capture_output=True, text=True, timeout=120, check=True)
rows = json.loads(run.stdout)
cases = {r["case"]: r for r in rows}
checks = {
    "disjoint_control_200ms": cases["disjoint_control"]["reported_ms"] == {"A": [200]},
    "shared_observation_two_policies": cases["overlap_positive"]["reported_ms"] == {"A": [200], "B": [100]},
    "negative_interval_retained": cases["overlap_later_creation"]["reported_ms"]["B"] == [-100],
    "namespace_collision": cases["same_name_different_namespaces"]["reported_ms"]["allow"] == [-700]
}
result = {"date": "2026-10-13", "image": image, "checks": checks, "cases": rows,
          "scope": "Unmodified extracted Go aggregation loop. Creation-map assignments mirrored. Synthetic timestamps; no cluster or full application run.",
          "novelty": "Unresolved; reproducible engineering mechanism, not established scholarly contribution."}
(root / "analysis/policy-attribution-results.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(checks))
assert all(checks.values())
