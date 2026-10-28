Confirmed: pending natural-release budget was erased before strict acceptance.

| Completed generation | Raw estimate GiB | Initial realized GiB | Negative-C token erosion GiB | Realized at strict GiB | Added protection GiB |
|---|---:|---:|---:|---:|---:|
| scan R2 | 1.347712 | 1.344646 | 0.000000 | 1.346965 | 1.010224 |
| cutcp F256 | 15.646346 | 15.646346 | 15.646346 | 0.328643 | 0.246482 |
| hybridsort DH-P0 | 13.768680 | 13.768680 | 13.768680 | 0.173007 | 0.129756 |

cutcp chronology (CST): DONE18:16:28.160; pending token18:16:34; cutcp M8 dispatch~18:16:38.544; token0 at18:16:40; RESULT18:16:46.666; strict credit18:16:50.
hybridsort chronology (CST): DONE18:53:31.079; pending token18:53:33; cutcp Q128 dispatch~18:53:36.622; token0 at18:53:38; RESULT18:54:13.008; strict credit18:54:15.

large_job_aging.py71-75 debits every negative C from pending tokens before95-102 grants75% of the accepted remainder. The exact token accounting and ordering are facts. Claim-driven headroom consumption is strongly consistent with the full-cost new dispatches; not all negative C is claimed to be precisely caused by those claims. Writer gzip times, estimated event UTC and filesystem mtimes have the limitations recorded in JSON.

Minimal design only: natural-DONE + fresh-PSS + observed positive-margin pending tokens can provisionally earmark75% before backfill; effective target fence includes this escrow. Legal new claims cannot erase the earmark merely by producing negative C. Accepted strict/archive/restore transfers escrow once into strict protection; a definitive negative removes it; unknown remains provisional and never accepted. Keep full costs, physical gates,75/25, target feasibility/lifecycle and original records unchanged. No retroactive credits. Implement only after Main reviews/authorizes; focused rollback/no-closure/unknown/negative/double-count tests would be required.

Evidence: CHRONOLOGY_PROBE_V1.json; FINDING_AND_ESCROW_RULES_V1.json. No production writes, tests, signals, models, hooks or implementation occurred.
