# AWMA 174 Translation Frontend V1 — Accepted CUDA Toolchain Recovery Addendum

Date: 2026-09-22

Applies to:

`AWMA_TRANSLATION_FRONTEND_PIPELINING_RECALIBRATION_V1`

Blocker classification:

`ENGINEERING_TOOLCHAIN_RECOVERY / NO_SCIENTIFIC_CONTRACT_CHANGE`

## 1. Accepted historical toolchain authority

The repository already contains an accepted 174 build-toolchain receipt:

```text
CUDA nvcc = 12.4.131
accepted archive SHA256 =
7ffba1ada0e4b8c17e451ac7a60d386aa2642ecd08d71202a0b100c98bd74681

gcc/g++ = 11.4.0
GNU ld = 2.38
```

Historical execution context states the CUDA/compiler dependencies were
installed privately under an isolated worktree `.awma_runtime`, not
system-wide.

Therefore this stage is authorized to recover the same accepted toolchain.
This is not a new scientific environment.

## 2. Recovery priority

### R0 — search existing accepted private artifacts first

Before downloading anything, search bounded historical locations for:

- the exact nvcc archive with the accepted SHA256;
- an extracted private CUDA 12.4.131 tree;
- historical `.awma_runtime` build/toolchain directories;
- node164 durable toolchain/build artifacts if any.

Search roots may include current/old 174 worktrees and the AWMA node164
namespace.

If an archive candidate is found, admit it only after:

`sha256sum == 7ffba1ada0e4b8c17e451ac7a60d386aa2642ecd08d71202a0b100c98bd74681`

Do not trust filenames alone.

### R1 — official exact-archive recovery

If R0 finds no accepted artifact, downloading the exact NVIDIA redistribution
archive is authorized:

`cuda_nvcc-linux-x86_64-12.4.131-archive.tar.xz`

The downloaded file MUST match the accepted SHA256 above before extraction.

A hash mismatch is a hard engineering stop.

Install/extract only below the candidate staging/private `.awma_runtime`
namespace.

Do not use apt/system CUDA installation.

Do not modify the NVIDIA driver.

Do not create a persistent host-level `/bin/nvcc` or
`/usr/local/cuda` symlink.

## 3. Explain the current /bin/nvcc path before changing it

The checked-in Framework build uses `CUDA_INSTALL_PATH` for CUDA include and
nvcc discovery.

Before editing anything:

1. grep the candidate staging/build tree for the exact `/bin/nvcc` reference;
2. identify whether it is:
   - generated because `CUDA_INSTALL_PATH` was empty;
   - cached from an earlier configure/makedepend step;
   - literal source/build-script hardcoding.

Record:

`NVCC_PATH_ORIGIN.md`

## 4. Preferred path repair

If `/bin/nvcc` arose from an empty/cached `CUDA_INSTALL_PATH`:

- set `CUDA_INSTALL_PATH=<private accepted CUDA root>`;
- verify `$CUDA_INSTALL_PATH/bin/nvcc --version` reports 12.4 / V12.4.131;
- remove only generated candidate build/cache/dependency products that contain
  the stale absolute path;
- regenerate/reconfigure the candidate build;
- do not edit simulator semantic source.

This is the preferred route.

## 5. Fallback build-plumbing repair

Only if source/build plumbing literally hardcodes `/bin/nvcc` and cannot be
regenerated from `CUDA_INSTALL_PATH`:

- make the smallest build-only path repair required to consume the private
  accepted nvcc;
- label it `BUILD_ONLY_TOOLCHAIN_PATH_REPAIR`;
- keep it separate from candidate simulator semantic changes;
- show a diff proving it changes compiler path selection only;
- do not create a system-wide compiler alias.

Generated Makefiles should not be hand-edited if a source/configuration-level
path exists.

## 6. Dependency/version audit

Before candidate compile, record:

- nvcc version and binary path;
- accepted archive SHA256;
- gcc/g++ version;
- GNU ld version;
- m4/bison/flex/zlib versions or private dependency paths actually used;
- relevant PATH, CUDA_INSTALL_PATH and LD_LIBRARY_PATH;
- candidate source SHA / baseline source SHA.

If an additional CUDA redistribution component is genuinely required for
headers/build support, use the CUDA 12.4.1 family only, bind its official
artifact/version/hash in the build receipt, and do not silently mix another
CUDA release.

A need for a different compiler major/minor release requires STOP for review.

## 7. Build qualification before science

After toolchain recovery:

1. compile legacy mode and candidate mode from the same isolated source/staging;
2. run directed/unit tests first;
3. run legacy reproduction/neutrality before candidate scientific replays;
4. require exact accepted legacy behavior within the declared test contract.

No candidate T0/T1/T2 replay may begin merely because compilation succeeds.

## 8. Publication evidence

Create/update:

- `TOOLCHAIN_RECOVERY_RECEIPT.md`;
- `NVCC_PATH_ORIGIN.md`;
- `BUILD_TOOLCHAIN_ENV.tsv`;
- build log hash;
- candidate/legacy binary hash;
- build-only path repair diff if any.

Then continue the existing Frontend Pipelining V1 Goal.

No new architecture mechanism is authorized.
