#!/usr/bin/env python3
"""Read-only topology-aware CPU candidate selection for immutable FAST64 R2."""
from __future__ import annotations

import argparse
import collections
import os
import pathlib
import subprocess
import sys


def expand_cpu_list(value: str) -> set[int]:
    result: set[int] = set()
    for part in value.strip().split(","):
        if not part:
            continue
        if "-" in part:
            lo, hi = part.split("-", 1)
            result.update(range(int(lo), int(hi) + 1))
        else:
            result.add(int(part))
    return result


def field(path: pathlib.Path, name: str) -> str:
    for line in path.read_text(errors="replace").splitlines():
        if line.startswith(name + ":"):
            return line.split(":", 1)[1].strip()
    return ""


def topology() -> dict[int, tuple[int, int, int]]:
    output = subprocess.check_output(
        ["lscpu", "-p=CPU,CORE,SOCKET,NODE"], text=True
    )
    result: dict[int, tuple[int, int, int]] = {}
    for line in output.splitlines():
        if not line or line.startswith("#"):
            continue
        cpu, core, socket, node = map(int, line.split(","))
        result[cpu] = (core, socket, node)
    return result


def live_simulator_affinity(proc_root: pathlib.Path) -> tuple[set[int], int, int]:
    hard: set[int] = set()
    narrow = broad = 0
    for proc in proc_root.glob("[0-9]*"):
        try:
            cmdline = (proc / "cmdline").read_bytes().replace(b"\0", b" ")
            if b"accel-sim.out" not in cmdline:
                continue
            allowed = expand_cpu_list(field(proc / "status", "Cpus_allowed_list"))
        except (FileNotFoundError, PermissionError, ValueError):
            continue
        # A singleton or small taskset/cpuset is a hard reservation.  A broad
        # affinity (e.g. 0-511) is only a throughput input and must not reserve
        # every CPU it could migrate to.
        if 0 < len(allowed) <= 4:
            hard.update(allowed)
            narrow += 1
        else:
            broad += 1
    return hard, narrow, broad


def scheduler_occupancy() -> collections.Counter[int]:
    output = subprocess.check_output(["ps", "-e", "-o", "psr="], text=True)
    result: collections.Counter[int] = collections.Counter()
    for value in output.split():
        if value.isdigit():
            result[int(value)] += 1
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--proc-root", default=os.environ.get("FAST64_PROC_ROOT", "/proc"))
    parser.add_argument("--format", choices=("tsv", "cpus"), default="tsv")
    args = parser.parse_args()
    proc_root = pathlib.Path(args.proc_root)
    if not proc_root.is_absolute():
        raise SystemExit("FAST64_PROC_ROOT_MUST_BE_ABSOLUTE")

    topo = topology()
    allowed = expand_cpu_list(pathlib.Path("/sys/fs/cgroup/cpuset.cpus.effective").read_text())
    hard_cpus, narrow_workers, broad_workers = live_simulator_affinity(proc_root)
    hard_cores = {(topo[cpu][1], topo[cpu][0]) for cpu in hard_cpus if cpu in topo}
    occupancy = scheduler_occupancy() if proc_root == pathlib.Path("/proc") else collections.Counter()

    # Keep one representative logical CPU for each physical core and avoid a
    # sibling/core touched by a hard-pinned simulator.  Rank only by current
    # scheduler occupancy then CPU number; broad-affinity processes are not
    # excluded, exactly as required by the FAST64 host-policy authority.
    test_candidates = os.environ.get("FAST64_CPU_CANDIDATES")
    if test_candidates:
        # Synthetic selector tests use a finite candidate domain; production
        # always derives its domain from lscpu/cpuset above.
        candidates = sorted(
            (cpu for cpu in expand_cpu_list(test_candidates) if cpu in allowed and cpu not in hard_cpus),
            key=lambda cpu: (occupancy[cpu], cpu),
        )
    else:
        representatives: dict[tuple[int, int], list[int]] = collections.defaultdict(list)
        for cpu, (core, socket, _node) in topo.items():
            if cpu in allowed:
                representatives[(socket, core)].append(cpu)
        candidates = []
        for core_key, cpus in representatives.items():
            if core_key in hard_cores:
                continue
            candidates.append(min(cpus, key=lambda cpu: (occupancy[cpu], cpu)))
        candidates.sort(key=lambda cpu: (occupancy[cpu], cpu))

    if args.format == "cpus":
        print(",".join(map(str, candidates)))
        return 0
    print("schema\tFAST64_R2_CPU_SELECTION_V1")
    print(f"topology_source\tlscpu -p=CPU,CORE,SOCKET,NODE")
    print(f"cpuset_effective\t{pathlib.Path('/sys/fs/cgroup/cpuset.cpus.effective').read_text().strip()}")
    print(f"hard_pinned_cpu_count\t{len(hard_cpus)}")
    print(f"narrow_affinity_simulator_count\t{narrow_workers}")
    print(f"broad_affinity_simulator_count\t{broad_workers}")
    print(f"available_distinct_physical_cores\t{len(candidates)}")
    print(f"candidate_cpus\t{','.join(map(str, candidates))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
