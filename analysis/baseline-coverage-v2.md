# Baseline coverage and contribution decision, 2026-10-08

**Decision: do not pursue a new temporal-monitor algorithm on the present evidence.** Continue only the narrower evidence/contract investigation. No new experimental results, CNI defects or publication novelty are established here. This supplements, rather than replaces, the historical literature-gate-v1.md.

## Pinned source review

These are development snapshots, not claims about a tested release. Source inspection does not establish runtime behavior. The [source manifest](vendor-source-review-v2.json) records retrieval hashes for six files. No third-party code was executed or redistributed.

| Source | Inspected evidence | Supported conclusion and limit |
|---|---|---|
| Cyclonus `12f646fbd7d348dedb538e4bb7f076e4d927d7a6` | [job.go lines 61-65](https://github.com/mattfenwick/cyclonus/blob/12f646fbd7d348dedb538e4bb7f076e4d927d7a6/pkg/connectivity/probe/job.go#L61) and [jobrunner.go](https://github.com/mattfenwick/cyclonus/blob/12f646fbd7d348dedb538e4bb7f076e4d927d7a6/pkg/connectivity/probe/jobrunner.go) | The non-batch runner executes each job's `/agnhost connect` command. This path checks connection establishment. The runner also has a separate batch path; its internal connection lifecycle was not audited, so do not generalize the finding to all Cyclonus execution. |
| Cilium `eb6a6617d9ce9b33299c488c8672c359eaadfc37` | [upgrade.go lines 25-40](https://github.com/cilium/cilium/blob/eb6a6617d9ce9b33299c488c8672c359eaadfc37/cilium-cli/connectivity/tests/upgrade.go#L25) and [builder](https://github.com/cilium/cilium/blob/eb6a6617d9ce9b33299c488c8672c359eaadfc37/cilium-cli/connectivity/builder/no_interrupted_connections.go) | Existing tests explicitly retain long-lived connections across upgrades and compare restart counters. Therefore persistent-session test infrastructure is not new. Upgrade continuity is not identical to security-policy revocation; this is not a claim that the entire vendor suite covers or omits our exact rollback contract. |
| Calico `290dc6ac64dd75013a58f299696e4c1639adb3db` | [bpf_test.go lines 5574-5584](https://github.com/projectcalico/calico/blob/290dc6ac64dd75013a58f299696e4c1639adb3db/felix/fv/bpf_test.go#L5574) | Starts a persistent connection, checks pongs, enables BPF mode and checks the existing connection again. Persistent application-level liveness checks already exist. This migration test does not itself establish coverage of rollback revocation. Additional selected matches inspect reset detection after backend changes; no exhaustive suite audit was performed. |

An attempted old Cilium path `test/runtime/Policies.go` returned 404 at the pinned commit. This is a retrieval failure, not evidence that policy tests do not exist. Discovery then used the repository tree and current connectivity paths. The selected Calico `policy_test.go` contains established-traffic logging checks; that alone does not establish a retained-session mutation test.

## Strong monitoring baseline

[Basin et al., MONPOLY: Monitoring Usage-control Policies](https://people.inf.ethz.ch/basin/pubs/rv11b.pdf), sections 1-3, describes monitoring a safety fragment of metric first-order temporal logic over timestamped events and identifiers. Section 3's manager example represents a relation's lifetime using start/end events and the past-time SINCE operator. This supports a straightforward specification-level baseline for an active revocation obligation with an elapsed deadline. The paper also states monitorability restrictions; an actual formula must pass the selected implementation's checks.

The [contract analysis](../protocol/rollback-contract-v2.md) expresses the central safety obligation with existing temporal operators. It is a mathematical specification, not a parser-tested MonPoly program or a performance result. Nevertheless, the proposed novelty argument must now explain why standard monitoring of the same events is insufficient. It cannot rely on comparing a richly instrumented custom monitor only against configuration hashes or fresh probes.

## What changes in the research direction

Reject as prospective contributions: adding persistent probes; reporting known session survival; implementing a basic temporal violation detector; comparing a monitor given more events against a baseline denied those events.

Retain as an unproven candidate: determine what evidence is sufficient to distinguish an acknowledged policy revision from actual enforcement on all relevant paths, under a stated revocation contract. This would require either a demonstrably useful measurement result, a validated diagnostic method, or a substantive formal result beyond established partial-observation reasoning. We have none of those yet.

Before any further testbed expansion:

1. Pin versions and inspect what each acknowledgement actually guarantees, including the distinction between object acceptance, rule programming and effective enforcement.
2. Review monitoring with incomplete/out-of-order logs and distributed enforcement acknowledgements. Search for counterexamples to the proposed evidence claim, not only supporting papers.
3. Define externally observable ground truth and an identical-input baseline. If both methods use the same complete trace, ordinary temporal evaluation is expected to agree.
4. Freeze a contribution-specific hypothesis only if a distinct gap survives. Otherwise retain this repository as a reproducible replication/conformance study and select the next project by literature review.

No HPC job, Docker experiment, cluster deployment or manuscript result was produced in this stage.
