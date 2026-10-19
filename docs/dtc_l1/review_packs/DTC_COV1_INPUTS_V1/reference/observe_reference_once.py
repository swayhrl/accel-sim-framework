"""SOURCE_PREPARED_NOT_EXECUTED: bounded actual-COV observation rendezvous.

One inherited anonymous-pipe ACK, then the unchanged four tests in this same
Python process. No Popen, sleep, registry, simulation or import-time action.
Only a frozen sole manager may launch/release this separately registered role.
"""
import hashlib
import os
from pathlib import Path
import runpy
import select
import stat
import sys
import time


ACK_ENV = "DTC_COV1_REFERENCE_ACK_FD"
ACK = b"A"
WAIT_SECONDS = 5.0
WORKTREE = Path("/workspace/worktrees/accel-sim-iscas2027-dtc-cov1-inputs-174-v1")
DIRECTORY = WORKTREE / "docs/dtc_l1/review_packs/DTC_COV1_INPUTS_V1/reference"
TEST = DIRECTORY / "test_reference_algorithms.py"
SOURCES = {
    TEST: "26feedbe5a6f519478668fc7f3795fa60d5cc912201763dd03f60a81ca55c607",
    DIRECTORY / "reference_algorithms.py": "44a3775c0221ea71f035ed9d7402d562e64c28c495f9057290e2eb0d651386b0",
}
ENVIRONMENT = {"PATH": "/usr/bin:/bin", "LANG": "C", "LC_ALL": "C",
               "CUDA_VISIBLE_DEVICES": "", "PYTHONDONTWRITEBYTECODE": "1"}


def require(ok, reason):
    if not ok:
        raise RuntimeError(reason)


def check_sources():
    for path, expected in SOURCES.items():
        require(hashlib.sha256(path.read_bytes()).hexdigest() == expected,
                "UNCHANGED_FOUR_TEST_SOURCE_REQUIRED:" + str(path))


def main():
    require(len(sys.argv) == 1 and Path(sys.argv[0]).resolve() == DIRECTORY / "observe_reference_once.py",
            "EXACT_REFERENCE_OBSERVER_ARGV_REQUIRED")
    require(Path.cwd() == WORKTREE, "EXACT_REFERENCE_WORKTREE_CWD_REQUIRED")
    require(sys.flags.ignore_environment == 1 and sys.flags.dont_write_bytecode == 1 and
            sys.flags.isolated == 0, "EXACT_E_B_REFERENCE_FLAGS_REQUIRED")
    require(set(os.environ) == set(ENVIRONMENT) | {ACK_ENV} and
            all(os.environ[key] == value for key, value in ENVIRONMENT.items()),
            "EXACT_CLEAN_REFERENCE_ENVIRONMENT_REQUIRED")
    raw_fd = os.environ[ACK_ENV]
    require(raw_fd.isascii() and raw_fd.isdecimal(), "EXPLICIT_PIPE_FD_REQUIRED")
    fd = int(raw_fd)
    require(3 <= fd <= 2**31 - 1, "INHERITED_NONSTANDARD_PIPE_FD_REQUIRED")
    try:
        require(stat.S_ISFIFO(os.fstat(fd).st_mode), "INHERITED_PIPE_REQUIRED")
        # Nonblocking read prevents a readiness race from extending the bound.
        os.set_blocking(fd, False)
        check_sources()
        deadline = time.monotonic() + WAIT_SECONDS
        ready, _, _ = select.select([fd], [], [], max(0.0, deadline - time.monotonic()))
        require(ready and time.monotonic() <= deadline, "REFERENCE_OBSERVATION_ACK_TIMEOUT")
        value = os.read(fd, 2)
        require(value == ACK and time.monotonic() <= deadline,
                "REFERENCE_OBSERVATION_ACK_EOF_WRONG_BYTE_OR_EXPIRED")
    finally:
        os.close(fd)
        os.environ.pop(ACK_ENV, None)
    check_sources()
    # -E -B script launch retains this fixed source directory on sys.path.
    # runpy preserves one PID/start_ticks and unittest still executes once.
    sys.argv = [str(TEST), "-v"]
    runpy.run_path(str(TEST), run_name="__main__")


if __name__ == "__main__":
    main()
