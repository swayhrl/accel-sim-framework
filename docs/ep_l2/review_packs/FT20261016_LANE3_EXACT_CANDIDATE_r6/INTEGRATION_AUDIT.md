# Interface and lifecycle audit

| Surface | Exact adaptation / static evidence |
|---|---|
| New bool prefill entry | ft_try_force_tag_access rejects RO after ever_open before any release/reserve/Tag mutation. A false return reaches Lane 1's partition caller before its memcpy offset increment. The common function body is identical to62dc after removing exactly the two RO hook lines. |
| Existing force wrapper | Retain its RO prefill_begin check and Lane 1's checked try delegate. Default-OFF behavior uses the unchanged common implementation. |
| Successful initial prefill | Keep common selected-index assertion, generation-wrap check, clean/resident ownership, bank class and sector preservation. RO reuses its existing generation vector and validates the actual Tag/handle/ready masks only after success. |
| Shared clock | Both paths use Lane 1 ft_physical_cycle, sourced solely from GPU sim+total cycles. All timed FT bank and WB/WAD births retain physical time; native Tag timestamps retain the ordering offset. RO fill/read bridges check that supplied cycles equal the same helper. |
| GPU/partition memcpy | Exact-parent function comparisons preserve full-width host addresses, partial endpoints and partition hardware closure. The GPU-level additional RO whole-commandlist write rejection remains; no host-copy meaning is broadened. |
| Detached late sector fill | Existing transaction id/generation lookup, issued/ready masks and attached-only Tag callback remain unchanged. A detached old return cannot install into a reused Tag. No detached completion address CAM is added. |
| Descriptor / response | Shared D512/native128/address32 implementation and cycle-local response enqueue/pin release remain. Software ready selection is not an address merge search. No r4 local PASS is promoted to the new source. |

The actual merge had conflicts in ep-l2-ft-cache.inc, gpu-cache.h, l2cache.h and CMakeLists.txt. The repair candidate's common prefill was retained wholesale with RO hooks; the old inline partition prefill was replaced by Lane 1's guarded out-of-line implementation. One duplicate bank-counter test getter was removed. Both Lane 1 repair and Lane 3 RO EXCLUDE_FROM_ALL targets remain. Other Lane worktrees were not changed.

The newly staged cache checks call the bool prefill entry after epoch activation and after epoch end, assert false with unchanged Tag handle/bank grants, and retain the wrapper rejection. Partition cases check false and unchanged memcpy offset before requests and after full drain, where a mere empty-hardware check would otherwise admit the operation. Existing late-fill, sector, D512 and ICNT cases stay staged. The twelve partition matrix cases (four offset0; offset4096×C8/C16×four modes) are NOT_RUN.

Official source/binary freeze and Lane 5 physical_bank_clock, memcpy_payload_identity and separate RO feature gates remain necessary before formal RO applications. The latest Lane 5 acceptance snapshot has no current accepted application result. New withdrawals continue to veto old qualification/run terminals. No build or scientific acceptance is inferred from patch/tree equality or Python tests.
