# Local reproduction, not a production run

The two `.cpp` files here are self-contained **source-function extraction fixtures**, not full GPGPU-Sim tests. They were compiled and executed in the ChatGPT isolated container; old174/174-new, scientific data and registry were not touched. Follow the existing host's resource policy before running any compiler there; these commands are not an admission exception.

```sh
mkdir audit-local-build
# Keep assertions enabled; do not add -DNDEBUG.
g++ -std=c++11 -O0 -g -Wall -Wextra -fsanitize=address,undefined \
  repro_bank_retry.cpp -o audit-local-build/repro_bank_retry
g++ -std=c++11 -O0 -g -Wall -Wextra -Wno-unused-parameter \
  -fsanitize=address,undefined repro_replacement_target.cpp \
  -o audit-local-build/repro_replacement_target
./audit-local-build/repro_bank_retry
./audit-local-build/repro_replacement_target
```

Observed output:

```text
CONTROL stable role and selected requester: grant at next cycle
REPRO role transition: 1000 consecutive denied retries; selected old RO read remains parked
REPRO candidate switch: 1000 denied retries of new slot0; retry of original slot4 releases grant
CONTROL stable requesters: max bank grants in any physical cycle=1
REPRO B16 replacement target: pending tag=1, reprobe after unrelated fill=0; original ft_access invariant is false
```

Optional expected-failure invocation:

```sh
ulimit -c 0
./audit-local-build/repro_replacement_target --invoke-original-assert
# Expected SIGABRT (Python subprocess returncode -6; typical shell code 134).
```

The selected/requested role and slot changes are supplied by source-derived fixture schedules; full RO/cache/partition/DRAM timing is not instantiated. The Tag-probe fixture models the source's fill-status/last-access behavior and explicitly invokes the original pending-target assertion; it does not compile `ft_access` itself. Therefore these are deterministic local counterexamples, not claims that a particular application has already failed.

Remote files at `95e886431edceea809ddf560468505c07f02be8a` were independently read back and matched byte-for-byte via Git blob hashes to the standalone sources compiled locally:

- `repro_bank_retry.cpp`: `432a1ab455e2976a60a5d681eb6b80be0659d639`
- `repro_replacement_target.cpp`: `5b263077ddd9eeb42f073da981d4c4037ce54981`

The delivered local source ZIP additionally contains an unchanged full Ideal reference header (upstream blob `41da8ec3dfc7a27f2e1c55ff0a4f37d5d03513e6`), its actual passing sanitizer test, all extracted functions and scaffolding, `run_tests.py`, `SOURCE_LOCK.json`, exact logs, and the longer Chinese audit report. This repository pack is sufficient to reproduce the three blocking cases; the full official 21-case and independent eleven-gate validations are still required after repair.

No defect is repaired by these files. Do not patch the live Core, remove an assertion or clear all bank grants merely to make the fixture green. Apply the ownership/retry fix in the owning Lane's isolated source revision and add the corresponding real production-path regression.
