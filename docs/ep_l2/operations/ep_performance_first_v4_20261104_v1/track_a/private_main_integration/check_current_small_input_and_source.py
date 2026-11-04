from pathlib import Path
import hashlib,json,subprocess,sys
sys.dont_write_bytecode=True
P=Path('/root/data/ep_l2_full_workload_performance_20261027_v1');O=P/'research/performance_first_v4_20261104_v1/track_a/private_main_integration'
g=next(g for g in json.loads((O/'PRIVATE_GRAPH_INDEX.json').read_text())['graphs']if g['lane']==sys.argv[1]);sys.path.insert(0,g['runtime']);import ep_perf_native_wv_modes_draft as e
s=e.read(g['candidate_specs'][0]['path']);proof=e.fresh_input(s);src={}
for name,field in [('core','core_source_commit'),('framework','framework_source_commit')]:
 repo=s['source_worktrees'][name];head=subprocess.check_output(['git','-C',repo,'rev-parse','HEAD'],text=True).strip();dirty=subprocess.check_output(['git','-C',repo,'status','--porcelain','--untracked-files=no'],text=True).strip()
 assert head==s['source_identity'][field]and not dirty
 src[name]=dict(path=repo,HEAD=head,tracked_clean=True)
out=dict(schema='EP_PFV4_SOURCE78_CURRENT_SMALL_INPUT_AND_SOURCE_CHECK_V1',lane=g['lane'],input_identity_sha256=s['input_identity_sha256'],applies_to_cohorts=[json.loads(Path(r['path']).read_text())['cohort']for r in g['candidate_specs']],input_proof=proof,current_Source_worktrees=src,Trace_bodies_read=False,small_whole_commandlist_hashed=True,models_started=0)
(O/'delta_metadata_checks'/(g['lane']+'_CURRENT_INPUT_STORAGE_AND_SOURCE.json')).write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
print(json.dumps(dict(lane=g['lane'],status='PASS',current_members=len(proof['members']),no_large_body_rehash=True,Source_current_clean=True)))

