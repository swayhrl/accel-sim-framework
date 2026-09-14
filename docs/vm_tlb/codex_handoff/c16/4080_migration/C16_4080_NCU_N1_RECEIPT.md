# C16 RTX4080 NCU N1 tiny hardware-counter canary

Status: `NCU_N1_HARDWARE_COUNTER_CANARY_PASS`

Exactly one NCU profile was run as ordinary user `huangrulin`. It profiled no
model, used no Docker or NVBit, and used neither root nor a capability workaround.
Earlier N1 directories contain only pre-profile metric-query failures; they did
not compile or launch the fixture and did not invoke NCU profiling.

| Field | Value |
| --- | --- |
| Fixture source | `util/vm_tlb/c16/host_4080/ncu_n1_vector_add.cu` |
| Source SHA256 | `eeb35a0fd71429fef59aff7643a73fafc97c426dff452cd02974893e89c6a2d0` |
| Metric file SHA256 | `44b2a484b6305b73b1dc587c58bd35255bcb01dbe2940584c7bc14678fe25680` |
| Frozen metric | `sm__cycles_elapsed.avg` (AD103 query observed it as Counter, unit `cycle`) |
| Binary | `/data/c16/ncu/canary/C16_NCU_N1_20260914T094300Z/c16_ncu_vector_add` |
| Binary SHA256 | `870e8a73373f8676eb01b337e2d0916a0e77c12b658fc197734d9fbd72e0e093` |
| Native result | `C16_NCU_CANARY_NATIVE_PASS`, checksum `25288758001664` |
| Profiled kernel | `<unnamed>::c16_vector_add_kernel(const unsigned int *, const unsigned int *, unsigned int *, unsigned long)` |
| Metric result | `sm__cycles_elapsed.avg = 32375.236842 cycle` |
| Raw report | `/data/c16/ncu/C16_NCU_N1_vector_add_20260914T094300Z.ncu-rep` |
| Raw report SHA256 | `d2e97a920a998d76f14902d21e3d71b6e23d11ad00cf2eed797b4b0758e07102` |
| CSV export | `/data/c16/ncu/canary/C16_NCU_N1_20260914T094300Z/report_raw.csv` |
| CSV SHA256 | `372ee15d20bc6ac44a5178b23e7cbc350d8890e10f354689c76ac87ffcb56d17` |
| NCU / GPU / driver / kernel | `2025.1.1.0` / RTX 4080 UUID `GPU-ce6cba36-415b-4e27-40e2-bded6bc1ee59` / `580.178.04` / `7.0.0-31-generic` |

Exact compile argv:

```text
/usr/local/cuda-12.8/bin/nvcc -std=c++17 -O2 -arch=sm_89 /home/huangrulin/workspace/accel-sim-framework/util/vm_tlb/c16/host_4080/ncu_n1_vector_add.cu -o /data/c16/ncu/canary/C16_NCU_N1_20260914T094300Z/c16_ncu_vector_add
```

Exact profile argv (bounded by `timeout --foreground 120s`):

```text
/opt/nvidia/nsight-compute/2025.1.1/ncu --target-processes application-only --replay-mode kernel --kernel-name-base function --kernel-name c16_vector_add_kernel --metrics sm__cycles_elapsed.avg --export /data/c16/ncu/C16_NCU_N1_vector_add_20260914T094300Z /data/c16/ncu/canary/C16_NCU_N1_20260914T094300Z/c16_ncu_vector_add
```

The same NCU reopened the raw report with `--import --page raw --csv`, producing
the listed CSV. Pre- and post-profile compute-process records are empty and the
post-profile NCU process check is empty. Raw report and CSV remain outside Git.
