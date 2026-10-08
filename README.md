# Segmentation semantics and rollback

**Status: Local feasibility pilot complete; novelty unresolved.** Two corrected isolated Linux traces distinguish restored rules from ongoing-session behavior. This reproduces known conntrack semantics, not a new vulnerability or CNI comparison. [Results](analysis/feasibility-report-v0.md), [literature gate](analysis/literature-gate-v0.md), and [current plan](protocol/research-plan-v1.md).

[Research protocol and prior-art leads](protocol/research-plan.md). This plan comes from the October 4, 2026 independent research portfolio. Its literature assessment must be refreshed before implementation and submission.

## Research identity and publication route

Author: **Ezekiel Ologunde**. Affiliation: **Independent Researcher**, with no institutional affiliation. Author email: ologunde@bu.edu. No corresponding-author designation. Intended route: a suitable ACM journal, selected after assessing the completed contribution. No journal has accepted this work and no publisher metadata or DOI is assigned.

## Repository workflow

Keep research questions and hypotheses in `protocol/`; put code in `src/`, tests in `tests/`, and analyses in `analysis/`. Store redistributable datasets with provenance in `data/`, including source URL, retrieval date, version, license, SHA-256, schema, and role in the study. For restricted or large data, publish an acquisition script and manifest instead of copying files. Never commit credentials, private participant records, or copyrighted downloaded papers.

Freeze each experimental plan and code revision before collection. Retain failed and excluded runs with reasons. Publish analysis and result artifacts as work progresses. Keep manuscript drafts in `paper/`, clearly versioned; deposit the author-permitted final paper after journal-policy review. A planned experiment is not a result, and public code is not peer-reviewed acceptance.

Original work is intentionally unlicensed pending an author decision. Preserve applicable third-party notices. No dataset or final paper is claimed to exist merely because its directory is present.
