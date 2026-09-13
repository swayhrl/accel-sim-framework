# Reproduce the Lane-E review pack

No simulator, trace capture, GPU, raw SIM_HOST directory, or active Codex session is required.

From the repository root, use the committed compact snapshots:

```bash
python3 util/dtc_l1/build_post_fast64_lane_e.py --build \
  --inputs docs/dtc_l1/post_fast64/lane_e/inputs \
  --output /tmp/post-fast64-lane-e-rebuild
python3 util/dtc_l1/build_post_fast64_lane_e.py --validate \
  --inputs docs/dtc_l1/post_fast64/lane_e/inputs \
  --output /tmp/post-fast64-lane-e-rebuild
```

The command writes only the supplied output directory.  The committed `review_packs/POST_FAST64_FINAL/` is built from the same snapshots.  `--import-git` is a one-time maintainer import mechanism and is not part of ordinary reproduction.
