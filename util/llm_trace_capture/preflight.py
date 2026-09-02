#!/usr/bin/env python3
"""Compatibility alias for the host-only Route-E preflight.

Use host_preflight.py before bootstrap and capture_ready_preflight.py after it.
This alias prevents older notes from accidentally selecting the retired,
combined host-and-tracer check.
"""
from host_preflight import main

if __name__ == "__main__":
    raise SystemExit(main())
