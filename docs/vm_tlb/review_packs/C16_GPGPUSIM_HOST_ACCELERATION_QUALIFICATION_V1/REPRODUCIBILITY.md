# Reproducibility

## Environment

- Host: `hrl-174-new`, Ubuntu 22.04, AMD EPYC 9754, 512 logical CPUs, two NUMA nodes.
- CUDA headers/tool: `/root/workspace/c16_cuda_12_4_build` (12.4).
- Compiler: GCC/G++ 11.4.0.
- Build: release `-O3`; no LTO, PGO, or fast-math.
- Current authority binary SHA-256: `6be0986958ffbb8a128ce19e8a88b53a4c4838f97202c2f3d1c9dec6e9a02186`.

## Inputs

The benchmark list is the accepted 16-kernel prefix (global dynamic kernels 2926–2941), list SHA-256 `0948cad8583f9399d4fb61aa5a35270dc11b626a9ae89201324533c4361d35857`. The M1 config SHA-256 is `15e06af19200e7fb40af93c6a21b19290b581c327f420dd3fdefc3f4b33af3bdd`; trace config SHA-256 is `a46fe47a14f3ca4116a35c5bf1dc156f4e861484b91278e8b3f66e09519bd7e5b`.

The 59-kernel preferred prefix was attempted with list SHA `340468e82ac15da0f259a08a5d3429d3f838dcf24141b5ff30a0aa6c9ba766729`. It reached only 20 completed kernels in 175.93 seconds, so it was deliberately terminated as `ABORTED_NOT_SHORT`; receipt SHA `2da01cb76e00ac4ee1d597f0f3f03c372a857fe7920322d8851eb40c11c0dcad`.

## Recompute the qualification

```bash
python3 util/vm_tlb/c16/gpgpusim_host_acceleration_v1.py \
  --runs-root /root/share/mnt164/huangrulin/c16_ai_workload/host_acceleration_v1/qualification_runs/runs16 \
  --legacy-audit /root/workspace/accel-sim-framework-c16-e1-oracle-elastic-b16-reuse-canary-174new-v1/docs/vm_tlb/review_packs/C16_E1_ORACLE_ELASTIC_B16_REUSE_PERFORMANCE_CANARY_174NEW_V1/HOST_OVERHEAD_PREFIX_AUDIT.json \
  --output docs/vm_tlb/review_packs/C16_GPGPUSIM_HOST_ACCELERATION_QUALIFICATION_V1/QUALIFICATION.reproduced.json
cmp docs/vm_tlb/review_packs/C16_GPGPUSIM_HOST_ACCELERATION_QUALIFICATION_V1/QUALIFICATION.json \
    docs/vm_tlb/review_packs/C16_GPGPUSIM_HOST_ACCELERATION_QUALIFICATION_V1/QUALIFICATION.reproduced.json
```

`QUALIFICATION.json` re-verifies every recorded `OUTPUT_SHA256SUMS`, receipt, exact semantic tuple, normalized stdout SHA, and termination marker before producing a result.

## Candidate source replay

The rejected source candidate is Core commit `5bf79a3635ae4e84e4c0f5b8e7bbc46c48f7778e`; its directed test is:

```bash
python3 src/gpgpu-sim/tests/test_ptx_stats_disable_guards.py
src/gpgpu-sim/tests/run_oracle_elastic_residency_tests.sh
```

Both passed before benchmarking. The candidate was reverted by `c583a6f36d232bfc69f92a73e6b17a5080ebfaf3`; the committed rejected binary is evidence-only.
