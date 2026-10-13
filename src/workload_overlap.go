// Render the pinned upstream template and count shared probe coverage.
// This is a static workload census, not cluster execution or a new algorithm.
package main
import("bytes";"encoding/json";"fmt";"os";"text/template";"github.com/Masterminds/sprig/v3";networkingv1 "k8s.io/api/networking/v1";"sigs.k8s.io/yaml")
func main(){
 raw,err:=os.ReadFile("examples/workloads/network-policy/templates/ingress-np.yml");if err!=nil{panic(err)}
 tmpl,err:=template.New("policy").Funcs(sprig.TxtFuncMap()).Parse(string(raw));if err!=nil{panic(err)}
 rows:=[]map[string]any{}
 for _,c:=range []struct{name string;namespaces,replicas,pods,local,peerNS,peerPods int}{
 {"upstream_example",9,1,2,1,2,2},
 {"controlled_overlap_variant",9,20,2,1,2,2},
 }{
  flowPolicies:=map[string]map[string]bool{};policyFlows:=map[string]map[string]bool{}
  for i:=0;i<c.namespaces;i++{for r:=1;r<=c.replicas;r++{
   v:=map[string]any{"Iteration":i,"Replica":r,"namespaces":c.namespaces,"pods_per_namespace":c.pods,"netpols_per_namespace":c.replicas,"local_pods":c.local,"pod_selectors":1,"single_ports":1,"port_ranges":1,"peer_namespaces":c.peerNS,"peer_pods":c.peerPods,"cidr_rules":1}
   var b bytes.Buffer;if err:=tmpl.Execute(&b,v);err!=nil{panic(err)}
   var p networkingv1.NetworkPolicy;if err:=yaml.Unmarshal(b.Bytes(),&p);err!=nil{panic(err)}
   ns:=fmt.Sprintf("network-policy-perf-%d",i);key:=ns+"/"+p.Name;policyFlows[key]=map[string]bool{}
   for _,ingress:=range p.Spec.Ingress{for _,from:=range ingress.From{
    for _,remoteNS:=range from.NamespaceSelector.MatchExpressions[0].Values{for _,remotePod:=range from.PodSelector.MatchExpressions[0].Values{for _,localPod:=range p.Spec.PodSelector.MatchExpressions[0].Values{
     if remoteNS==ns&&remotePod==localPod{continue}
     flow:=remoteNS+"/"+remotePod+"->"+ns+"/"+localPod+":8080"
     if flowPolicies[flow]==nil{flowPolicies[flow]=map[string]bool{}}
     flowPolicies[flow][key]=true;policyFlows[key][flow]=true
    }}}
   }}
  }}
  shared:=0;maxMultiplicity:=0;for _,p:=range flowPolicies{if len(p)>1{shared++};if len(p)>maxMultiplicity{maxMultiplicity=len(p)}}
  unique:=0;for _,flows:=range policyFlows{for f:=range flows{if len(flowPolicies[f])==1{unique++;break}}}
  rows=append(rows,map[string]any{"profile":c.name,"policies":len(policyFlows),"distinct_probe_flows":len(flowPolicies),"shared_probe_flows":shared,"policies_with_unique_probe":unique,"max_policies_per_flow":maxMultiplicity})
 }
 json.NewEncoder(os.Stdout).Encode(rows)
}
