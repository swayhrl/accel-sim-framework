#!/usr/bin/env python3
"""Repair final observed failed 128 MiB range after primary pool exit."""

from repair_observed_failures import repair

if __name__ == "__main__":
    repair("model.safetensors-00002-of-00002.safetensors", 3767803904, 3902021631)
