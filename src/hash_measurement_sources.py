"""Record byte hashes of the pinned primary sources without redistributing them."""
import hashlib
import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
review = json.loads((ROOT / "analysis/measurement-contribution-review.json").read_text())
urls = [s["url"] for s in review["sources"] if s["url"].startswith("https://raw.githubusercontent.com/")]
urls += [
    "https://raw.githubusercontent.com/kube-burner/kube-burner/28f74ab467b212cb77e53881c7d34973f5b99a8d/pkg/measurements/netpol_latency.go",
    "https://raw.githubusercontent.com/cilium/cilium/eb6a6617d9ce9b33299c488c8672c359eaadfc37/pkg/endpointmanager/manager.go",
]
records = []
for url in urls:
    with urllib.request.urlopen(url, timeout=30) as response:
        data = response.read()
    records.append({"url": url, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
(ROOT / "analysis/measurement-source-hashes.json").write_text(
    json.dumps({"date": "2026-10-13", "sources": records}, indent=2) + "\n")
print(f"Hashed {len(records)} pinned sources")
