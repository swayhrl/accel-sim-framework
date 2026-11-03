# Stage II-A first8 scientific figures

This read-only consumer renders only B_runtime_analysis_v1/PUBLICATION_PROVIDER.json and its SHA-verified RESULTS.json.gz/SUMMARY.json.gz. It also checks the B snapshot manifest. Fixed programs, order and full input digests are embedded in plot_first8.py. No original native result, model, authority, controller or Git state is changed.

## Run now or after natural first16 completion

```sh
/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_stage_iia_first16_execution_20261104_v1/agents/A_figures_v1/plot-venv/bin/python /root/share/mnt164/huangrulin/host174_storage_recovery/dtc_stage_iia_first16_execution_20261104_v1/agents/A_figures_v1/plot_first8.py --provider /root/share/mnt164/huangrulin/host174_storage_recovery/dtc_stage_iia_first16_execution_20261104_v1/agents/B_runtime_analysis_v1/PUBLICATION_PROVIDER.json
```

Optional `--output-root PATH` controls immutable snapshot storage; the script always updates only its own A_figures_v1/PUBLICATION_PROVIDER.json. Same provider+script SHA returns the existing verified snapshot without changing frozen file bytes or mtimes. SVG hash salt is fixed and Date metadata is explicitly omitted; the provider timestamp remains visible in the figure. REPRODUCIBILITY_CHECK.json proves all4 fresh SVG/PNG rerenders have identical SHA. A changed provider or script creates a new directory, preserving historical renders. Every snapshot includes its exact plotting source, data, input provider, environment and per-file SHA manifest. Nothing automatically registers or launches models.

## Reading the plots

- CH_DH_P0_normalized_first8.png/svg: two panels, own P0 cycles / configuration cycles; P0=1 and >1 is faster. F128/F256 points appear only after the complete matching CH-P0/CH-F/DH-P0/DH-F quadruple is accepted. Existing DH-only response is deliberately omitted until its CH match is accepted. Pending, negative and HOLD annotations are textual statuses, never zero or speedup-one values.
- relative_extra_DH_benefit_I_first8.png/svg: I=S_DH/S_CH for both F levels; <1 negative and =1 neutral cases remain. I>1 means the relative change favours DH; both designs may slow down. It does not prove DH beats CH or equal physical cost.
- GM on both figures uses exactly B summary common_F128_F256 population at both F levels, explicitly n/8. No per-program best profile or unequal-denominator GM comparison.

Current snapshot: 20261103T191610724309Z_dec3d0bf53_9d996a27; CH accepted3/16; common set n=1/8. This is the first8 predeclared subset, not core32 or full35. FIGURE_DATA.json includes all16 rows, source SHA pointers, cycles, status and input digests; missing plotted values stay null. Negative cases are preserved. Root is the sole publisher and final visual reviewer.

## Environment and validation

System Python had no Matplotlib. An isolated true164 `plot-venv` installs Matplotlib3.10.8 and NumPy2.2.6; requirements.lock.txt pins every plotting dependency actually used. Existing system/user packages were not modified. Installation TMPDIR/TMP/TEMP/PIP_CACHE_DIR and plotting MPLCONFIGDIR point to this directory; pip used --no-cache-dir and the existing127.0.0.1:27890 proxy. The venv, cache, installation log and old snapshots are not automatically publication members.

CPU_VALIDATION.json has10 assertions: fixed population/order, null missing values, negative case retention, source common-set agreement, corrupted SHA rejection and every output hash. All metrics are independently checked against cycles before plotting. These are consumer checks, not scientific simulations. Local PNGs have been initially inspected; final publication inspection remains with Root.

Source SHA: `9d996a2784a96a4ab5b970a73ddc5eeb481ab66b538dd3b4558d9e8781ef017e`. Current render manifest SHA: `3469ee53fbf4e24ebac5dd07a723e8192b9f5c27184236ba2b78b028475aed66`.
