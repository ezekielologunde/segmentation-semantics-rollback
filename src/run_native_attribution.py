"""Compare pinned native measurement methods before/after a namespace-key patch."""
import difflib
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKOUT = ROOT / ".local-review/kube-burner-native"
PIN = "28f74ab467b212cb77e53881c7d34973f5b99a8d"
IMAGE = "golang@sha256:8bee1901f1e530bfb4a7850aa7a479d17ae3a18beb6e09064ed54cfd245b7191"
SOURCE = "pkg/measurements/netpol_latency.go"

def main():
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=CHECKOUT, text=True).strip()
    assert head == PIN
    original = subprocess.check_output(["git", "show", f"HEAD:{SOURCE}"], cwd=CHECKOUT).decode()
    disk = (CHECKOUT / SOURCE).read_text(encoding="utf-8")
    assert disk == original, "Checkout source changed; refusing to overwrite"
    shutil.copyfile(ROOT / "src/native_attribution_test.go", CHECKOUT / "pkg/measurements/research_attribution_test.go")
    patched = original.replace("npCreationTime[netpol.Name]", 'npCreationTime[netpol.Namespace+"/"+netpol.Name]')
    anchor = '\t\t\t\t\tlocalPods := addPodsByLabel'
    assert patched.count(anchor) == 1
    patched = patched.replace(anchor, '\t\t\t\t\tpolicyKey := namespace+"/"+networkPolicy.Name\n' + anchor)
    for old, new in [
        ('[]string{networkPolicy.Name}', '[]string{policyKey}'),
        ('slices.Contains(addrReuse[ar], networkPolicy.Name)', 'slices.Contains(addrReuse[ar], policyKey)'),
        ('append(addrReuse[ar], networkPolicy.Name)', 'append(addrReuse[ar], policyKey)'),
        ('Netpol:    networkPolicy.Name', 'Netpol:    policyKey'),
    ]:
        assert patched.count(old) == 1, old
        patched = patched.replace(old, new)
    diff = ''.join(difflib.unified_diff(original.splitlines(True), patched.splitlines(True), fromfile='a/'+SOURCE, tofile='b/'+SOURCE))
    (ROOT / "analysis/native-namespace-fix.patch").write_text(diff, encoding="utf-8")
    results = {}
    try:
        for name, source in [("baseline", original), ("fixed", patched)]:
            (CHECKOUT / SOURCE).write_text(source, encoding="utf-8")
            cmd = ["docker", "run", "--rm", "--network", "none", "--memory", "4g", "--cpus", "2",
                   "-e", f"RESEARCH_FIXED={int(name=='fixed')}",
                   "--mount", f"type=bind,source={CHECKOUT},target=/work",
                   "--mount", "type=volume,source=segmentation-go-modcache,target=/go/pkg/mod",
                   "--mount", "type=volume,source=segmentation-go-buildcache,target=/root/.cache/go-build",
                   "-w", "/work", IMAGE, "go", "test", "-p", "2", "./pkg/measurements", "-run", "^TestResearchNative", "-v", "-count=1"]
            run = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", timeout=600)
            log = run.stdout + run.stderr
            (ROOT / f"analysis/native-attribution-{name}.log").write_text(log, encoding="utf-8")
            rows = [json.loads(line.split("RESEARCH_RESULT ", 1)[1]) for line in log.splitlines() if "RESEARCH_RESULT " in line]
            mapping_passed = "--- PASS: TestResearchNativeMapping" in log
            results[name] = {"returncode": run.returncode, "rows": rows, "mapping_test_passed": mapping_passed, "source_sha256": hashlib.sha256(source.encode()).hexdigest()}
            print(name, run.returncode, len(rows), flush=True)
            if run.returncode != 0:
                raise RuntimeError(log[-3000:])
    finally:
        (CHECKOUT / SOURCE).write_text(original, encoding="utf-8")
        (ROOT / "analysis/native-attribution-results.json").write_text(json.dumps({"pin":PIN,"image":IMAGE,"scope":"Native measurement package with synthetic objects and loopback proxy, not a cluster deployment", "results":results}, indent=2)+"\n")
    assert all(len(r["rows"]) == 4 for r in results.values())
    assert all(r["mapping_test_passed"] for r in results.values())
    bad = [r for r in results["baseline"]["rows"] if r["threshold_failed"] != r["ground_truth_threshold_failed"]]
    assert len(bad) == 1 and bad[0]["case"] == "same_names_slow"
    assert all(r["threshold_failed"] == r["ground_truth_threshold_failed"] for r in results["fixed"]["rows"])
    print("Native false-pass reproduction and namespace-key control validated")

if __name__ == "__main__":
    main()


