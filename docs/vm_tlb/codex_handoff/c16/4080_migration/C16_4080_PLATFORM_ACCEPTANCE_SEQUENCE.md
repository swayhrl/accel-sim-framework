# C16 RTX4080 platform acceptance sequence

This sequence is deliberately serial at profiler boundaries. It is an acceptance plan, not permission to launch a GPU workload during source preparation.

1. **P0 source admission** — verify this package's base commit `f6a2d064796ac8cf027846e573200943b1ba4182`, source receipt hashes, and host-owner approval.
2. **P1 prechange audit** — run only the read-only inventory/security/preflight templates; review the A receipt. No host mutation or GPU workload.
3. **P2 approved admin configuration** — administrator applies the approved driver/Docker/NVIDIA Container Toolkit policy and, on this trusted dedicated host only, `NVreg_RestrictProfilingToAdminUsers=0`; reboot/reload as required; rerun P1 to prove loaded state.
4. **P3 container admission** — administrator creates the fixed-digest, fixed-UUID, fixed-whitelist container; audit that research UID/GID has no sudo, Docker socket, privileged mode, SYS_ADMIN, or prohibited mount.
5. **P4 NCU N0–N2** — ordinary-user permission proof, one tiny counter canary, then immutable NCU/image/metric/UUID freeze. NCU is mandatory.
6. **P5 model-native admission** — conduct N3 Llama native baseline with no NCU or NVBit; close model/input/runtime/checksum identity.
7. **P6 local-kernel admission** — conduct N4 4080 census and bind a local code object/static target. The RTX3090 target is reference-only.
8. **P7 profiler lanes** — N5/N6 NCU capture and closure occur as one separate lane. NVBit qualification/canary may occur only in another process/window and starts from Recovery-V2 S5 as positive reference; Recovery-V3 is negative-control-only.
9. **P8 formal admission** — permit a formal NCU or NVBit target only after its own clean N6/trace closure, no stale process/marker, immutable command and target identity, and host-owner approval.

At every stage write a new receipt. Failed stages remain evidence; do not overwrite directories, reuse an armed measurement marker, or relax security isolation to make a profiler work.
