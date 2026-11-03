# Independent vectorAdd six-source negative-control review

Decision: **PASS_WITH_EXISTING_SOURCE_AND_COUNTER_SCOPE_LIMITS**. All55 independent check groups passed for B_vectoradd_three_profiles_v1, manifest `06a0d2ec6752970574cb7a67436679020288d23c741bc714d95f9b48d10b9046`.

All six closed RESULT/raw gzip/uncompressed/natural-exit identities, fixed build, exact one-kernel geometry and counters match. The input is e7bb67e6 DTC6M,84000768 active-thread instructions and23438CTAs; it is separate from EP4M and matrix-vector two-kernel inputs. Both new CH results pass strict,21-entry native restore and genuine164 archive chunk SHA checks.

| Profile | CH cycles | DH cycles | CH self speedup | DH self speedup | I |
| --- | --- | --- | --- | --- | --- |
| P0 | 220803 | 217305 | 1 | 1 | 1 |
| F128 | 214503 | 213053 | 1.029370 | 1.019957 | 0.990856 |
| F256 | 223020 | 236217 | 0.990059 | 0.919938 | 0.929175 |

All six explicit GLOBAL accepted/read-miss/DRAM-read counts equal1500000 sectors/atoms32B; L2 total accesses/misses equal2250000 and pending hits are zero. Each DH source has375000 OO128B new misses, lower creations/issued/responses and acquired/released credits, with explicit zero valid/pending hits. This is observed same-domain conservation, not permission to replace missing fields with zeros.

DH F256 uses8.702975% more cycles than P0 and5.917407% more than matched CH despite L2 retries decreasing5068832 to2472990 and ICNT admission-block events4943384 to2374608. Read MSHR entry failure increases while miss-queue retries decrease. The negative result remains in the fixed set; lower retry counts are not a sufficient performance predictor or proof of reduced critical wait.

All six latency mean dictionaries are empty and raw mean fields are unprinted, despite explicit nonzero DRAM reads. Every run ends below500000cycles, consistent with known fold/print-window limitations. These means stay unavailable, not zero. Reported maxima were independently matched to raw values; F256 large maxima are tail clues, not means, critical-load identification, exact queue residence or causal attribution. Service sums/ratios retain entry/sample domains rather than a fraction of runtime.

Active domains remain CH common PIB256 versus DH OO PIB128, generic DH PIB8 inactive for OO admission. Unprinted OO pressure fields stay null. FR-FCFS changes couple shared credits255/319/447. Candidate source/captureELF/numeric binding and equal-area boundaries remain disclosed.

This is one frozen-input interim review, not all16 terminal acceptance, a suiteGM or release of further experiments. No model, running component, owner, registry, historical source/result,48 plan or v0.23 manuscript was changed. REVIEW.json contains all55 checks with paths/hashes; independent_audit.py is the read-only reproduction.
