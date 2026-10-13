# Segmentation semantics and rollback

**Deployed reproduction completed:** [eight-check assessment](analysis/cluster-attribution/assessment.json) and [reproduction instructions](protocol/cluster-attribution/REPRODUCE.txt). In an isolated single-node Kubernetes cluster with policy enforcement, two same-name policies produced one metric and a negative minimum latency (-203 ms). A unique-name control produced two metrics. The namespace-key candidate also produced two correctly identified, nonnegative metrics. All eight attribution checks and three allow/deny/restore checks passed. This is a concrete measurement defect, not established journal novelty. One run per condition does not estimate prevalence or performance; the live run did not reproduce the synthetic threshold false pass.

**Native validation result:** [assessment](analysis/native-validation-assessment.json), [results](analysis/native-attribution-results.json), and [candidate patch](analysis/native-namespace-fix.patch). With synthetic events passed through the actual measurement package, a true 6000 ms delay incorrectly passed a 5000 ms maximum threshold after policy identities collided. Namespace-aware keys restore the correct failure. Four attribution cases and a native mapping test pass on each implementation. This is not a live-cluster result or a journal novelty claim.

To reproduce the earlier native tests, clone upstream tag `v2.5.1` into `.local-review/kube-burner-native`, verify commit `28f74ab467b212cb77e53881c7d34973f5b99a8d`, and populate the Go module/build caches used by `src/run_native_attribution.py` through a dependency-enabled initial build. The runner then uses a pinned Go container with networking disabled, saves both logs and restores the source. `python src/run_workload_overlap.py` renders the actual workload template for the separate static census. The prepared native fixture must be copied to `pkg/measurements/research_attribution_test.go` for the initial build. The deployed reproduction above extends these tests.

The native fake-client fixture requires the two test-only dependencies recorded in `analysis/native-test-dependencies.patch`. Use `go test -mod=mod -p 2 ./pkg/measurements -run '^$'` for the dependency-enabled preparation in the same pinned container and cache volumes. No tests execute in that preparation step. The final research comparison runs without network access. Failed offline dependency setup logs are retained separately from successful test logs.

[Policy attribution audit](analysis/policy-attribution-assessment.json): an extracted upstream Go aggregation loop reproduces a same-name namespace collision and shared-flow timing ambiguity on synthetic fixtures. Four checks pass. This is a source-level engineering result; default workload failure, live cluster impact and research novelty are not established. Reproduce with `python src/run_attribution_fixture.py` after pulling the pinned Go image named in that script.

Latest evidence: [measurement contribution review](analysis/measurement-contribution-review.json). Upstream Kubernetes already measures policy enforcement through traffic and pod churn. A 12-trial local command calibration passed five checks and confirmed response-completion confounding, but this is known command behavior, not research novelty. The bounded next candidate is measurement validity under incomplete observations; full-method comparison remains required.

Latest review: [vendor and monitoring baseline coverage](analysis/baseline-coverage-v2.md), [explicit rollback contract](protocol/rollback-contract-v2.md), and [pinned source manifest](analysis/vendor-source-review-v2.json). Persistent-session tests already exist, and the basic revocation predicate uses established temporal operators. Generic monitor novelty is not supported. Further experimental expansion remains on hold pending a distinct evidence-related gap.

**Status: Literature-first review in progress; experimental expansion on hold; novelty unresolved.** The [updated contribution gate](analysis/literature-gate-v1.md) compares primary papers and pinned conformance source. Broad claims about temporal verification and LLM-assisted configuration are already covered. Two corrected isolated Linux traces reproduce known conntrack semantics, not a new vulnerability or CNI comparison. [Pilot results](analysis/feasibility-report-v0.md), [historical literature gate](analysis/literature-gate-v0.md), and [provisional plan](protocol/research-plan-v1.md).

[Research protocol and prior-art leads](protocol/research-plan.md). This plan comes from the October 4, 2026 independent research portfolio. Its literature assessment must be refreshed before implementation and submission.

## Research identity and publication route

Author: **Ezekiel Ologunde**. Affiliation: **Independent Researcher**, with no institutional affiliation. Author email: ologunde@bu.edu. No corresponding-author designation. Intended route: a suitable ACM journal, selected after assessing the completed contribution. No journal has accepted this work and no publisher metadata or DOI is assigned.

## Repository workflow

Keep research questions and hypotheses in `protocol/`; put code in `src/`, tests in `tests/`, and analyses in `analysis/`. Store redistributable datasets with provenance in `data/`, including source URL, retrieval date, version, license, SHA-256, schema, and role in the study. For restricted or large data, publish an acquisition script and manifest instead of copying files. Never commit credentials, private participant records, or copyrighted downloaded papers.

Freeze each experimental plan and code revision before collection. Retain failed and excluded runs with reasons. Publish analysis and result artifacts as work progresses. Keep manuscript drafts in `paper/`, clearly versioned; deposit the author-permitted final paper after journal-policy review. A planned experiment is not a result, and public code is not peer-reviewed acceptance.

Original work is intentionally unlicensed pending an author decision. Preserve applicable third-party notices. No dataset or final paper is claimed to exist merely because its directory is present.
