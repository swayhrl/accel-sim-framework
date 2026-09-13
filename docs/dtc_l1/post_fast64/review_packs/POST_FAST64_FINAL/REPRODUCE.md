# Reproduce the Lane-E review pack

No simulator, trace capture, GPU, raw SIM_HOST directory, or active Codex session is required. Python 3 and Pillow are required; exact build/font provenance is in `E_BUILD_PROVENANCE.tsv`.

```bash
python3 util/dtc_l1/build_post_fast64_lane_e.py --build-core --inputs docs/dtc_l1/post_fast64/lane_e/inputs --output /tmp/lane-e-core
python3 util/dtc_l1/build_post_fast64_lane_e.py --validate-core --inputs docs/dtc_l1/post_fast64/lane_e/inputs --output /tmp/lane-e-core
python3 util/dtc_l1/run_post_fast64_lane_e_qa.py --builder util/dtc_l1/build_post_fast64_lane_e.py --inputs docs/dtc_l1/post_fast64/lane_e/inputs --qa-dir docs/dtc_l1/post_fast64/lane_e/qa_records --negative --claim-audit --core-determinism
python3 util/dtc_l1/run_post_fast64_lane_e_qa.py --builder util/dtc_l1/build_post_fast64_lane_e.py --inputs docs/dtc_l1/post_fast64/lane_e/inputs --qa-dir docs/dtc_l1/post_fast64/lane_e/qa_records --validator-readonly --final-package docs/dtc_l1/post_fast64/review_packs/POST_FAST64_FINAL
python3 util/dtc_l1/run_post_fast64_lane_e_qa.py --builder util/dtc_l1/build_post_fast64_lane_e.py --inputs docs/dtc_l1/post_fast64/lane_e/inputs --qa-dir docs/dtc_l1/post_fast64/lane_e/qa_records --final-determinism
python3 util/dtc_l1/build_post_fast64_lane_e.py --build --inputs docs/dtc_l1/post_fast64/lane_e/inputs --qa-dir docs/dtc_l1/post_fast64/lane_e/qa_records --output /tmp/lane-e-final
python3 util/dtc_l1/build_post_fast64_lane_e.py --validate --inputs docs/dtc_l1/post_fast64/lane_e/inputs --output /tmp/lane-e-final
```

The formal build consumes frozen compact inputs and executed QA records only; it refuses a missing/non-PASS core determinism, final-package determinism, or validator-read-only record. It never launches a simulator.
