# EP-L2 Target Baseline overlays

`b0_legacy_850.config` is the C1--C3 target overlay and is applied after the
standard QV100 configuration.  It freezes 850 MHz DRAM as the primary point;
`b0_legacy_1ghz.config` is the only intended clock sensitivity overlay.

The four-field queue option is ordered `ICNT->L2:L2->DRAM:DRAM->L2:L2->ICNT`.
The independent DRAM scheduler queue and ReturnQ remain 128 and 192 per
channel respectively.  The 256 persistent descriptors are Core-owned and
are intentionally distinct from the 128-entry lower-issue queue.

These overlays do not enable any deferred C4+ mechanism or characterization.
