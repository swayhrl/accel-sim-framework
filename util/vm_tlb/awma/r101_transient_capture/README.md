# R101 L512 transient-L2 capture producer

This directory adapts the pinned R101 BF16 L512 first-step gradient payload to the accepted Route-B simulator-native tracer. The only tracer-source extension is an opt-in bounded multi-kernel ROI mode under `util/tracer_nvbit/route_b_1771/route_b_tracer.cu`; the accepted formatter and packet grammar are copied unchanged from producer authority `5143b4e10aaf2fc47bb60492155d2464b0b726fd`.

Execution order: `build_producer.sh` → `run_driver_audit.sh` → `prepare.py` → `run_census.sh` → `freeze_census.py` → `freeze_lifetime.py` → `launch_capture.py` canary1/canary_multi/formal → `region_address_sanity.py` → `parser_check.py` → `finalize.py` → `write_reports.py` → `publish.py`. All CUDA runs acquire `/data/c16/locks/c16_gpu_campaign.lock`; postprocessing, grammar/parser checks, sidecars, and node164 publication are CPU-only. The formal scope, selectors, caps, and source hashes are frozen in the review pack.

No algorithm, tile population, Newton–Schulz coefficient/step count, trace grammar, simulator, or 174-new GPU workload is changed by these scripts.
