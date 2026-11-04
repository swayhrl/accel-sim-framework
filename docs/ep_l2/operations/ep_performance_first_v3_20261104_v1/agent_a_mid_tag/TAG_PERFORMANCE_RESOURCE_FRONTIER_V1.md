# Tag performance/resource frontier V1

**Eight accepted reference points reused; eight intermediate geometry points prepared, performance UNKNOWN pending authorization/execution.**

| Input | Geometry | S cycles | WV cycles | Same-background S/WV |
|---|---|---:|---:|---:|
| FWT |REF32x8|181827|178951|1.01607x|
| FWT |G32x16|UNKNOWN|UNKNOWN|UNKNOWN|
| FWT |G64x8|UNKNOWN|UNKNOWN|UNKNOWN|
| FWT |G64x16|170266|170105|1.00095x|
| GEMM |REF32x8|558588|550642|1.01443x|
| GEMM |G32x16|UNKNOWN|UNKNOWN|UNKNOWN|
| GEMM |G64x8|UNKNOWN|UNKNOWN|UNKNOWN|
| GEMM |G64x16|548988|548988|1.00000x|

TAG_PERFORMANCE_RESOURCE_FRONTIER.csv/json uses null/UNKNOWN candidate values, never zero. Existing FWT WV G64x16 improves about4.94% versus own REF; GEMM about0.30%. S and WV both benefit; this is not all EP-specific acceleration.

The two512-Tag geometries have equal nominal4MiB addressability across64 slices but different associativity and decoder/address grouping. Their comparison distinguishes organization from count without changing DRAM or physical Payload. A middle point matching1024-Tag performance would bound excess for these inputs, not prove a universal optimum.

Resource proxies relative to REF32x8:

- G32x16:2x Tag entries,2x ways/comparisons per target set; same set count.
- G64x8:2x Tag entries, same8-way comparison width;2x sets and different real decoder.
- G64x16:4x Tag entries,2x ways and2x sets.
- Physical Payload remains9.125MiB aggregate (64x1168x128B), fixed four-bank P1, WB/Bypass/descriptor/WAD/MSHR/queues. More Tag addressability does not add Payload SRAM.

These are metadata/count proxies. Exact Tag bit widths, comparator/decoder area, wiring, access energy, timing and PPA remain UNKNOWN. Declared cache timing is fixed; extra16-way comparator delay is not automatically charged. No equal-area, calibrated hardware or new T contribution claim.

Next decision: execute bounded middle-geometry matched pairs only after authorization, select least-resource point retaining useful absolute performance, preserve regressions and zeros. No automatic finer geometry scan or FR-FCFS combination is released by this package.
