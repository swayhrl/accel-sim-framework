#!/usr/bin/env python3
"""Synthetic, no-host-mutation checks for B9's future admission contract."""

from __future__ import annotations


def required_kb(mem_total: int, peak: int = 0, span: int = 0) -> int:
    normal = mem_total // 5 + 4 * 1024 * 1024
    if not peak:
        return normal
    return max(normal, 4 * peak, span + 2 * peak)


def admit(mem_available: int, mem_total: int, swap_in_delta: int, swap_out_delta: int,
          iowait_pct: int, peak: int = 0, span: int = 0) -> bool:
    return (mem_available >= required_kb(mem_total, peak, span) and swap_in_delta == 0 and
            swap_out_delta == 0 and iowait_pct <= 15)


def main() -> None:
    total = 400 * 1024 * 1024
    assert required_kb(total) == 84 * 1024 * 1024
    assert admit(85 * 1024 * 1024, total, 0, 0, 0)
    assert not admit(83 * 1024 * 1024, total, 0, 0, 0)
    assert not admit(200 * 1024 * 1024, total, 1, 0, 0)
    assert not admit(200 * 1024 * 1024, total, 0, 1, 0)
    assert not admit(200 * 1024 * 1024, total, 0, 0, 16)
    assert required_kb(total, peak=32 * 1024 * 1024, span=20 * 1024 * 1024) == 128 * 1024 * 1024
    assert not admit(127 * 1024 * 1024, total, 0, 0, 0, peak=32 * 1024 * 1024, span=20 * 1024 * 1024)
    print("PASS B9 synthetic_resource_gate normal_and_calibrated_cases=7")


if __name__ == "__main__":
    main()
