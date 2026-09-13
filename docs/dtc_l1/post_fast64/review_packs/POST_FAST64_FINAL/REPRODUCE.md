# Reproduce the Lane-E review pack

No simulator, trace capture, GPU, raw SIM_HOST directory, or active Codex session is required. Python 3 and Pillow are required; exact build/font provenance is in `E_BUILD_PROVENANCE.tsv`.

```bash
python3 util/dtc_l1/build_post_fast64_lane_e.py --build-core --inputs docs/dtc_l1/post_fast64/lane_e/inputs --output /tmp/lane-e-core
python3 util/dtc_l1/build_post_fast64_lane_e.py --validate-core --inputs docs/dtc_l1/post_fast64/lane_e/inputs --output /tmp/lane-e-core
python3 util/dtc_l1/build_post_fast64_lane_e.py --build --inputs docs/dtc_l1/post_fast64/lane_e/inputs --qa-dir docs/dtc_l1/post_fast64/lane_e/qa_records --output /tmp/lane-e-final
python3 util/dtc_l1/build_post_fast64_lane_e.py --validate --inputs docs/dtc_l1/post_fast64/lane_e/inputs --output /tmp/lane-e-final
```

The final command consumes frozen compact inputs and explicit QA records only; it never launches a simulator.
