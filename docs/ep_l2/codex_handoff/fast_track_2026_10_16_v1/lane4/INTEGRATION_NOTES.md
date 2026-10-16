# Lane 4 integration notes

1. The inherited QV100 `gpgpusim.config` has a quoted
   `-gpgpu_dram_timing_opt` value spanning lines 216–217. Per-physical-line
   `shlex.split` fails with `No closing quotation`. The Lane 4 adapter tokenizes
   the complete config text and still rejects unexpanded nested config inputs.
   The published Lane 5 `run.py:validate_config_closure` needs the same parsing
   treatment before using this actual QV100 input. This is an input-wrapper
   issue; no architecture setting is changed and no failed simulation is hidden.
2. Lane 4's current compiled candidate is historical M0a+M1 plus default-OFF
   metadata/read-reference diagnostics. It is not a B16 release. I_WB will hook
   the real Lane 1 staging path with extra diagnostic WB storage, preserving
   copy/read grants, WAD, lower queue and completion.
