"""Extract the actual upstream aggregation loop into a standalone Go fixture."""
import hashlib
import json
import urllib.request
from pathlib import Path

root = Path(__file__).resolve().parents[1]
pin = "28f74ab467b212cb77e53881c7d34973f5b99a8d"
url = f"https://raw.githubusercontent.com/kube-burner/kube-burner/{pin}/pkg/measurements/netpol_latency.go"
raw = urllib.request.urlopen(url, timeout=30).read()
source = raw.decode()
start = "\tfor pod, results := range clusterResults {"
end = "\n\tresp.Body.Close()"
assert source.count(start) == 1
a = source.index(start)
b = source.index(end, a)
block = source[a:b]
out = root / ".local-review" / "attribution"
out.mkdir(parents=True, exist_ok=True)
prefix = '''// Extracted block: Copyright The Kube-burner Authors, Apache-2.0.
// Source provenance and license stored alongside this generated file.
package main
import ("encoding/json"; "fmt"; "os"; "time")
type observation struct {Address string; Timestamp time.Time}
type logger struct{}
func (logger) Warnf(format string, args ...interface{}) {}
var log logger
func aggregate(clusterResults map[string][]observation, addrReuse map[string][]string, npCreationTime map[string]time.Time) map[string][]float64 {
npResults := make(map[string][]float64)
'''
suffix = '''
return npResults
}
func stamp(ms int64) time.Time { return time.Unix(0, ms*1000000) }
func main() {
 rows := []map[string]interface{}{}
 for _, c := range []struct{name string; keys []string; created map[string]time.Time; observed int64}{
 {"disjoint_control", []string{"A"}, map[string]time.Time{"A":stamp(100)}, 300},
 {"overlap_positive", []string{"A","B"}, map[string]time.Time{"A":stamp(100),"B":stamp(200)}, 300},
 {"overlap_later_creation", []string{"A","B"}, map[string]time.Time{"A":stamp(100),"B":stamp(400)}, 300},
 } {
 result := aggregate(map[string][]observation{"client":{{"server",stamp(c.observed)}}}, map[string][]string{"client:server":c.keys}, c.created)
 rows = append(rows,map[string]interface{}{"case":c.name,"reported_ms":result})
 }
 // Mirror the inspected creation callback's map assignment using unqualified names.
 creation := map[string]time.Time{}
 creation["allow"] = stamp(100) // ns-one/allow
 creation["allow"] = stamp(900) // ns-two/allow
 result := aggregate(map[string][]observation{"client-one":{{"server-one",stamp(200)}}},map[string][]string{"client-one:server-one":{"allow"}},creation)
 rows=append(rows,map[string]interface{}{"case":"same_name_different_namespaces","reported_ms":result,"expected_ns_one_ms":100})
 json.NewEncoder(os.Stdout).Encode(rows)
}
'''
(out / "main.go").write_text(prefix + block + suffix, encoding="utf-8")
license_url = f"https://raw.githubusercontent.com/kube-burner/kube-burner/{pin}/LICENSE"
license_bytes = urllib.request.urlopen(license_url, timeout=30).read()
(out / "LICENSE").write_bytes(license_bytes)
manifest = {"source":url,"source_sha256":hashlib.sha256(raw).hexdigest(),
            "extracted_block_sha256":hashlib.sha256(block.encode()).hexdigest(),
            "scope":"Actual aggregation loop; synthetic fixtures; surrounding types and logging stubbed; not full Kube-burner execution"}
(root / "analysis/attribution-source-manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
print(out)
