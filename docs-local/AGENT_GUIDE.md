# Offline-Sim V1 local agent guide

This is ordinary project documentation, not a repository-root agent instruction.

Work only under `/root/workspace/offline-sim-v1/`. The Framework repository and nested `gpu-simulator/gpgpu-sim` are separate Git repositories; commit Framework changes to the active Offline-Sim branch and never mix simulator-source changes into packaging work. Preserve simulator architecture behavior.

Use `OFFLINE_BUNDLE_ROOT` to locate bundle-local `cache`, `toolchain`, `dist`, and `logs`. Offline execution must not call `git clone`, `wget`, `curl`, or index-backed pip. Build and test receipts live in the bundle-local logs directory. Use the fixed logged runner for commands with a timeout.

For debugging, inspect the latest `<test>-latest.log` and `.rc`, simulator `justrun.sh`, `gpgpusim.config`, and trace configuration before altering infrastructure. Framework drives SASS trace replay and PTX launch orchestration; GPGPU-Sim implements shader, memory, cache, interconnect and DRAM behavior.
