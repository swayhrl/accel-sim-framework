# Latest Codex Report

Stage: `M1_FOUNDATION`

Status: **PASS — M2_IO_READ AUTHORIZED**

Core SHA: `48b0be73833fc89fcf833349e82886ddc6d883b0`

Framework implementation/parser SHA: `ff26ef4642fdf10d353fb7d981b931afb25291a8`

## M1 closeout

Authorized B07 recovery and R07.1-R07.6 are complete. The repaired L1-hit
true-completion path retires the Paper Base PIB UID; B07 `A:1:1` completes
with 166 native merge-full observations and PIB 33/33/0. A frozen clean
upstream run reports the same merge-full count.

All M1 HARD gates passed. The release Core build and CTest suite pass. B06
MSHR=1 reports 26,265 entry-full observations; B08 cap=2 reaches exactly peak
2 and closes 64 token acquires/releases. Strict parser output records both
the primary closure and independent PIB/Tag/lower/MSHR resource views.

LEGACY exactly matches frozen clean Core `91880c533` for deterministic hit,
merge, bypass, and VecAdd: dynamic instructions, cycles, L1 accesses/misses,
L2 global reads, and DRAM reads all agree.

## Review entry point

`review_packs/M1_FOUNDATION/README.md`

## Next action

Begin M2 IO-DTC whole-line read implementation. Do not start M5.
