# Literature and contribution gate v0

Date: 2026-10-08. Targeted primary-source screen, not a systematic review. No novelty clearance.

| Prior source | Established overlap | Consequence |
|---|---|---|
| Kubernetes NetworkPolicy documentation, https://kubernetes.io/docs/concepts/services-networking/network-policies/#networkpolicys-impact-on-existing-connections | Existing-connection handling following policy changes is plugin-defined | Different session outcomes are not automatically CNI defects. An explicit operational contract is required. |
| Rollback-Recovery for Middleboxes, SIGCOMM 2015, author PDF https://cs.nyu.edu/~apanda/assets/papers/ftmb-final.pdf | Restoring stateful middlebox execution with logging and output-commit semantics | Stateful rollback is not a new problem. Distinguish failure recovery from restoring security policy after a temporary admission. |
| NetSMC, NSDI 2020 primary paper https://www.usenix.org/system/files/nsdi20-paper-yuan.pdf | Verification of stateful network properties, including modeled history and dynamic rules | Do not claim existing verification considers only static rules. Full relation/capability comparison needed. |
| Compiling Stateful Network Properties for Runtime Verification, https://arxiv.org/abs/1607.03385 | Runtime verification of stateful network properties | Adding history-aware probes is not itself a novel runtime-verification principle. |
| Cilium and VDM: Towards Formal Analysis of Cilium Policies, https://arxiv.org/abs/2410.12009 | Formal analysis of Cilium policies | Product-specific formal analysis already exists; adding a parser or policy translation is insufficient. |
| Calico flow-state design, https://github.com/projectcalico/calico/blob/master/felix/design/bpf-conntrack-flowstate.md | Explicit connection-state handling and previously established flows | Use pinned implementation semantics, not an invented uniform expectation. Current branch is background, not an experimental pin. |

The historical CoSynth URL https://www.cs.ucla.edu/~todd/research/hotnets23.pdf again failed retrieval. Its full-text capabilities remain unverified; do not claim it lacks temporal analysis based on failed access.

## Decision

Reject broad claims of novelty for stateful rollback, consistent updates, or history-aware verification. The local feasibility probe reproduces expected Linux conntrack behavior and establishes no vulnerability or new discovery.

Conditional next question: for a documented revocation-versus-grandfathering contract, can a small, reproducible evidence set distinguish rule restoration from session-contract restoration across pinned CNI implementations and rollback histories? Evaluate against an ordinary state-aware test suite and the strongest applicable prior tools. A generic fresh-versus-existing connection comparison is not sufficient novelty.

Before substantial experiments: complete full-text review of closest verification/recovery work; locate and pin public conformance tests; map what they already cover; identify one concrete uncovered contract or failure mode. If coverage is complete, close the novel-method route instead of relabeling expected behavior as a discovery.
