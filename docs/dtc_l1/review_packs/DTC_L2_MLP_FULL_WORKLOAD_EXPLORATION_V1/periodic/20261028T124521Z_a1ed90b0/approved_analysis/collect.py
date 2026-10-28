"""One-shot read-only acquisition through the existing qualified generator."""
import sys
sys.dont_write_bytecode=True
import hashlib,importlib.util,json,pathlib,datetime
P=pathlib.Path
A=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1')
R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1');O=A/'agents/E/results_refresh_20261028_v1'
tool=A/'agents/D/report_v1/build_report.py'
expected='9ad9cdf8db29eb062f8053b51b3396a1bac6ff9132f6ad0d89ac64aac58786d7'
assert hashlib.sha256(tool.read_bytes()).hexdigest()==expected
spec=importlib.util.spec_from_file_location('qualified_existing_report',tool);g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
report=g.acquire(R,'2b545e7f54b0111a17c1ee1e5d124bd9acf1ee3d')
assert report['planned_cells']==350 and report['frozen_inputs']==35 and not report['uniform_option_errors']
assert all('-V2' not in r['cohort']for fs in report['table'].values()for cs in fs.values()for r in cs.values())
O.mkdir(parents=True,exist_ok=True)
(O/'PRIMARY_SNAPSHOT.json').write_bytes(g.encode(report))
sources={};C='E2-DTCL2MLP-6df3a84b612086e8-DH-M16-V2'
result=g.source(R/'analysis'/(C+'.RESULT.json'),sources)
canonical=g.source(R/'control/specs'/(C+'.json'),sources)
supp=dict(schema='SEPARATE_SUPPLEMENTAL_SNAPSHOT_V1',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
 cohort=C,result=result,canonical=canonical,source_snapshots=list(sources.values()),
 accepted_by_existing_generator=g.accepted(result),primary_matrix_member=False,automatic_union=False,
 original_negative_replaced=False,source_generator_sha256=expected)
(O/'SUPPLEMENTAL_SNAPSHOT.json').write_bytes(g.encode(supp))
print(json.dumps(dict(utc=report['utc'],state_counts=report['state_counts'],supplemental_accepted=supp['accepted_by_existing_generator'],supplemental_cycles=result.get('cycles'))))
