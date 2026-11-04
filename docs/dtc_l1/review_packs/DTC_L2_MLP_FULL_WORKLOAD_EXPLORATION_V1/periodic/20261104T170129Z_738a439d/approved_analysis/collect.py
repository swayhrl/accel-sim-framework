"""One shot, qualified read-only generator, immutable new output; no Git."""
import sys
sys.dont_write_bytecode=True
import hashlib,importlib.util,json,pathlib,datetime
P=pathlib.Path;A=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1')
R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1');O=A/'agents/E/results_refresh_20261028_v4'
assert not(O/'PRIMARY_SNAPSHOT.json').exists()and not(O/'SUPPLEMENTAL_SNAPSHOT.json').exists()
tool=A/'agents/D/report_v1/build_report.py';expected='9ad9cdf8db29eb062f8053b51b3396a1bac6ff9132f6ad0d89ac64aac58786d7'
assert hashlib.sha256(tool.read_bytes()).hexdigest()==expected
sp=importlib.util.spec_from_file_location('qualified_report',tool);g=importlib.util.module_from_spec(sp);sp.loader.exec_module(g)
d=g.acquire(R,'SOURCE_SHA_CANONICAL_NO_GIT_QUERY')
assert d['planned_cells']==350 and d['frozen_inputs']==35 and not d['uniform_option_errors']
assert all('-V2'not in r['cohort']for fs in d['table'].values()for cs in fs.values()for r in cs.values())
O.mkdir(parents=True,exist_ok=True);(O/'PRIMARY_SNAPSHOT.json').write_bytes(g.encode(d))
sources={};c='E2-DTCL2MLP-6df3a84b612086e8-DH-M16-V2'
result=g.source(R/'analysis'/(c+'.RESULT.json'),sources);spec=g.source(R/'control/specs'/(c+'.json'),sources)
s=dict(schema='SEPARATE_SUPPLEMENTAL_SNAPSHOT_V1',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),result=result,canonical=spec,
 source_snapshots=list(sources.values()),accepted_by_existing_generator=g.accepted(result),primary_matrix_member=False,automatic_union=False,original_negative_replaced=False)
(O/'SUPPLEMENTAL_SNAPSHOT.json').write_bytes(g.encode(s))
print(json.dumps(dict(utc=d['utc'],state_counts=d['state_counts'],R2_cycles=result['cycles'],R2_accepted=s['accepted_by_existing_generator'])))
