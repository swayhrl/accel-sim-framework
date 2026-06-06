# A1 build and binary smoke

## Purpose

Verify that Accel-Sim can be built reproducibly and that the trace-driven simulator binary is usable.

The repo already appears to contain gpu-simulator/bin/release/accel-sim.out, but do not assume it is current. Try to rebuild and record the result.

## Required tracked script

Create:

    scripts/accelsim/a1_build_smoke.sh

Required behavior:

- cd to repo root.
- Source scripts/accelsim/accelsim_env.sh.
- Install or verify Python requirements:
    pip3 install -r requirements.txt
  If pip install fails due permissions or network, record the failure and continue if imports already work.
- Prefer Make build first:
    make -j$(nproc) -C ./gpu-simulator/
- If Make fails, try CMake build:
    cmake -S ./gpu-simulator/ -B ./gpu-simulator/build
    cmake --build ./gpu-simulator/build -j$(nproc)
    cmake --install ./gpu-simulator/build
- Do not delete existing build outputs unless necessary.
- Capture all output into .local_logs/A1_build_TIMESTAMP.log.
- Write a summary to .local_reports/A1_build_smoke_TIMESTAMP.md.
- Check:
    test -x ./gpu-simulator/bin/release/accel-sim.out
- Capture one safe binary smoke output:
    ./gpu-simulator/bin/release/accel-sim.out --help
  Some versions may not support --help cleanly. If it returns nonzero but prints usage, record as usable. Do not mark failure solely due to --help nonzero.
- Also run:
    file ./gpu-simulator/bin/release/accel-sim.out
    ldd ./gpu-simulator/bin/release/accel-sim.out
  Record missing libs if any.

## Failure handling

If both Make and CMake fail but an executable binary exists, mark A1 as PARTIAL_PASS_BINARY_EXISTS and include:

- build failure reason
- binary path
- binary timestamp
- whether ldd has missing libraries
- next suggested fix

If no executable exists, mark A1 FAILED and stop before A2 unless Codex can fix a simple environment issue.

## A1 pass criteria

- accel-sim.out exists and is executable.
- Build succeeded, or existing binary is verified and build failure is clearly documented.
- A1 log and markdown report exist.
- git status only shows intended tracked script/doc changes.
