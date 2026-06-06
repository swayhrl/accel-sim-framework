# A6 clean baseline report template

## Status

PASS, PARTIAL_PASS, BLOCKED, or FAILED.

## Baseline commit

- Branch:
- Commit:
- Short commit:
- Git status at start:
- Git status at end:

## Environment

- CUDA:
- nvcc:
- gcc:
- g++:
- cmake:
- python3:
- ACCELSIM_ROOT:
- GPGPUSIM_ROOT:

## Build

- Command used:
- Build result:
- Binary:
- Binary timestamp:
- ldd missing libraries:
- Build log:

## Trace root

- Trace root:
- How selected:
- kernelslist.g count:

## Smoke reruns

### A2 style pre-trace smoke

- Run name:
- Result:
- Log:
- Stats CSV:

### A4 style smoke suite

- Run name:
- Result:
- Log:
- Stats CSV:

## Build string validation

- Dirty or modified marker found:
- Baseline commit found in logs or stats:
- Accel-Sim build string excerpts:
- GPGPU-Sim build string excerpts:

## Limitations

- This is a minimal smoke rerun, not a full Rodinia benchmark campaign.
- A3 tracer remains blocked if no GPU is visible.
- Only stats generated in this A6 rerun should be used for clean baseline references.

## Review pack

- Path:
