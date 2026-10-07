# Segmentation semantics and rollback

Status: Proposed. Historical candidate design, not a preregistration or proven novelty claim. Source: independent research portfolio dated 2026-10-04.

**Research question:** When a segmentation policy is translated or partially deployed, which existing application sessions and required flows change behavior despite apparently equivalent static rules?

**Existing coverage:** [CoSynth, HotNets 2023](https://www.cs.ucla.edu/~todd/research/hotnets23.pdf) uses syntax and semantic feedback for router-configuration synthesis and translation. Its publisher/author search extract was available, but full-PDF fetching failed in this pass. The exact baseline capabilities still require full-text reproduction. Generic LLM-assisted policy translation is already covered.

**Proposed difference:** Center the benchmark on stateful-session behavior, deployment ordering and rollback, rather than syntax correctness or a static routing snapshot. First verify whether existing network verification tools already cover each proposed case.

**Build and experiment:** Begin with two locally executable policy engines, not an unsupported claim to cover all enterprise products. Generate policies with overlapping rules, default actions, established-session handling and staged changes. Run separately labeled required and forbidden application traces. Compare a deterministic translator, a model-generated translator, and a verifier-assisted version using the same cases.

**Metrics:** Required-flow failures, forbidden-flow admissions, ongoing-session disruption, rollback equivalence and verification cost. Distinguish unsupported semantics from translation defects. Preserve minimal counterexamples so every failure is reproducible.

**Stop or narrow:** If the contribution is only adding a product parser, classify it as engineering. Use model-independent verification; a fluent explanation is not evidence of equivalent behavior.
