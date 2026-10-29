"""One-time read-only acquisition; writes only this new analysis directory."""
import sys
sys.dont_write_bytecode=True
import pathlib, hashlib, importlib.util, json, shutil
A=pathlib.Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1')
R=pathlib.Path('/root/data/dtc_l2_mlp_exploration_20261027_v1')
O=A/'agents/L/current_performance_report_20261029_v1'
assert not (O/'PRIMARY_SNAPSHOT.json').exists()
tool=A/'agents/D/report_v1/build_report.py'
assert hashlib.sha256(tool.read_bytes()).hexdigest()=='9ad9cdf8db29eb062f8053b51b3396a1bac6ff9132f6ad0d89ac64aac58786d7'
spec=importlib.util.spec_from_file_location('qualified',tool);g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
d=g.acquire(R,'SOURCE_SHA_CANONICAL_NO_GIT_QUERY')
assert d['planned_cells']==350 and d['frozen_inputs']==35 and not d['uniform_option_errors']
assert all('-V2' not in r['cohort'] and '-IR' not in r['cohort'] for fs in d['table'].values() for cs in fs.values() for r in cs.values())
O.mkdir(parents=True,exist_ok=True)
(O/'PRIMARY_SNAPSHOT.json').write_bytes(g.encode(d))
for src,name in [(A/'agents/E/results_refresh_20261028_v4/EVIDENCE.json','ANCHOR_EVIDENCE.json'),(A/'agents/B/adaptive_next_stage_preparation_v1/PAIRED_FACTOR_EVIDENCE.json','ANCHOR_PAIRED_FACTOR.json')]:shutil.copyfile(src,O/name)
shutil.copyfile(tool,O/'qualified_generator.source.py')
print(json.dumps({'utc':d['utc'],'states':d['state_counts'],'planned':d['planned_cells']}))
try:
 import matplotlib
 print('matplotlib='+matplotlib.__version__)
except ImportError: print('matplotlib unavailable')
