# Supplement S2: reference control architecture (unevaluated design)

This supplement is a newly assembled design description consistent with the manuscript discussion. It was not empirically tested and is not evidence of deployment.

## Threat-to-control correspondence
| Threat point | Proposed control | Evidence required | Evaluation status |
|---|---|---|---|
| Low-privilege request borrows agent authority | Authenticate requester; bind role cap to task | Trusted requester-role evidence | Not evaluated |
| Model selects an excessive tool | Deny-by-default pre-execution authorization | Requester scope, task scope, declared tool tier | Not evaluated |
| Tool description understates effect | Registration screening plus measured realized-effect comparison | Tool metadata, independent state/permission observation | Benchmark models the mismatch only |
| Irreversible operation | Human authorization/step-up confirmation and scoped credentials | Approved operation and target bound to execution | Not evaluated |
| Audit trail is modified | Append-only external log store and integrity hashes | Retained observation independent of tool credentials | Not evaluated |
| Effects differ from registration promise | Post-execution reconciliation and incident handling | Declared/realized effect pair and task authorization | Not evaluated |

## Layered flow
Requester identity -> request scope -> policy decision point -> execution gate -> scoped tool credentials -> tool operation -> independent effect observer -> append-only evidence store -> reconciliation report.

A model output is an untrusted proposal,not an authorization. Permission checks use the intersection of requester authority and legitimate task scope. Observed effects must not be inferred solely from the declared tier. The benchmark mock-effect score is not a validated production observer.

No thresholds,latency/throughput claims,control effectiveness percentages,or institutional implementation are inferred from this proposed design.
