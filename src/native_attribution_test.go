// Research regression fixture. Synthetic Kubernetes objects and proxy responses.
package measurements

import (
 "encoding/json"
 "net/http"
 "net/http/httptest"
 "os"
 "path/filepath"
 "strings"
 "testing"
 "time"

 "github.com/kube-burner/kube-burner/v2/pkg/config"
 "github.com/kube-burner/kube-burner/v2/pkg/measurements/types"
 "k8s.io/apimachinery/pkg/apis/meta/v1/unstructured"
 corev1 "k8s.io/api/core/v1"
 metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
 "k8s.io/client-go/kubernetes/fake"

)

func TestResearchNativeAttribution(t *testing.T) {
 fixed := os.Getenv("RESEARCH_FIXED") == "1"
 for _, tc := range []struct{name string; same bool; firstDelay int64}{
  {"unique_names_slow",false,6000}, {"same_names_slow",true,6000},
  {"unique_names_fast",false,1000}, {"same_names_fast",true,1000},
 } {
 t.Run(tc.name,func(t *testing.T){
  npCreationTime=map[string]time.Time{}; npResults=map[string][]float64{}
  clusterResults=map[string][]connTest{}; addrReuse=map[string][]string{}
  n:= &netpolLatency{BaseMeasurement:BaseMeasurement{JobConfig:&config.Job{Name:"research"},
   Config:types.Measurement{LatencyThresholds:[]types.LatencyThreshold{{ConditionType:"Ready",Metric:"Max",Threshold:5000*time.Millisecond}}}}}
  names:=[]string{"allow-one","allow-two"}; if tc.same {names=[]string{"allow","allow"}}
  namespaces:=[]string{"ns-one","ns-two"}
  for i,ms:=range []int64{1000,9000} {
   n.handleCreateNetpol(&unstructured.Unstructured{Object:map[string]interface{}{"apiVersion":"networking.k8s.io/v1","kind":"NetworkPolicy","metadata":map[string]interface{}{"name":names[i],"namespace":namespaces[i],"creationTimestamp":time.Unix(0,ms*int64(time.Millisecond)).UTC().Format(time.RFC3339)}}})
   key:=names[i]; if fixed {key=namespaces[i]+"/"+key}
   if i==0 {addrReuse["client-one:server-one"]=[]string{key}} else {addrReuse["client-two:server-two"]=[]string{key}}
  }
  payload:=map[string][]connTest{
   "client-one":{{Address:"server-one",Timestamp:time.Unix(0,(1000+tc.firstDelay)*int64(time.Millisecond))}},
   "client-two":{{Address:"server-two",Timestamp:time.Unix(0,10000*int64(time.Millisecond))}},
  }
  server:=httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter,r *http.Request){
   switch r.URL.Path {case "/stop":w.WriteHeader(200);case "/checkStopStatus":json.NewEncoder(w).Encode(ProxyResponse{Result:true});case "/results":json.NewEncoder(w).Encode(payload);default:http.NotFound(w,r)}
  })); defer server.Close()
  proxyEndpoint=strings.TrimPrefix(server.URL,"http://")
  n.processResults()
  err:=n.StopMeasurement(n.normalizeMetrics,n.getLatency)
  expectedFail:=tc.firstDelay>5000 && (!tc.same || fixed)
  if (err!=nil)!=expectedFail {t.Fatalf("threshold error %v expected fail %v",err,expectedFail)}
  count:=0; n.Metrics.Range(func(k,v any)bool{count++;return true})
  expectedCount:=2; if tc.same&&!fixed {expectedCount=1}
  if count!=expectedCount {t.Fatalf("metric count %d expected %d",count,expectedCount)}
  row:=map[string]any{"case":tc.name,"fixed":fixed,"reported_ms":npResults,"metric_count":count,"threshold_failed":err!=nil,"ground_truth_threshold_failed":tc.firstDelay>5000}
  b,_:=json.Marshal(row);t.Log("RESEARCH_RESULT "+string(b))
 })
 }
}

func TestResearchNativeMapping(t *testing.T) {
 fixed:=os.Getenv("RESEARCH_FIXED")=="1"
 connections=map[string][]connection{}; addrReuse=map[string][]string{};nsPodAddresses=map[string]map[string][]string{}
 pod:=func(ns,ip string)*corev1.Pod{return &corev1.Pod{ObjectMeta:metav1.ObjectMeta{Name:"pod",Namespace:ns},Status:corev1.PodStatus{PodIP:ip}}}
 client:=fake.NewSimpleClientset(pod("ns-0","10.0.0.1"),pod("ns-1","10.0.0.2"),pod("peer","10.0.0.3"))
 template:=`apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow
spec:
  podSelector: {}
  policyTypes: [Ingress]
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          kubernetes.io/metadata.name: peer
      podSelector: {}
    ports:
    - protocol: TCP
      port: 8080
`
 path:=filepath.Join(t.TempDir(),"policy.yml");if err:=os.WriteFile(path,[]byte(template),0600);err!=nil{t.Fatal(err)}
 n:=&netpolLatency{BaseMeasurement:BaseMeasurement{ClientSet:client,JobConfig:&config.Job{Name:"mapping",Namespace:"ns",JobIterations:2,IterationsPerNamespace:1,Objects:[]config.Object{{ObjectTemplate:path,Replicas:1}}}}}
 n.prepareConnections()
 for _,pair:=range []struct{address,ns string}{{"10.0.0.1","ns-0"},{"10.0.0.2","ns-1"}}{
  expected:="allow";if fixed{expected=pair.ns+"/allow"}
  got:=addrReuse["10.0.0.3:"+pair.address]
  if len(got)!=1||got[0]!=expected{t.Fatalf("unexpected mapping %v expected %s",got,expected)}
 }
 if len(connections["10.0.0.3"])!=2{t.Fatal("missing probe connections")}
 t.Logf("Native prepareConnections verified, namespace-aware=%v",fixed)
}


