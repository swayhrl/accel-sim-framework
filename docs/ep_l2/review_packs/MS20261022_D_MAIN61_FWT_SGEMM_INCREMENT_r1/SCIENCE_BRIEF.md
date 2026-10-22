# Scientific decision brief: two accepted main61 workload increments

## Performance and scientific populations

FWT S/F is 493,189/490,402 cycles: 2,787 fewer cycles, +0.568309% speedup (S/F−1), or −0.565098% cycle change (F/S−1). Its two endpoints execute 791,609,344 instructions. SGEMM S/F is 343,730/343,442 cycles: 288 fewer cycles, +0.083857% speedup, or −0.083787% cycle change; both endpoints execute 1,658,916,864 instructions. These are finite normal-P1 main61 measurements, not ideal-capacity runs.

FWT restores the sixth of the original seven MAIN inputs. The unweighted GM of accepted Conv/CFD/DWT/SAD/Vector/FWT is 0.9990537501× (−0.094625%). The old five values and negative CFD/DWT/Vector outcomes are unchanged. The original-seven GM remains UNKNOWN because Btree is HOLD. SGEMM is independently preregistered exploration and cannot fill Btree's slot or be pooled into an original-seven GM. The 93a9 five-pair diagnostic remains a separate identity/population; distinct workloads measured across cohorts are not a single completed denominator.

## FWT: measured mechanism, service, and traffic

| Whole-app final observation | S | F | Interpretation |
|---|---:|---:|---|
| Copy reads / copy writes, each direction |178,569|0|W-related logical copy disappearance; not an isolated W cycle saving |
| Physical bank grants |11,713,359|11,304,326|−3.4920%, retaining P1 |
| Lower reads |954,036|873,164|−80,872 reads |
| Lower read bytes |30,529,152|27,941,248|−8.4768% |
| Lower WB bytes |22,856,832|26,565,888|+16.2273% |
| WB created = lower accepted = completed |178,569|207,546|Closure within each endpoint; higher F writeback count |
| F victim read responses |UNKNOWN native V records|184,660|Includes 12,489 dirty-forward responses; these are a subset, not extra responses |
| F promotions / directory queries |UNKNOWN native V records|37,675 / 441,298|Counts do not identify exclusive saved cycles |

F additionally records 32,495 clean installs and 207,546 dirty installs; clean and dirty retention integrals are 823,977,852 and 1,954,741,834 slot-cycles. These are occupied-slot integrals, not elapsed application stalls. The served 184,660 sectors correspond to 5,909,120 bytes of victim service, but lower read reduction is only 2,587,904 bytes: direct-service events and avoided lower events are different populations and cannot be equated.

Total lower read+WB bytes rise 53,385,984→54,507,136 (+1,121,152; +2.1001%) while cycles decrease. This rules out describing the measurement simply as less total lower traffic. It does not prove a critical-path benefit from any one W/V feature.

Nonexclusive first-block admission request-wait sums rise 1,500,304→1,527,866, although application time falls. Copy/WB-space waits fall 178,569/890,651→0 and same-address WB waits 276,421→2,593. MissQ wait sums rise 12,870→785,957; F also records landing 336,379 and V-query 441,298. These observations suggest redistributed queue pressure after changed residence/writeback handling. They overlap across requests, slices and causes, and must not be added or subtracted into a program-stall budget.

## SGEMM: clean-victim opportunity with a small timing response

Copy reads/writes and WB creation/acceptance/completion/bytes are measured zero in both accepted endpoints. F records 10,592 clean victim installs, 35,936 direct read responses and 1,149,952 served-sector bytes, with no dirty install, dirty-forward response or promotion. F clean-retention integral is 313,781,298 slot-cycles.

Lower reads fall 139,632→135,168 (−4,464; −3.1970%), and read bytes 4,468,224→4,325,376. Physical grants fall 2,727,280→2,722,816 (also−4,464; −0.16368%). Thus direct victim reads 35,936 are not the same as avoided lower reads 4,464. No useful copy-saving attribution is supported by the zero-copy observation.

First-block admission wait sum rises 16,081→84,900; F V-query wait is 69,728 while data-service wait falls 16,081→15,172. The 288-cycle improvement coexists with more request-wait observations. A plausible explanation is that clean retention avoids some misses while added lookup and changed overlap offset much of the gain. That is a hypothesis, not a V-only causal estimate: S/F changes the full design and retry/matching behavior, not one isolated mechanism.

## RO, correctness, identity and unsupported attribution

Both F endpoints report accepted_oracle_candidates/accepted_ro/transactions/merges/detached/avoided_line_allocations/query_count all zero with 64 final readonly records. This is a measured zero certified-admission background. Actual workload RO opportunity remains UNKNOWN under the empty certificate; zero admission does not prove the workload has no readonly reuse. Successful Tag-detach application evidence is not expanded by these pairs. S lacks native V/RO records, so those missing S values remain UNKNOWN, not synthesized zero.

E's accepted endpoints retain 64-slice hardware drain, response/exact-requester closure (FWT 10,223,616 each; SGEMM 2,587,648 each), WB lower-accept closure and P1 peaks. Source/config/binary/trace/Q/run-key/receipt hashes are carried unchanged in EXACT_ACCEPTED_IDENTITIES.json. D neither requalifies E nor turns aggregate closure into numerical SASS/host-output validation. Source/capture/numeric uncertainties in SGEMM's frozen trace-model applicability remain outside these conclusions.

## Per-kernel localization remains explicitly unknown

The published accepted pairs set all four kernel_completion fields to null. E's SHA-bound terminal_summary JSONs contain final application cycles, not ordered per-kernel elapsed cycles; the exact metrics exports contain final 64-slice counters. Reported F native_snapshot_count 20 (FWT) and 2 (SGEMM), and proposed 19/1 kernel counts, do not give phase duration or kernel-level attribution. No trace/raw is scanned, no phase is filled with zero, and whole-app cycles are not relabeled as kernel cycles. An optional E request asks only for already saved small accepted kernel metadata; if absent, keep UNKNOWN. Whole-app analysis is delivered now.
