# Kernel manifests

Raw rank0 traces and raw/full `kernelslist.g` are retained inside both archives.
The filename-only classifier reports all entries COMPUTE, but RF3 established
that this is not an absence of NCCL: a prefill middle trace header is
`ncclDevKernel_AllReduce_Sum_bf16_TREE...`. `kernelslist.g` contains filenames,
not embedded kernel names, so the current classifier cannot recognize it. Raw
evidence remains intact; no permanent keep/drop policy is made.
