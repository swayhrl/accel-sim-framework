# Source-bound resume with immutable prior attempts

Optional --resume reuses only complete per-mode receipts with exact hardware,
fixture, full-top/GEN and test-scope identity plus decoded accepted binary SHA.
The full-base Unified result cannot qualify the highest physical-slot test.
Owner/concurrency validate actual accepted archives and reject changed source
or fixture across each compile/run; Lane3 supports both legacy and explicit
new archive paths.

When a mode has any prior raw or compressed executable, compile/run log or
archive, its next attempt gets a fresh exclusive attempts/MODE-rN directory.
The prior binary/archive/log is never overwritten or unlinked. Already-passed
modes are not re-executed. Receipts point to exact current attempt logs/archive.
Only the current ongoing receipt accumulates newly successful modes; frozen
published packs and their original rows/files remain unchanged.

IO-only artifact regression passed for compressed-only interruption, retained
logs/raw VVP, repeated retries, first-use layout and archive digest rejection.
No compiler/RTL regression/EDA tool ran for this helper change. R3 hardware
source remains e8d67d13, and its incomplete mandatory real qualification stays
INCOMPLETE. R3A ac607 tree is read-only. B0 d74 tests remain separate.
