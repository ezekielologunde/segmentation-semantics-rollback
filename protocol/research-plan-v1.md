# Current research plan: rollback evidence and session contracts

This narrows the historical research-plan.md after initial literature screening. Status: feasibility established; novelty unresolved.

RQ1: Under a declared contract, when do identical restored rules and passing fresh-connection tests fail to establish the required outcome for sessions created during a temporary permission?
RQ2: What minimal additional observations distinguish permitted grandfathering from a required revocation violation?
RQ3: Do these observations add coverage beyond existing conformance and stateful verification tools on actual pinned implementations?

H1 is only a feasibility expectation, not novel: a stateful rule snapshot can be restored while a previously admitted connection still transfers data. H2 remains prospective: a history-aware evidence set reduces incorrectly reported restoration under an explicit immediate-revocation contract versus rules-only and fresh-only baselines. H3, additional coverage beyond established stateful baselines, is the critical unresolved contribution gate.

Use public implementation source and redistributable generated traces with pinned container image IDs, versions, license references, run commands, policy histories, expected contract, packet/application observations and hashes. No private enterprise dataset or participant study is needed for the initial work. Local Docker is sufficient; HPC is unnecessary until a measured scale requirement exists.

Start with a deterministic non-LLM baseline. Do not add an LLM translator simply to label the project AI research. The original proposal's model comparison is deferred until a meaningful translation question survives prior-art comparison.

Prospective design after novelty gate: at most two pinned CNI products, fresh isolated clusters, fresh/established flows, temporary allow/deny transitions, successful/partial deployment and rollback, explicit grandfathering and immediate-revocation contracts. Label unsupported semantics separately from defects. Preserve observation timestamps and control sessions. Do not equate iptables-legacy and iptables-nft with two independent CNI products. No production network experiments are authorized or needed.

Publication gate: actual implementation evidence, traceable contracts, applicable stateful baseline comparisons, reproducible counterexamples or informative negative results, and honest limitations. The current pilot alone is not a paper contribution.
