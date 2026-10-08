# Local rollback feasibility protocol v0

Written before collecting packet outcomes. This is a known-behavior feasibility probe, not a novelty experiment or Kubernetes/CNI reproduction.

Question: can an isolated local test distinguish restored rule text, fresh-connection denial, and continued traffic on a connection admitted during an intermediate allow policy?

Use a Docker network-none container with NET_ADMIN only, no host network, no host namespace mounts or published ports. Scope all OUTPUT rules to loopback TCP port 45001. Other workloads and the host firewall are outside scope. Fresh container per backend. Initial policy P0 accepts ESTABLISHED packets then rejects other packets to the test port. P1 accepts packets to the test port. Restore exactly P0 while keeping the P1-admitted socket open. Then apply an explicit revocation policy that rejects before ESTABLISHED. This policy is deliberately different; do not call it equivalent rollback.

Expected controls: fresh denied at initial P0; fresh and ongoing traffic accepted under P1; after P0 restoration fresh denied but P1 session may survive; explicit revocation rejects both. Compare iptables-legacy and iptables-nft as two Linux interfaces, not independent CNI products. Save all commands, timestamps, rules, versions and results. A driver or environment failure is not packet rejection. No population estimates or timing-performance claims. The result can validate the harness and demonstrate known conntrack semantics only.
