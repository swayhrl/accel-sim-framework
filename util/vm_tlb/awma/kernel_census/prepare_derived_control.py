#!/usr/bin/env python3
"""Materialize a declared deterministic prefix control; never retokenizes text."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('--source', type=Path, required=True)
p.add_argument('--source-sha256', required=True)
p.add_argument('--length', type=int, required=True)
p.add_argument('--out', type=Path, required=True)
a = p.parse_args()
if hashlib.sha256(a.source.read_bytes()).hexdigest() != a.source_sha256:
    raise SystemExit('source authority mismatch')
ids = json.loads(a.source.read_text())
if not isinstance(ids, list) or len(ids) < a.length:
    raise SystemExit('source cannot supply requested deterministic prefix')
a.out.parent.mkdir(parents=True, exist_ok=True)
a.out.write_text(json.dumps(ids[:a.length], separators=(',', ':')) + '\n')
print(json.dumps({'classification':'DERIVED_CONTROL','derivation':'first_N_tokens_of_accepted_S2_token_stream','source_sha256':a.source_sha256,'length':a.length,'output_sha256':hashlib.sha256(a.out.read_bytes()).hexdigest()}, sort_keys=True))
