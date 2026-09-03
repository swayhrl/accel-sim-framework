# Kernel manifests

Raw rank0 traces and raw/full `kernelslist.g` are retained inside both archives.
The filename-only 724/772 COMPUTE reports are historical-invalid for semantic
interpretation: `kernelslist.g` contains opaque filenames, while the semantic
name is in each trace header. The M4A merge-prep classifier reads exactly one
embedded `-kernel name` header per trace. It finds prefill = 692 COMPUTE + 32
NCCL and decode1 = 740 COMPUTE + 32 NCCL, with one observed NCCL semantic
family: `ncclDevKernel_AllReduce_Sum_bf16_TREE...`. Raw evidence is intact and
the permanent keep/drop decision remains `DEFER_TO_M4B_INTEGRATION`.
