import pathlib,json,importlib.util,os
ROOT=pathlib.Path('/root/data/shared_rtx4080_trace_library_20261024_v1/control' )
s=importlib.util.spec_from_file_location('actual_common',ROOT/'stencil768_common_v2.py');a=importlib.util.module_from_spec(s);s.loader.exec_module(a)
SCAN=a.SCAN;LIMIT=a.LIMIT
WORK=pathlib.Path('/root/data/shared_rtx4080_trace_library_20261024_v1/stencil768_private_qualification_A3/startup_journal_failure/ORD_LATE_stencil_c3e987b033b4_A002_CPU_ADOPT_V2_post_epoch4_single768')
F=pathlib.Path('/root/data/shared_rtx4080_trace_library_20261024_v1/stencil768_private_qualification_A3/startup_journal_failure/control/FAKE_FOREIGN_GROWTH')
def epoch_native_usage():
 return {'total_bytes':SCAN.tree_size_race_safe(WORK)if WORK.exists()else 0}
def resources(force=False,stage_budget=0,admission=False):
 reserved=14763950080+(2**30 if F.exists()else 0);free=5*2**30+14763950080+2**30+64*2**20+LIMIT+128*2**20;used=SCAN.tree_size_race_safe(WORK)if WORK.exists()else 0;p=a.policy(free,reserved,used,stage_budget,admission);assert p['PASS'],('injected_private_dynamic_floor',p);return {'policy':p,'Native_free':free,'authority':{'sum_all_records_reserved_write_bytes':reserved},'fixture_only':True}
