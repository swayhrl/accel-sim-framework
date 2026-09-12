# C15 Lane B — capability-limited checkpoint

Status: `C15_B_NATIVE_CAPTURE_CAPABILITY_LIMITED_READY_FOR_REVIEW`.

This report describes the published B checkpoint at framework commit
`9ecd9cb4ecc7577b52d6e1e372769b0416365c14` on
`hrl/vm-c15-native-capture-v0`. It began from planning/handoff commit
`9a755b14b01c5a77a6fc98c2547616e1c490e806` in the isolated non-detached
worktree `/workspace/worktrees/accel-sim-vm-c15-native`.

## What is publishable

The sole review entry is
`docs/vm_tlb/review_packs/C15_LOWCOST_MULTIMODEL/lane_b/README.md`.
`PUBLISH_MANIFEST.json` lists and hashes 21 small artifacts. It contains:

- an actual host/tool/guard probe and three local-weight preflights;
- 13 executed synthetic contract checks, explicitly marked
  `SYNTHETIC_TEST_ONLY`;
- 22 frozen-C12 provenance records as `TRACE_HEADER_ONLY`; and
- empty/unknown native, scenario, capture, and lifetime tables rather than
  fabricated values.

The C12 source is fixed at `a268aba0d01310294074ded5bb8017e2092394c0`.
Its imported marker counts are not per-launch headers: no kernel name, shape,
launch identity, duration, or native object attribution has been inferred.

After its publication, B read C's committed selector only at
`4fd34b1837ab6e23832c9ab1f215869c9185f68a`. All 11 C manifest entries passed
byte-size and SHA256 validation; `CONSUMED_INPUTS.tsv` records the manifest
SHA256 `103c44c9bd264a9a3a64476047d5434f5cb8faf8354741153ccf13f1ff900b0e`.
C explicitly labels the selector `OFFLINE_ONLY_NOT_CAPTURE_AUTHORIZATION`, and
its historical fine strata are unknown/infeasible here. B therefore retained
zero capture targets rather than binding opaque historical indices to a native
launch.

## Capability result and budget

The probe found no `nvidia-smi`, no `/dev/nvidia*`, no `libcuda`, and no
installed `torch`/`transformers`/`accelerate`. Nsight Systems/Compute binaries
and CUDA 11.8 compiler presence are recorded, but do not establish an
instrumentable GPU or compatible model backend. The three local model roots
have nonempty indexed/monolithic weights and metadata, but their revisions are
unverified; no remote code or CPU fallback was run.

Accordingly, this checkpoint spent 0 native deployments, 0 scenarios, 0 target
windows, 0 capture bytes, and 0 GPU-active seconds. It did not start an
Accel-Sim/GPGPU-Sim build/replay, full ROI, full-model SASS, or any raw capture.
`RAW_LOG_INDEX.tsv` records that intentional absence.

## Validation and consumption

Executed successfully:

```text
python3 -m unittest tests/vm_tlb/c15/lane_b/test_c15_lane_b.py -v
python3 util/vm_tlb/c15/lane_b/c15_lane_b.py --self-test \
  --fixture-file docs/vm_tlb/chatgpt_handoff/c15_lowcost/fixtures/contract_examples.json
python3 util/vm_tlb/c15/lane_b/c15_lane_b.py --validate \
  --output-root docs/vm_tlb/review_packs/C15_LOWCOST_MULTIMODEL/lane_b
```

Consumers must fetch exactly `9ecd9cb4…`, validate its manifest, and retain
the evidence tiers. In particular, they must not select native capture targets
from the header-only directory or treat any fixture as a scientific result.

## Remaining gap / next permitted action

Native C15 work needs an already-authorized visible GPU, a compatible existing
backend, verified local model revision, and a resource-green preflight. Only
then may B restart with the real canary, unprofiled repetitions, and a
separate profiler-overhead pass; target selection and capture remain bounded by
the C15 contract. No additional authorization was inferred from this checkpoint.
