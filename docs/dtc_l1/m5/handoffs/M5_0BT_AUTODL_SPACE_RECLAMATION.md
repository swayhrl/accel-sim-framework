# M5.0BT — AutoDL provenance-preserving space reclamation

Status: `R5_GATE_PASS; SYR2K_CAPTURE_ACTIVE`.

This recovery is capture-host storage management only.  It changes no Core
behavior, frozen platform/configuration, trace identity, replay result, or
acceptance gate.  The control-side implementation is Framework
`6bb28841d2b791080d1b6c912dca8ae824b2c54d`, whose no-GPU controller and
contract regressions PASS.

## Fail-closed evidence and policy

The live heavy-pilot receipt requires `55,353,177,980` free bytes.  Its gate
correctly refused SYR2K while the capture volume held fewer bytes.  The
recovery did not weaken the receipt, change its budget, or delete BICG (the
capture-side BICG storage-admission/provenance anchor).  The explicit
`--evict-offloaded` controller operation is opt-in and requires a receipt
binding the remote archive SHA, trace bundle ID, remote `SHA256SUMS`, local
archive SHA and `LOCAL_IMMUTABLE_PASS`; it was not needed for R1/R2.

## Reclamation ledger

| step | removed path class | bytes removed | reason | free before | free after | gate after |
| --- | --- | ---: | --- | ---: | ---: | --- |
| R1 | controller tracer scratch and probe-tool directories | 18,112,615 | non-scientific, controller-regenerable build/probe products | 54,886,830,080 | 54,905,155,584 | FAIL (expected: still below budget) |
| R2 | one GESUMMV failed attempt's raw working directory | 573,214,227 | checker-failed non-candidate attempt (1,964 mismatches), separately superseded by the source-repair-provenanced accepted GESUMMV bundle | 54,905,151,488 | 55,478,362,112 | PASS |
| R3 | ATAX remote uncompressed working bundle | 5,806,756,882 | redundant only after remote archive SHA, SIM_HOST archive SHA, local immutable `SHA256SUMS` binding and recorded local validation all passed | 54,448,041,984 (last exact pre-receipt sample) | 59,566,977,024 | PASS (59,432,751,104 at gate sample) |
| R4 | MVT remote uncompressed working bundle | 5,777,441,032 | redundant only after remote archive SHA, SIM_HOST archive SHA, local immutable `SHA256SUMS` binding and recorded local validation all passed | 54,885,117,952 | 59,949,592,576 (first post-deletion observation while SYR2K writes continued) | PASS (59,907,649,536 at controller gate sample) |
| R5 | GEMVER remote uncompressed working bundle | 2,647,569,402 | redundant only after remote archive SHA, SIM_HOST archive SHA, local immutable `SHA256SUMS` binding and recorded local validation all passed | 57,012,793,344 | 59,584,905,216 | PASS (59,551,346,688 at controller gate sample) |

Before R2 removal, the compact application stdout, tracer stderr, empty
checker log, full file-size inventory and their `SHA256SUMS` were retained in
the capture host's reclamation evidence directory with a machine-readable
receipt.  The failed raw attempt was not a capture candidate, archive, local
immutable bundle, or formal result.  No remote SYRK archive or working data
was removed; its active copyback remained live.

R3 used Framework `6bb28841...`'s explicit `--evict-offloaded atax` action,
not a shell deletion.  It refused any incomplete proof and left the remote
ATAX archive in place.  SYR2K was already actively capturing, so its concurrent
trace writes mean the recorded `free_before` is the final exact pre-receipt
sample rather than an invented instantaneous value; the controller's separate
post-R3 gate sample is recorded above.  BICG and SYRK were not reclamation
targets.

R4 was triggered before SYR2K could consume the remaining start-gate margin.
The local and remote MVT archives both had SHA-256
`6c537caf1e110c3804bdc943211078565580f88d9ed85ac8dfa12d685964f270`, and
their bundle manifests both had SHA-256
`073fcc922d13e700c78c39429ae1bf55abc31d405ce5a2b5789f5f04b7ae5e10`.
The controller's proof-bound `--evict-offloaded mvt` action removed only
`bundles/mvt`; it preserved the remote archive and the locally immutable MVT
payload.  The remote machine-readable receipt is
`reclamation/R4_mvt_offload_evict.json`.  The unchanged gate then returned
`projected_bytes=55,353,177,980`, `free_bytes=59,907,649,536`, `status=PASS`.
SYR2K remained `CAPTURING` throughout; its active trace is not part of R4.

R5 applied the same controller proof to GEMVER before live SYR2K writes could
exhaust the renewed R4 margin. The local and remote GEMVER archive SHA is
`a7b660882539ce422cabf4fa26d1637f319071a9c3a7ff1d13804b4a3363228c`; the
matching remote/local bundle-manifest SHA is
`2f3e6a0be45a062a83805b2d123c37a7db8ccbdf7e579420bdf753a620f79011`.
`--evict-offloaded gemv` removed only `bundles/gemv` and retained the remote
archive and locally immutable GEMVER payload. Its machine receipt is
`reclamation/R5_gemv_offload_evict.json`; the unmodified gate passed with
`free_bytes=59,551,346,688`. SYR2K remained active throughout.

## Resume

Immediately after R2, the unmodified fail-closed gate returned
`projected_bytes=55,353,177,980`, `free_bytes=55,478,362,112`, `status=PASS`.
The capture host then started the one permitted SYR2K controller under the
exclusive capture lock.  The sequential next order remains SYR2K, SpMV, then
2MM; each still requires its normal checker, bundle, archive, copyback and
local immutable-store gates.
