# Feasibility amendment v2

v1 completed but both restored sessions reset. The allow policy had removed the only conntrack match, so session-state continuity was not controlled. Keep a permanent all-state conntrack match on the scoped OUTPUT jump throughout all phases, including chain reconstruction. This keeps the tracking dependency active rather than changing it with the application policy. Record this as a harness confound correction, not evidence of a policy-engine defect.

v1 also attempted explicit revocation after a reset socket. This cannot attribute failure to the revocation policy. For v2 reopen under allow, confirm an echo, then revoke and test that distinct live socket. Preserve v1 but exclude its revocation-socket outcome from causal interpretation. Single trace per backend remains feasibility, not timing or prevalence evidence.
