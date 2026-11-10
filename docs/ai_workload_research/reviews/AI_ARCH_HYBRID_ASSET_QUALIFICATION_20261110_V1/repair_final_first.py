#!/usr/bin/env python3
"""Retry the one fixed range left by a bounded mirror connection timeout."""

from repair_observed_failures import repair

if __name__ == "__main__":
    repair("model.safetensors-00001-of-00002.safetensors", 4983353344, 5117571071)
