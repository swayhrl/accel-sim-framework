# Exact-base lifecycle and clock audit — source only

| Boundary | Exact62 adaptation / preserved behavior | Qualification |
|---|---|---|
| Native Tag vs physical time | Lane1 ft_physical_cycle preserved exactly, TVD helper delegates; native Tag access/bind/host fill keeps memcpy offset | incremental source check only |
| Host outer try interface | Lane1 actual frontend/lower/ICNT closure, offset increments only after success and abort wrapper retained verbatim | source equality to62 |
| Host refusal | mask/cache/drain/shared WAD/lookup/read lease/MSHR/issue/pending/dirty/reserved/role/bank/generation/landing checks before any mutation | source ordering; runtime pending |
| Exact detached alias | optional address/ticket, payload owner/role/pin/pending/generation checked first; reclaim uses physical time; no false-return branch after commit starts | source ordering; new gate uncompiled |
| Tag/payload identity | same-owner clean partial sectors reuse handle, ready mask OR, declared version-zero only, postfill actual chosen index checked; native full-width GPU memcpy unchanged | source equality/inspection |
| Mandatory WB | WB_STAGED waits real lower acceptance, WB_INFLIGHT valid reads forward before generic WAD rejection; writes/atomics/missing sectors wait; lower_accept/set_done remain actual producers | unchanged prior Lane2 source, not rerun |
| Shared bank/ICNT | actual bank service and pin/lease, real response enqueue then commit/unpin; all use physical GPU source | retained; no new runtime PASS |
| Epoch | mandatory WB/live read rejected by cleanup; optional entries reclaimed via sole allocator; host mutation uses full hardware closure | retained/adapter source only |

No new payload data array, WAD CAM, descriptor pool, bank, port, oracle or trace input. Physical payload remains1168/1160 at C16/C8, WAD128, D512 and the common128B copy latch. Default clean/dirty switches remainOFF. Native Tag-hit counts and TVD served-response counts stay separate; served bytes are not lower/DRAM saved bytes. Existing dirty post-lower retention counter still excludes clean occupancy.

New prepared case uses address0x100000000 and actual try-prefill: held ICNT response refusal, later dirty resident refusal, exact detached-alias state retention including offset/payload/Tag, ordinary dirty WB drain, then successful exact-alias reinit preserving an unrelated TVD entry. Every timed step audits physical bank grant<=1. This is executable test source, not an executed test or numerical full-byte proof.
