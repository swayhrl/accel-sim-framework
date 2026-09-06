#!/usr/bin/env python3
"""No-GPU unit test for the source-copy-only GESUMMV accumulator repair."""
import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location("repair",Path(__file__).with_name("prepare_m5_gesummv_source.py"));repair=importlib.util.module_from_spec(spec);spec.loader.exec_module(repair)
sample="before\n"+repair.OLD_TMP+"\nmid\n"+repair.OLD_Y+"\nafter\n"
fixed=repair.repair(sample)
assert repair.OLD_TMP not in fixed and repair.OLD_Y not in fixed
assert fixed.count(repair.NEW_TMP)==1 and fixed.count(repair.NEW_Y)==1
for bad in ("", repair.OLD_TMP, repair.OLD_TMP+"\n"+repair.OLD_TMP+"\n"+repair.OLD_Y):
 try: repair.repair(bad)
 except RuntimeError: pass
 else: raise AssertionError("unexpected source shape accepted")
print("PASS GESUMMV source-copy repair: exact zero-accumulator transform only")
