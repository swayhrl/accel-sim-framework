# M5 execution and reproducibility anchor

Status: **M5.0A PASS**. This is the M5 execution anchor; M5.0E will emit the first formal behavior/timing anchor.

## Parent and branch identity

| Item | SHA | Verification |
| --- | --- | --- |
| Validated Core M1--M4 parent | `cdeec769fd0c1be12b45d58536ecb81074d4b415` | ancestor PASS |
| M5 Core head | `ddb9aac59cd1f6c80d7990b8bb9ec173d4819680` | descendant PASS |
| Validated Framework M1--M4 parent | `56369da33dc5f48fc9ac071fd122fde4b35bd8c9` | ancestor PASS |
| M5 Framework head | `deca81b47623854d849520015b2ac20864080eb7` | descendant PASS |

The dedicated M5 worktrees leave validated M1--M4 branches unchanged.

## Build and runtime identity

- Configure: `cmake -S <M5-core> -B /tmp/dtc-l1-m5-core-build -DCMAKE_BUILD_TYPE=Release -DGPGPUSIM_BUILD_DTC_L1_TESTS=ON`.
- Build: `cmake --build /tmp/dtc-l1-m5-core-build -j 4`.
- Test: `ctest --test-dir /tmp/dtc-l1-m5-core-build --output-on-failure`.
- `dtc_l1_m1_common_test`, `dtc_l1_bad_generation_test`, and `dtc_l1_completion_accounting_test` all PASS.
- Runtime `libcudart.so` SHA-256: `c5710f5ed1fb9e147300baac15c6153e8c9b874a3aea8823606935fe6b51b052`.
- Toolchain: CMake 3.31.7, GCC 11.4.0, CUDA 11.8.89.

## Sentinel differential

The M4 VecAdd binary/PTX was run with M5 runtime and identical configuration except `-gpgpu_dtc_l1_mode`.

| Mode | cycles | dynamic instructions | Result | M4 differential |
| --- | ---: | ---: | --- | --- |
| LEGACY | 5562 | 5376 | PASS | exact cycle match |
| PAPER_BASE | 5708 | 5376 | PASS | new formal Base sentinel |
| PAPER_IO | 5545 | 5376 | PASS | exact cycle match |
| PAPER_OO | 5533 | 5376 | PASS | exact cycle match |

Base lower acquired/released is `64/64` with final outstanding zero. IO and OO drain PIB/inflight/lower state and close `16/16` dependencies; OO active references end at zero. This is a regression sentinel, not a paper performance result.

## Result identity and resume contract

`util/dtc_l1/m5_result_registry.py` keys valid results by `{core_sha, framework_sha, config_sha256, workload_id, workload_sha256, ptx_sha256, input_sha256[], parser_schema}`. The committed registry contains four valid sentinels. Launchers must run `check` before executing and `register` only after strict parsing. A demonstrated Base lookup returns `VALID M5-53d21c0738f6e0f4`.

## Host concurrency calibration

A timed PAPER_BASE VecAdd used 1.16 s user, 0.47 s system, 1.53 s wall, and 385,024 KiB max RSS without swaps. Other host workloads are active and system swap is full, so initial M5 batch concurrency is **one simulator process**. Raise it only after representative Base smoke memory/headroom measurements.
