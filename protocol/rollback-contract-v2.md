# Rollback contract and standard-monitor comparison

Status: specification analysis only, 2026-10-08. Supersedes no historical result. No claim of a new logic, theorem or validated implementation.

## Operational contract

For each session s and unique revocation obligation e, record:

- Revoke(s,e): the contract's effective revocation start. This is not automatically the time the Kubernetes API accepted an object.
- End(s,e): explicit cancellation, reauthorization or supersession of that obligation. Each identifier is used once and has at most one end.
- Deliver(s): independent observation of successful application delivery on the same session. A live file descriptor, retained conntrack entry or forwarded log line alone is insufficient.
- Delta: a nonnegative, fixed permitted revocation delay, selected before evaluation.

Require unambiguous session identity, complete ordered events over the assessed interval, defined clock units, and a documented connection-versus-packet contract. A rollback allowed to grandfather a session does not create a revocation obligation for that session.

## Basic safety predicate

At time t, report a violation if delivery occurs while an unended revocation is at least Delta old:

`Violation(s,t) = Deliver(s,t) AND EXISTS e,u: Revoke(s,e,u) AND t-u >= Delta AND NOT EXISTS v in [u,t]: End(s,e,v)`.

Disallow simultaneous Revoke and End for one identifier, or supply an explicit ordering. The mathematical past-temporal counterpart is:

`Deliver(s) AND EXISTS e: ((NOT End(s,e)) SINCE_[Delta,infinity) Revoke(s,e))`.

This is mathematical notation, not a claim that a particular parser accepts this spelling. The free/quantified variables, interval notation and monitorability must be validated against a pinned tool before execution. No new algorithm is required to state the obligation. Standard temporal monitoring is therefore a mandatory baseline.

Illustrative deductions, not collected data: with Delta=5, revocation at t=10 and delivery at t=14 is inside the grace period; delivery at t=15 violates the contract if no end occurs; an end at t=14 removes that obligation for delivery at t=15. A grandfathered session with no revocation does not violate this particular property.

## Observation limits and verdicts

A witnessed late delivery can establish a bounded contract violation if all relevant event identities, ordering and contract facts are trustworthy. Failure to observe delivery cannot establish universal isolation. Report only no witnessed violation over the stated complete observation interval, or inconclusive when evidence is incomplete. Do not convert a finite quiet trace into a guarantee about all traffic or future time.

Consider two executions with identical configuration hashes, API acknowledgements and fresh-connection results. An established session delivers after the deadline in one and does not in the other. A monitor receiving only those shared observations cannot distinguish the executions. This elementary indistinguishability argument motivates measurement, but is not a claimed novel theorem. Giving one method the missing session observation is an instrumentation advantage, not an algorithmic advance.

Clock uncertainty matters: if the possible delivery time and revocation start ranges straddle the deadline, the verdict is inconclusive. Lost end events can produce false violations; lost delivery events can hide violations. Missing acknowledgements cannot be silently interpreted as convergence. These concerns must be checked against existing incomplete-log and distributed-monitoring literature before becoming proposed contributions.

## Equal-input comparison

Give both the candidate and the baseline the same event schema, event ordering, epoch boundaries, missingness indicators and contract. Validate a standard monitor on independently labelled fixtures before live collection. Separate the value of additional sensors from monitor logic through evidence ablations. Existing pilot traces informed the design and are not held-out evaluation data.

Advance only if the literature review establishes a meaningful unanswered measurement or inference question. The current contract analysis weakens the case for building a new monitor; it does not establish novelty for a renamed evidence framework.
