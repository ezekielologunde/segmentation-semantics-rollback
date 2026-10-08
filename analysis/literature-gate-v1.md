# Literature-first contribution gate, 2026-10-08

**Decision: HOLD experimental expansion. No novelty established.** This is a targeted closest-work review, not a systematic or exhaustive review. Existing pilot traces remain feasibility evidence only. The review rejects broad contributions before spending more compute.

## Review method and limits

Searched for stateful network verification, policy rollback, existing connections, temporal policy updates, CoSynth follow-ups, and public CNI conformance tests. Searches included 2024-2026 work and older foundations. Read the primary full-text sections identified below, rather than treating abstracts or search snippets as evidence. Proofs and published experimental results were not independently reproduced. Dates refer to publications where verified, not search-engine crawl dates. Findings about missing coverage are restricted to inspected sections or functions.

Include primary papers, official specifications, and pinned implementation evidence. Treat issue discussions as evidence of an acknowledged question, not as a normative specification or verified product defect. Exclude generic blogs, marketing, unrelated patent search hits and unverified quantitative claims from the gap argument.

## Closest-work evidence matrix

| Work and inspected location | Contribution, method and evaluation | Explicit limits or scope | Effect on our candidate |
|---|---|---|---|
| [Yuan et al., NetSMC, NSDI 2020](https://www.usenix.org/system/files/nsdi20-paper-yuan.pdf), sections 4-5, 7-8 and Appendix D | Symbolic verification of stateful network functions and temporal policies. Models state tables; evaluates synthetic/real topology models and CloudLab configurations including pfSense and HAProxy. Reports better scalability than comparator tools. | Section 8 identifies missed packet-interleaving violations, restricted operations and temporal language, and no direct failure model. Appendix D compares expressiveness with VMN. | Reject generic history-aware verification as novelty. Its stated restrictions do not establish that our sequential rollback trace is beyond its capabilities. An explicit encoding comparison is required. |
| [Mondal et al., What do LLMs need to Synthesize Correct Router Configurations?, HotNets 2023](https://conferences.sigcomm.org/hotnets/2023/papers/hotnets23_mondal.pdf), sections 2-4 | CoSynth vision combines model-generated configurations with syntax and semantic feedback. Evaluated Cisco-to-Juniper translation and BGP policies; section 3 describes manually feeding generated prompts to GPT-4. | Preliminary evaluation; incomplete specifications and human intervention remain relevant. Do not misdescribe this as an independently reproduced, fully automated benchmark. | Reject generic LLM plus verifier as a new contribution. Its evaluated router tasks do not resolve session rollback, but that absence alone is not a research gap. |
| [Liu et al., CEGS: Configuration Example Generalizing Synthesizer, NSDI 2025](https://www.usenix.org/system/files/nsdi25-liu-jianmin.pdf), introduction limitations and sections 4.1-4.4 | Combines GNN example retrieval/generalization, LLM template generation and formal synthesis. Evaluates routing intents and topologies; validates using Batfish. Section 4.3 uses an author reconstruction of CoSynth because code was unavailable. | Depends on documentation examples, formal synthesizer expressiveness and correct intent formalization; reported formalization accuracy is dataset-specific. | Stronger follow-up invalidates a weak comparison against unassisted prompting. Its limitations are candidate leads, not proof of unsolved problems. |
| [Nelson et al., Compiling Stateful Network Properties for Runtime Verification, 2016, arXiv v2](https://arxiv.org/pdf/1607.03385v2), introduction and section 5 | Varanus compiles temporal network queries into switch execution. Modified Open vSwitch and Mininet evaluation examines connection-rate and retained-state overhead. | Prototype omits some OpenFlow features, including general multicast egress observation; workload and retained query state affect overhead. | Reject simply adding temporal runtime checks as novelty. Compare a concrete monitoring contract and observation assumptions before claiming additional coverage. |
| [Cilium and VDM: Towards Formal Analysis of Cilium Policies, 2024, v1](https://arxiv.org/html/2410.12009v1), sections 4-5 and 7 | VDM-SL models policy-controlled communication for an industrial system; scenario execution distinguishes permitted and prohibited transfers. This is model analysis, not our live CNI experiment. | Authors propose deployment-pipeline integration, richer protocols, broader policy definitions and combinatorial testing as future work. | Formal Cilium policy analysis already exists. A live rollback conformance artifact might differ, but extensions and subsequent work must be checked first. |
| [Weintraub et al., Exploiting Temporal Vulnerabilities for Unauthorized Access in Intent-Based Networking, CCS 2024](https://web.mit.edu/ha22286/www/papers/CCS24.pdf), sections 5.3-5.4 and 6.1 | Spotlight screens flow-rule updates for temporary unintended connectivity. Evaluates fat-tree, Stanford and Cisco topologies with generated host-to-host intents. Detection timing excludes topology preprocessing. | Inspected algorithm assumes static topology and atomic updates per switch; examines intermediate combinations of old/new flow rules. | Temporal update safety is established. Our possible distinction concerns retained sessions after rollback convergence, not merely intermediate forwarding states. This is an inference requiring further comparison, not a proven exclusion from all extensions. |
| [Galletta, Enforcement of In-Kernel Stateful Security Policies via eBPF, 2026 preprint](https://arxiv.org/pdf/2609.13930), abstract and section 10 only | BPFence presents temporal monitors compiled to eBPF. Author reports seven case studies and performance benchmarks. Evaluation details and proofs have not yet been reviewed here. | Section 10 distinguishes observable from synchronously enforceable events and fixed-capacity state. Distributed enforcement and orchestration integration are future directions. | Recent adjacent work must be included before proposing a new history-aware kernel monitor. This row is preliminary screening, not completed capability review. |

## Public implementation evidence

The [Kubernetes NetworkPolicy documentation](https://kubernetes.io/docs/concepts/services-networking/network-policies/#networkpolicys-impact-on-existing-connections) treats effects on established connections as implementation-defined. [network-policy-api issue 305](https://github.com/kubernetes-sigs/network-policy-api/issues/305), opened July 11, 2025, explicitly discusses connection-based versus packet-based semantics and the wish to revoke established traffic after policy changes. The issue was displayed as open when reviewed. These are reasons to define the contract carefully, not grounds to label an implementation insecure.

Inspected `kubernetes-sigs/network-policy-api` at commit `c4572b0f2ba75fe770adea4a207ea2e02b43d538`:

Retrieval URLs and SHA-256 hashes of the UTF-8 source responses are recorded in [the source manifest](conformance-source-review-v1.json). Third-party source code and paper PDFs are not redistributed in this update.

- [TCP ingress tests](https://github.com/kubernetes-sigs/network-policy-api/blob/c4572b0f2ba75fe770adea4a207ea2e02b43d538/conformance/tests/admin-network-policy-standard-ingress-tcp-rules.go) change rule order and check connectivity. Therefore, claiming the tests never exercise updates would be false.
- [Integration tests](https://github.com/kubernetes-sigs/network-policy-api/blob/c4572b0f2ba75fe770adea4a207ea2e02b43d538/conformance/tests/admin-network-policy-standard-integration.go) patch actions and delete a policy to check precedence.
- [Helper, lines 66-119](https://github.com/kubernetes-sigs/network-policy-api/blob/c4572b0f2ba75fe770adea4a207ea2e02b43d538/conformance/utils/kubernetes/helper.go#L66) repeatedly invokes `/agnhost connect`, waits for expected connectivity, then checks again. This function does not retain an application socket across policy mutation. Its negative expectation specifically checks timeout, unlike our pilot's reject/reset outcomes.

This is a three-file inspection, not an audit of the entire repository, Kubernetes e2e suite, Cyclonus, Cilium or Calico tests. The snapshot uses ClusterNetworkPolicy types despite historical filenames. Do not equate it with ordinary NetworkPolicy conformance. A missing retained-socket check in this helper establishes only that helper's scope, not publication novelty.

## Candidate question and falsification gate

**Candidate RQ, not an approved experimental claim:** Can a contract-aware rollback conformance method distinguish permissible session continuation from a missed revocation after acknowledged enforcement convergence, across pinned implementations, more reliably than existing stateful monitors and vendor tests?

Potential contribution must be more than an extra connection probe: a precisely specified contract, justified observations, and demonstrated additional diagnostic coverage or a rigorous boundary on what can be inferred. Changing datasets, CNIs, industry labels or adding an LLM is insufficient by itself.

Draft hypothesis: given a fixed revocation deadline and explicit connection-versus-packet contract, a monitor using policy-generation acknowledgements, session identity and application-level liveness can reduce false restoration verdicts on independently labelled traces without misclassifying permitted grandfathering. No numerical improvement is predicted from current evidence. Competing explanation: existing temporal monitors can express exactly this contract, making the implementation only an application of known techniques.

Required baseline classes: exact rule/configuration comparison; fresh-connection checks; an existing temporal monitor with the SAME observable inputs and contract; strongest applicable pinned vendor/session tests. The first two are diagnostic controls, not sufficient novelty comparators. Compare methods with equal evidence access, then ablate evidence separately.

Proposed public evidence, subject to the gate: licensed public policy/test fixtures plus generated, versioned, isolated testbed traces. Public IDS datasets do not contain the required policy acknowledgements and session lifecycle ground truth. Record commit/image digests, policy timeline, connection identifiers, independent delivery observations, time uncertainty, failures and exclusions. Existing v2 traces cannot serve as a held-out evaluation after informing the design.

Support requires a reproducible difference beyond the strongest existing method, with an explanation of why it arises. Reject the novelty claim if the same specification in a standard monitor achieves equivalent coverage, if the only difference is more input data, or if apparent violations disappear under the documented contract. Unknown convergence or ambiguous observations must yield inconclusive, not secure or violated.

## Current gate ledger

| Obligation | Status |
|---|---|
| Separate known stateful behavior from a contribution | Passed for broad candidate rejection |
| Identify contemporary counterexamples to broad originality claims | Passed: CEGS, Spotlight, explicit Kubernetes discussion |
| Inspect all strongest test/tool baselines | Incomplete: vendor suites, Cyclonus, general monitors and follow-ups remain |
| Establish a distinct capability not already covered | Not established |
| Freeze fair evaluation and independent ground truth | Draft only |
| Authorize substantive experiment expansion through this gate | HOLD |

Next research work is source and specification analysis: inspect pinned vendor tests and Cyclonus; formalize the same rollback obligation in an existing monitor; follow citations on temporal update verification and revocation. If that exercise covers the proposed method, close this as a replication/conformance artifact rather than forcing a novelty claim. No new experiment, dataset download, cluster deployment or manuscript result was produced during this review.
