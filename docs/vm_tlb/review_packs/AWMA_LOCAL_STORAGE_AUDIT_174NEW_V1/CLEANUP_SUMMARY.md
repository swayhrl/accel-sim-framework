# Cleanup summary — read-only

The local overlay has about 43.5GB under `/root`; node164 is excluded. Dominant consumers are an unrelated `offline-sim-v1` workspace (~27.5GB), preserved AWMA runtime (~5.6GB), VS Code server (~3.9GB), and the shared active Accel-Sim repository (~3.8GB).

Conservative reclaimable estimate: 286,744,576 bytes, only the conventional pip cache and only after a separately authorized cleanup stage. Upper-bound is intentionally not calculated as a safe deletion estimate because large consumers are shared, active, reproducibility-critical, or unknown. No deletion occurred.
