# RTX4080 benchmark asset pilot 20261024 v1

One workload only: NVIDIA CUDA Samples vectorAdd, fixed source db3eea23946bca2e90a75eca2b5b3e07158a9e11. 4,000,000 float elements, srand(1), block256, one kernel. Device kernel unchanged; host adaptation patch retained. Historical CUDA9.1 SM70 numerical equivalence is not asserted.

Native correctness and successful third capture both exit0, max_abs_error0, FNV64 0a8162dae8a16ac5. Full kernel:15,625 CTAs,125,000 warps,2,125,000 records,64,000,000 active-lane instruction instances. All warps have17 records and one active terminal EXIT. Two16MB HtoD copies,250,000 LDG and125,000 STG records. No slicing or ROI filtering.

First capture loaded tool but produced no callbacks/traces. Second explicit device initialization failed likewise. Successful third attempt launches binary directly: applying LD_PRELOAD through nice/ionice wrappers suppressed callbacks. CPU nice is now preexec, I/O priority set externally by PID. Attempt1 log was overwritten by attempt2 due script path bug; original receipt/source/binary remain and the missing original log is disclosed. Two native correctness runs, three capture attempts total; no simulator.

Known resident ComfyUI untouched. Parent authorized independent pilot policy: shared GPU lock,15-second idle gate, reject new compute, abort only own process on competition. This is producer correctness/capture validation, not performance characterization.

Semantic qualification HOLD: ULDC.64 uniform destination/constant address, predicates, wide high halves are incomplete in legacy trace format. Structural full coverage gives no EP/Ada simulation qualification.

See evidence/RTX4080_PROGRAM_STATUS.json. Finite59 program rows from prior census, not every CUDA Sample. Existing109 SpMV small has GPU-proven SM89 full captures; new Vector is independently GPU-proven. Other SM70 headers are ISA evidence only:4080 can run older cubins. Unknown provenance must not be reported absent or automatically resampled. C16WARP1 events and AWMA calibration kernels are separate assets.

Next bulk phase (not executed): freeze suite/source/implementation/input manifest; inspect receipts for capture GPU provenance; repair and freeze Ada uniform/predicate/wide/constant trace contract and validate against SASS; build standard-input adapters and correct outputs; collect complete standard inputs under GPU lock; derive crops only from correct parent capture and record selection; seal source/input/binary/tool/GPU/commands/attempts/full trace/semantic checks; existing single sender/receiver locks and <=128MiB chunks through174-new into true164; independent SHA+extract+member checks then immutable publish; all-project access with architecture identity and per-project simulator eligibility separated. Do not switch SM70 CURRENT or replace scientific references. Source KEEP, release0.

Archive receiver/readback receipts are supplemental outside this frozen payload.
