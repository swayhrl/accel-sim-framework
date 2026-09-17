# Continue 174-new — recover the frozen F0 base config from accepted Framework authority

This continuation supersedes any blocker that requires finding a file whose SHA256 equals `base_config_sha256`, `vm_overlay_sha256`, or `runtime_wrapper_sha256` as though all three were standalone replay artifacts.

## Accepted authorities

- accepted baseline commit: `2cbb3bd7c85dd46977c2dbbbe829961c2f03ab49`
- accepted Framework: `d64408a97d76a320a6d49468653d416e33677af8`
- accepted Core: `57bb71ecd015b6ec0ab32e45b0815e5beaf69172`
- accepted baseline ID: `SIM_BASELINE_6305c065f2c4913448b0cb61a85d5003030c5917cd37d6a346fd3f42939d5964`
- qualified binary SHA256: `34deedd99e85e52fb309852de2ecc5fecd9471436a33a5e77d40bc038a2c31c4`

`BASELINE_CONFIG_COMPONENTS.json` defines the actual config members:

- `configs/vm_tlb/c5_configs/C11_C5_PREFILL_F0.config`
  - required SHA256: `16f9f1866a541ac5686a02f15b8f3abf5fd8723601ff8795db77a64fffb8d446`
- `configs/vm_tlb/c5_configs/C11_C5_DECODE1_F0.config`
  - required SHA256: `cef8605b2168904a9f41e71f95967c478d8a5b358b16dcfc993df06ca23b820b`

The same file explicitly states that:

- `base_config_sha256 = 5d9ae7f5...` is the canonical-JSON root over the corresponding member object;
- `vm_overlay_sha256 = aec7364f...` is historical qualification provenance over its member object, not a current replay overlay file SHA.

The baseline qualification addendum states that the F0 config bytes at the accepted historical source pair matched the historical hashes and the original configs were left unchanged.

## Recovery path

A temporary remote branch is provided solely to make accepted Framework commit `d64408a...` normally fetchable:

`hrl/awma-baseline-authority-d644-recovery`

Do not execute the replay from that old branch. Use it only as a byte authority.

From the active first-current-model replay worktree:

```bash
git fetch origin hrl/awma-baseline-authority-d644-recovery
mkdir -p .awma_runtime/recovered_baseline_authority

git show FETCH_HEAD:configs/vm_tlb/c5_configs/C11_C5_PREFILL_F0.config \
  > .awma_runtime/recovered_baseline_authority/C11_C5_PREFILL_F0.config

git show FETCH_HEAD:configs/vm_tlb/c5_configs/C11_C5_DECODE1_F0.config \
  > .awma_runtime/recovered_baseline_authority/C11_C5_DECODE1_F0.config

sha256sum .awma_runtime/recovered_baseline_authority/C11_C5_*_F0.config
```

PASS requires exactly:

```text
16f9f1866a541ac5686a02f15b8f3abf5fd8723601ff8795db77a64fffb8d446  C11_C5_PREFILL_F0.config
cef8605b2168904a9f41e71f95967c478d8a5b358b16dcfc993df06ca23b820b  C11_C5_DECODE1_F0.config
```

For the current Q05 Prefill replay, use the recovered Prefill F0 config.

If the SHA does not match, STOP with the exact observed hash and do not alter bytes to force a match. The historical qualification statement and remote accepted Framework object would then be internally inconsistent and requires review.

## Overlay contract correction

Do **not** search for a standalone file with SHA256 `aec7364f1d2df147fe287088bbbfa91ff095dd855ac95089396d637fc45f60d8` to use as the current replay overlay.

Consumer preparation explicitly defines the current-model runtime overlay as a newly derived, hash-closed overlay containing exactly:

```text
-gpgpu_vm_object_map <current-model hash-preserved compatibility view>
-gpgpu_vm_weight_segment_map <current-model hash-preserved compatibility view>
-gpgpu_max_cycle 10000
```

`fixed_window_replay.py` hashes this new overlay plus its referenced assets for the SIM_RUN receipt.

Historical overlay member files at `d64408a...` may be recovered and rehashed only as qualification provenance; they are not substituted for current-model maps.

## Runtime-wrapper contract correction

Do **not** require the current `fixed_window_replay.py` source file to have SHA256 `73095444d883114deb54e14bf0794be247295c298b68c4dd27dff0d52247d931` before executing the new run.

That field remains part of the frozen baseline identity/provenance. The accepted consumer-preparation stage later added `fixed_window_replay.py` specifically for future current-model replay. Its runtime implementation validates the frozen baseline identity, qualified binary and accepted base-config member SHA, then hashes the current command/environment/effective config into the new SIM_RUN evidence.

Continue to use the accepted current consumer implementation, including the LDGDEPBAR validator hotfix authority, and record/hash its exact source in the new review pack.

## Continue without another intermediate stop

Once the Prefill F0 config SHA matches, resume the existing Goal immediately:

1. preserve the already-issued immutable `SIM_INPUT_ID` and its admission evidence;
2. verify the qualified simulator binary SHA;
3. create the current-model hash-preserved object-map/segment-map compatibility views;
4. create the restricted current-model 10k overlay;
5. run `fixed_window_replay.py` using the recovered accepted Prefill F0 config;
6. require `EXPECTED_FIXED_WINDOW_BOUNDARY` at `gpu_sim_cycle = 10000` plus telemetry PASS;
7. repeat the identical bounded run;
8. compare deterministic scientific receipts/normalized telemetry (raw log byte identity is not required if nondeterministic text exists);
9. issue `SIM_RUN_ID` and `SIM_EVIDENCE_ID` only after closure;
10. write final review pack/report; commit, push, and leave worktree clean.

Success states remain:

`SIM_COMPAT_CAPTURE_V1_QUALIFIED`

`FIRST_CURRENT_MODEL_BASELINE_SIM_PASS`

Do not start mechanism sweeps, Native↔Simulation numerical calibration, or full-ROI claims in this Goal.
