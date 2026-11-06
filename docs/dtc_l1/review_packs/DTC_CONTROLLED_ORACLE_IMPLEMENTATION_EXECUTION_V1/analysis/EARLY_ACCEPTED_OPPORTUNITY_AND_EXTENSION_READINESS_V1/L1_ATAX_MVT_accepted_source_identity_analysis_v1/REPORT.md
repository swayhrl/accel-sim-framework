# Accepted L1 ATAX/MVT: independent identities and convergent GEMV timing

The two equal totals are independent actual accepted results, not evidence of a mistaken input identity. Neither matching same-binary OFF had closed at this audit, so both S_oracle and H remain UNKNOWN. No historical DH-P0 is used as OFF.

## Actual identities and strict evidence

| Item | MVT | ATAX |
|---|---|---|
| Full input SHA | `f437190767aaed4921e11e6b85f80fb3348da90ec0f18fa8fa1bdfcd76ae3079` | `eededb785179fc0488c5a01d95154f6748ea45a2ea7bb18ecdbc316cf5166950` |
| UUID | `6a524b3c-d4c9-43f2-862f-52aa1c294c31` | `249ab5a6-5659-464b-9d78-2ef35c7b0f88` |
| Actual PID / start ticks | 364916 / 1070781648 | 382071 / 1071036187 |
| Accepted cycles | 1,714,624 | 1,714,624 |
| Active instructions / CTAs | 145,666,048 / 32 | 145,666,048 / 32 |
| Declared HtoD commands / bytes | 5 / 67,174,400 | 4 / 67,158,016 |

Both native DONE records report observed real simulators, exit0, no stop reason and no retry. UUIDs, consumed INTENTs, PID/start pairs, native result directories, commandlists, bundles, individual trace-body SHAs, raw gzip/uncompressed SHAs and archive transaction IDs differ. Both native STRICT objects equal their own original RESULT proof, and both raw checksums match strict and DONE. Actual cmdline and option echo select the correct distinct trace entries. Detailed source path/SHA pins are in EVIDENCE_INDEX.json. This is a targeted identity/shape audit, not a repeat hash pass over all archive chunks.

The common frozen Core is `e6b41ab8992e7d41651501c4d34cfe24195c4f96`, Framework `02775fd795cde5aae1480d81cee6eb481d0a08f4`, binary `3f8e547d87893aaf7319e337883a2bcc1f5717138296e3e6d1425cc75d055283`, libcudart `174f53a02223ae69e4a549e60a310f7e69a9334748e719fd48c40640c2a0af43`, mode3,271 effective options. Each accepted archive records SOURCE_KEEP, native restore and22 independently verified entries.

## Per-kernel facts worth preserving

| Ordinal | MVT kernel | ATAX kernel | Actual cycles (each) | Active instructions (each) | CTA delta | Frozen 128B reference shape |
|---:|---|---|---:|---:|---:|---|
| 1 | `_Z11mvt_kernel1PfS_S_` | `_Z12atax_kernel1PfS_S_` | 1,185,017 | 71,380,992 | 16 | 524,416 warp loads x 1 line(s), 524,288 warp loads x 32 line(s) |
| 2 | `_Z11mvt_kernel2PfS_S_` | `_Z12atax_kernel2PfS_S_` | 529,607 | 74,285,056 | 16 | 1,048,704 warp loads x 1 line(s) |

K1 is 69.112% of the total and costs 2.237540 times K2. Equality is therefore present in each phase, not cancellation of opposite phase changes. Frozen body-qualification records match in all11 compared shape fields: per-kernel instructions, CTAs/warps, warp instruction records, global reference histogram, opcode/width/path counts and trace/SM version. K1 registers17,301,632 logical128B references; K2 registers1,048,704. Their sum18,350,336 equals each run's printed registered/closed completion-dependency count. These counts describe trace work and registration; they are not cache-hit or critical-path claims.

The original raw endpoints preserve mode3 exposure: after K1 eligible_admitted1,048,704 and events_enqueued=delivered11,376,816; after K2 the as-printed cumulative values are2,097,408 and11,903,280. Pending events0, real OO lower_created/issued/responses0, real lower-credit acquire/release0, active refs0 and PIB0 at the endpoints. Do not label the second cumulative exposure11,903,280 as K2-only work. Finite Tag/allocation/Ref/notification/collection/WB/retirement still execute.

Each raw kernel block has143 scalar integer key/value observations under the explicit parser. Across MVT versus ATAX only two keys differ:

| As-printed key | K1 MVT | K1 ATAX | K2 MVT | K2 ATAX |
|---|---:|---:|---:|---:|
| DTC_SERVICE_V1_physical_integral | 9,411,966,484 | 9,411,966,228 | 17,318,228,066 | 17,318,227,775 |
| gpu_total_sim_rate (wall execution throughput) | 149,960 | 158,624 | 216,121 | 223,414 |

Thus the complete observed state is not identical. The retained physical occupancy integral differs by256 at K1 and291 at the final endpoint; no demonstrated cycle/critical-path effect or causal reason is assigned. Wall simulation throughput varies with host execution and is not GPU performance. Other strings/noninteger/raw metadata are outside this143-key equality statement.

## Fixed source candidate: two matching GEMV bodies, different applications

The recovered Atlas source is pinned to gpu-app-collection `dad09cb0487845edc7524ded814c6cde9f0ef6a1`. ATAX source SHA `bca826a6e4fbdad67b11400ef2193210f43d8181441a0b9883e19445db049cfb` and MVT source SHA `83764e6633f3a0976423e0ba7ab351ac42b0eeb249bf59a9e3531c639d4923d6` are candidate-source identities, not certification of the captured ELF. Original source manifests and BUILD_VARIANT_AUTHORITY are pinned. Do not replace these with the later repaired M5 source variant.

- ATAX K1 (atax.cu84–96): `tmp[i] += A[i*NY+j] * x[j]`; MVT K1 (mvt.cu109–121): `x1[i] += a[i*N+j] * y_1[j]`. With NX=NY=N4096, both map an output index to a matrix row and loop across columns. Adjacent warp lanes own adjacent output rows, so at a fixed inner j their matrix reads are separated by4096 floats. The frozen trace confirms up to32 logical lines per warp load.
- ATAX K2 (atax.cu98–110): `y[j] += A[i*NY+j] * tmp[i]`; MVT K2 (mvt.cu124–136): `x2[i] += a[j*N+i] * y_2[j]`. Rename output/inner indices: both map a warp across contiguous columns for the current matrix row. The frozen trace confirms one logical line per warp load.
- Both sources use256x1 blocks and4096 outputs, consistent with16 CTAs per phase. The two function bodies match token-for-token after explicit identifier alpha-renaming and substituting the fixed size4096; token strings, mappings and SHA are retained in ANALYSIS.json. Member fields such as threadIdx.x are not renamed. This is source text equivalence, not a new normalized SASS/address-stream comparison.
- ATAX feeds the first kernel's tmp vector into its second GEMV; MVT uses separately initialized y_1/y_2 inputs and independent output vectors. ATAX declares four HtoD copies; MVT five. Initialization and numeric semantics therefore differ even though the loop bodies and measured work shape match. The recovered ATAX candidate also has its existing accumulator-initialization limitation; this audit makes no new numerical correctness claim.

## Explanation and uncertainty

A supported hypothesis is that L1_DATAREADY removes the address-dependent eligible read lower/refill path that previously differentiated the applications, exposing the common instruction, full-reference registration and finite completion schedule. Equal phase work and candidate kernel bodies make equal controlled-oracle phase cycles plausible. This is a source-backed explanation to test against matched OFF, not proof that the programs are interchangeable, that Tag is uniquely critical, or that equal cycles are guaranteed for every allocation/order.

K1 remains more expensive than K2 despite eligible data availability being idealized. Its much greater logical-reference fanout is consistent with retained Tag/physical/ref/collection costs; ordinary stores, dependencies, issue and WB remain alternative/concurrent constraints. No critical-path attribution follows by summing counters. Actual L2 traffic remains4,194,304 accepted write sectors and DRAM read/write commands0 at the final endpoint; eligible virtual events never create ordinary lower mem_fetch reads. Nonzero averagemflatency1079 describes remaining actual request traffic and must not be reinterpreted as virtual-event latency.

The continuation's two installed postprocess repairs are preserved: approval-key alias and independently source-proven sparse-L2-zero reporting. Raw missing GLOBAL_ACC_R TOTAL_ACCESS remains null, while a separate proven derived read count is0. Neither repair is a new simulation or a changed Core. This audit changes no source/runtime/registry/owner/model/history.

For final interpretation retain: K1 versus K2 exact cycle split; one-line versus32-line reference work; mode3 physical/Tag/service occupancy and WB stalls as correlates; actual same-binary OFF phase comparisons when those rows close; ATAX inter-kernel dataflow and MVT independent-vector distinction; all capture-ELF/HtoD/value/numerical limits. No S/H or historical-baseline speedup is reported here.
