# Exact source/conflict audit

The actual merge of Lane 5 candidate 832d986b03dc3c940eb99a1ae6845dd07297f4ed into Lane 3 r4 ac3028b00aa37c08b2210b1c9a1fe8444060c0f9 had zero textual conflicts. PATCH_CHECKS.json binds each patch to its full parent/source SHA and an isolated Git-index apply check. These checks do not compile C++ or prove runtime behavior.

| Surface | Adaptation / next integration check |
|---|---|
| FT bank and WB/WAD lifetime | Consume Lane 5 clock-only 1565f1f04978f12e51a29fcbf9dab9a3c61b5c4e. Native Tag timestamps still receive the memcpy ordering offset; FT bank operations and WB/WAD births use physical GPU cycles, with the candidate monotonic assertion. |
| RO bank callbacks | Actual ReturnQ and ICNT callers already supply GPU physical cycles. New boundary checks reject a mismatched cycle before bank service. RO-created sector packets and victim WB creation/enqueue use physical timestamps. |
| Warmup payload identity | Consume warmup delta 5d974c3bf116ad21da74d3a27eace028c1f2e197. RO checks prefill before mutation and verifies actual Tag index, shared owner/handle, bank class and ready masks after prefill. Existing Tag-generation vector advances; no extra array is introduced. |
| Epoch / host writes | RO permits only initialization before the single whole-commandlist epoch starts. Once ever_open is true, a drained kernel or final epoch boundary does not reopen permission to warm a certified line. Existing Framework host-copy checks remain. |
| Late detached fill | Old payload id/generation remains the destination; no Tag installation by detached return. No lookup of detached completions by address is introduced. |
| Shared request capacity | D512 and combined address32 guard unchanged; detach-only uses the native128 index, bypass does not allocate native RO entries. |
| Future official R0.1 conflict hotspots | force_tag_access, ft_access clock local, payload request arbiter, Tag sidecar ownership. Keep official common repair first; add RO guards without deleting official dirty-victim/pending/pin handling. No actual official-parent apply check is claimed until its SHA is published. |

Unresolved common-repair issue belongs to Lane 1: the uncompiled warmup candidate can release an old dirty resident at a MISS without staging a WB; it also chooses a payload before calling native Tag fill. A generic after-kernel warmup must not lose dirty versions. The RO guard narrows *its own* warmup to pre-epoch initialization and adds a chosen-index consistency check, but does not claim to fix or qualify all-OFF/common warmup semantics. Lane 1 must test/reject the remaining cases per review_r3 before official release. Candidate assertions are retained; none are disabled to pass a warmed read.

Scientific withdrawal is snapshotted from Lane 5 b134f76d8f4cd759c0852b68edf922ecbd445ea9, including the six suspended runs and four unstarted rows. COMPLETE_VALID remains the old execution fact; it is not current scientific acceptance. Configuration preparation now names both repair gates and requires latest CURRENT_ACCEPTED identity/supersession evidence at launch. The tool itself still does not launch or qualify a simulator.
