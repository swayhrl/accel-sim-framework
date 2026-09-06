# M5.0BT SpMV source transfer readiness

Status: **AUTODL_SOURCE_SWITCH_PASS; SYR2K_ARCHIVE_GATED**.

This is a source-provenance/transport record for the exact Paper-10 SpMV
capture identity.  It is neither a capture result nor permission to use a
dirty worktree, substitute source, or start a capture without the existing
controller's storage/lock/source gates.

## Verified SIM_HOST source objects

| component | required identity | verified object/tree | transfer object SHA-256 | disposition |
| --- | --- | --- | --- | --- |
| SpMV wrapper | `gpgpu-workloads@de9cf4293f418877aa9cdb6a2395338ca06674a6` | commit `de9cf4293f418877aa9cdb6a2395338ca06674a6`; tree `5b8b3a8ea5121d89d451c54e4ec68dd300d0d5c2` | `f7dd365b923380592f8d6d9d95d0c392dc7e7553b525cb9659ea988209a14102` | complete-history Git bundle verifies PASS |
| Parboil support | `parboil@4e0fc54866546efa44fe93af57c9cef62f6c8eb9` | commit `4e0fc54866546efa44fe93af57c9cef62f6c8eb9`; tree `0bc89442638a5dfdf4feb8dc9964e158c9270bd2` | `8c250c801515d96df42fbda56c4aeba69a02c889450f343dd394c497f69951f2` | complete-history Git bundle verifies PASS |

The wrapper tree contains the canonical
`suites/parboil-wrapper/spmv/{Makefile,jds_kernels.cu,main.cu,...}` source
surface.  The staged Parboil checkout is clean at its pinned commit.  Bundle
verification was performed in new temporary bare repositories; no mutable
worktree is a source input.

## AutoDL transfer and source-switch receipt

The three source-transfer objects reached an isolated capture-host staging
directory with their exact SHA-256 values.  Both Git bundles then passed
complete-history verification in fresh temporary bare repositories.  A fresh
detached Parboil checkout from the transferred bundle was verified clean at
`4e0fc548...`, with tree `0bc8944...`, before becoming the source path used by
the already-running SpMV queue supervisor.  The pre-existing public-network
clone had made no progress for the observed interval; it was terminated only
after the verified replacement was ready, and its clone cleanup removed its
incomplete, non-candidate directory.  No trace, archive, capture attempt,
controller lock, or result state was changed by this source recovery.

The existing remote wrapper path independently remains clean at
`de9cf429...` / tree `5b8b3a8...`; the frozen matrix/vector checks remain
part of the supervisor.  Thus the sole remaining SpMV predecessor is the
current SYR2K `ARCHIVE_PASS` transition plus the controller's normal storage
and exclusive-lock gates.

## Bound Paper capture identity

The transfer objects are bound to the committed Paper-10 manifest row:

- canonical ID: `parboil_spmv_medium_bcsstk18`;
- matrix SHA-256: `abbe1909f57d6fc17fc800446bac326bd0c5343305cf193b3aa1bc8f40c82ec9`;
- vector SHA-256: `d155de2b9615cae3c2bb8b60a9e82a7d26be7e80de772a5f1c0cb830d2e49061`;
- build: CUDA 11.8, sm70, `-O2`, shared cudart;
- checker: `verify_m5_parboil_spmv_output.py`.

## Remaining gated action

Before the SpMV queue entry can start, the controller must:

1. retain the completed bundle-SHA and detached-checkout proofs above;
2. verify the already-frozen matrix/vector/reference identities again;
3. re-observe the exclusive capture lock and unchanged storage-admission
   state; and
4. let the existing `SYR2K -> SpMV -> 2MM` supervisor start SpMV only after
   those gates pass.

No SpMV capture has been launched by this transfer/recovery record.
