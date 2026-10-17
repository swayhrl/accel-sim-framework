#!/usr/bin/env python3
"""Standalone negative control for the state comparator (exit 1 on mismatch)."""
import json
import sys
from reference_model import subset
try:
    subset(json.load(open(sys.argv[1])),json.load(open(sys.argv[2])))
except (AssertionError, KeyError, ValueError) as e:
    print(str(e));sys.exit(1)
sys.exit(0)
