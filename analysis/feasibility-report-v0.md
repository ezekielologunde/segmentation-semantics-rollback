# Initial local feasibility result

Two corrected v2 traces ran successfully on Linux kernel 6.6.87.2-microsoft-standard-WSL2 with iptables 1.8.10 legacy and nf_tables interfaces. Both produced the same outcomes:

| Phase | Fresh connection | Previously admitted session |
|---|---|---|
| Initial P0 | Rejected | Not applicable |
| Temporary allow P1 | Connection opened and echo confirmed | Accepted |
| Exact P0 rule restoration | Rejected | Echo continued |
| Explicit revocation | Rejected | Separately opened, confirmed-live session rejected |

The initial and restored study-chain rule strings are identical. This demonstrates the harness can distinguish rules and fresh-connectivity checks from continuing session behavior. It reproduces known stateful firewall semantics, not a new vulnerability or validated novelty. These are two interfaces to the Linux networking stack, not two independent products. One trace per interface cannot estimate reliability or timing.

The container had network none, no host network/device mounts and no published ports. NET_ADMIN and NET_RAW were limited to its disposable namespace. All rules targeted loopback TCP port 45001. Existing Docker workloads and host firewall were unchanged. No HPC execution.

Preserved history: v0 legacy lacked capability for table initialization and nft rejected an incomplete TCP-reset rule. v1 executed but removed the only conntrack match during the allow phase, so tracking continuity was uncontrolled; both sessions reset. Its later revocation probe reused an already reset socket and is not a valid independent revocation control. v2 keeps a permanent conntrack match on the scoped jump and tests revocation using a separate confirmed-live socket. The correction is a harness amendment, not a product finding.

The next scientific gate is prior-art and conformance coverage under an explicitly declared session contract. Kubernetes permits plugin-defined handling of existing connections, so survival alone does not establish a defect. See literature-gate-v0.md and protocol/research-plan-v1.md.
