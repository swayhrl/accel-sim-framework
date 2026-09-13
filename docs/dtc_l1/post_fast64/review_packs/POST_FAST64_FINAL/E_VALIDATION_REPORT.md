# Lane-E validation report

Overall: **PASS**

| Check | Status | Evidence |
|---|---|---|
| pinned source hash and snapshot integrity | PASS | manifest plus SHA-256 rechecked |
| exact FAST12 / 36 primary cell membership | PASS | 12 workloads and Base/IO/OO only |
| integer performance and GM arithmetic | PASS | recomputed from accepted cycles |
| Stage6 membership and deadlock boundary | PASS | D4=18; nonnumeric BICG/GESUMMV 16.5 retained; Btree numeric |
| D5 duplicate arithmetic and 7/3/2 classification | PASS | D/L and D/(L-D) recomputed from integers |
| metric-denominator scope | PASS | observer sampled active-SM cycles never replaced with 64*global cycles |
| claim/evidence boundary | PASS | D6 selected revision; no L2 dominance/duplicate-performance proof |
| negative fixture: wrong FAST12 membership | PASS | validator requires exact ordered 12 source rows |
| negative fixture: observer in GM | PASS | primary is read solely from FAST12 summary |
| negative fixture: numeric deadlock | PASS | requires NONNUMERIC for four BICG/GESUMMV 16.5 rows |
| negative fixture: OO proxy | PASS | requires qualified D5 exact OO duplicate fields |
| negative fixture: invented 40 KiB observer | PASS | requires D4 exact 24/32/48 membership |
| negative fixture: payload relabeled DRAM | PASS | scope string explicitly rejects DRAM/total-link terminology |
