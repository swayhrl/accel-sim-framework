#!/usr/bin/env python3
"""Bounded read-only production/input audit; writes only this report directory.
No compiler, simulator, native test, controller import, lease transaction or trace-body scan.
Large trace SHA values are retained evidence, not rehashed here.
"""
import collections, datetime, hashlib, json, pathlib, re, socket, subprocess
A=pathlib.Path('/workspace/worktrees/accel-sim-ep-l2-ms20261019-a-core-v1')
C=pathlib.Path('/workspace/worktrees/gpgpu-sim-ep-l2-ms20261021-a2-large-capacity-v1')
R=pathlib.Path('/workspace/worktrees/accel-sim-ep-l2-ms20261021-a2-large-capacity-runtime-v1')
E=pathlib.Path('/workspace/worktrees/accel-sim-ep-l2-ms20261019-e-eval-v1')
D=pathlib.Path('/workspace/worktrees/accel-sim-ep-l2-ms20261019-d-analysis-v1')
F=pathlib.Path('/workspace/worktrees/accel-sim-ep-l2-ms20261019-f-env-v1')
OUT=pathlib.Path(__file__).resolve().parent
EHEAD='0bb1699f71162963b2a8f061f4ee8c844df47f71'
DHEAD='f93add1ef2e22e5f8b04e1dce7de5b7ddfd15a80'
FHEAD='42846b018dc1f31f42a77ce1642d707195aa9a75'
FW='9dd1ee57a83d83b56b7874bc7c716185ab52c8f7'
CORE='fe7e1fc1e8f40b5c4c6d0f232a528483891389c5'
EP='docs/ep_l2/review_packs/MS20261021_E2_CAPACITY_DIAGNOSTIC_r1/'
DP='docs/ep_l2/mechanism_study_2026_10_19_v1/lane_d/'
refs=[]
def sha(raw):return hashlib.sha256(raw).hexdigest()
def git(root,*args):return subprocess.check_output(['git','-C',str(root),*args])
def pinned(commit,path):
 raw=git(A,'show',commit+':'+path)
 refs.append({'repository':'swayhrl/accel-sim-framework','commit':commit,'path':path,'sha256':sha(raw),'bytes':len(raw)})
 return json.loads(raw) if path.endswith('.json') else raw.decode()
def physical(path):
 path=pathlib.Path(path);h=hashlib.sha256()
 with path.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return {'path':str(path),'sha256':h.hexdigest(),'bytes':path.stat().st_size}
def metadata(path):
 p=pathlib.Path(path);assert p.stat().st_size<2*1024*1024,p
 raw=p.read_bytes();refs.append({'path':str(p),'sha256':sha(raw),'bytes':len(raw)})
 return json.loads(raw)
release=metadata(A/'docs/ep_l2/review_packs/MS20261021_A2_L2_LARGE_CAPACITY_PRODUCER_r1/RELEASE.json')
old=metadata(A/'docs/ep_l2/review_packs/MS20261020_A2_FORMAL_WAD_PRODUCER_RELEASE_r1/RELEASE.json')
inv=pinned(EHEAD,EP+'workload_research_r1/LOCAL_COVERAGE_INVENTORY.json')
survey=pinned(EHEAD,EP+'workload_research_r1/PRIMARY_SOURCE_WORKLOAD_SURVEY.json')
forward=pinned(EHEAD,EP+'workload_research_r1/LANE_FORWARD_MESSAGES.md')
d_status=pinned(DHEAD,DP+'STATUS.md')
da=pinned(DHEAD,DP+'input_suitability_20261020_r1/CANDIDATE_AUDIT.json')
sg=pinned(DHEAD,DP+'input_suitability_20261020_r1/SGEMM_PROPOSAL_TO_E.json')
fwtq=pinned(EHEAD,'docs/ep_l2/review_packs/MS20261020_E2_MAIN61_FWT_FIRST_PAIR_CONTINUATION_r1/FWT_7_21_QUALIFICATION.json')
fwt=metadata('/workspace/ep_l2_ms20261019_e_results/E012_63be0bb4/input_spec.json')
atomic=metadata('/workspace/ep_l2_ms20261019_e_results/E012_63be0bb4/atomic_scope.json')
sem=metadata('/workspace/ep_l2_ms20261019_e_results/E012_63be0bb4/native_input_semantics.json')
replay=pinned(EHEAD,EP+'E_NATIVE_REPLAY_RESULT.json')
# Audit physical source and parser/opcode portability, not runtime PASS inheritance.
assert git(C,'rev-parse','HEAD').decode().strip()==CORE
assert git(R,'rev-parse','HEAD').decode().strip()==FW
source=[]
for n in ['gpu-simulator/trace-parser/trace_parser.cc','gpu-simulator/trace-parser/trace_parser.h','gpu-simulator/trace-driven/trace_driven.cc','gpu-simulator/accel-sim.cc']+['gpu-simulator/ISA_Def/'+x+'_opcode.h' for x in ['kepler','pascal','volta','turing','ampere']]:
 b=(R/n).read_bytes();assert b==git(R,'show',FW+':'+n)
 source.append({'path':str(R/n),'relative_path':n,'commit':FW,'sha256':sha(b),'old_atomic_schema_match':sha(b)==atomic['native_schema_sources'].get(n),'D_opcode_schema_match':sha(b)==da['source_sha256'].get(n)})
assert all(s['old_atomic_schema_match'] for s in source if s['relative_path'] not in ['gpu-simulator/accel-sim.cc','gpu-simulator/trace-driven/trace_driven.cc'])
old_decoder=git(A,'show','9bd17f9db3e8cbbc3fdad7283d1e292918546fd5:gpu-simulator/trace-driven/trace_driven.cc')
new_decoder=(R/'gpu-simulator/trace-driven/trace_driven.cc').read_bytes()
assert new_decoder==old_decoder.replace(b'  std::string opcode1 = opcode_tokens[0];\n',b'  std::string opcode1 = opcode_tokens[0];\n  ep_l2_mq2_ordinary_read = inst_t::ep_l2_plain_ldg(opcode_tokens);\n')
decoder_delta={'old_framework':'9bd17f9db3e8cbbc3fdad7283d1e292918546fd5','current_framework':FW,'only_added_statement':'ep_l2_mq2_ordinary_read = inst_t::ep_l2_plain_ldg(opcode_tokens);','scope':'MQ2 classification field; parser, ISA lookup and address generation unchanged. Reviewed S/F and capacity profiles require MQ2=0. This is property portability only, not runtime qualification.'}
volta=(R/'gpu-simulator/ISA_Def/volta_opcode.h').read_text()
mapkeys=set(re.findall(r'\{"([A-Z0-9_]+)"',volta))
# Saved complete audits enumerate all opcodes; no full trace re-read.
a_fwt=next(x for x in sem['workloads'] if x['workload']=='FWT_7_21')
assert len(a_fwt['files'])==19 and sum(x['all_active_lane_records'] for x in a_fwt['files'])==791609344
native_generator=physical(C/'src/abstract_hardware_model.cc')
assert native_generator['sha256']==sem['core_memory_generator_sha256']
inputs=[]
for name,entry,files,insns,trace_hash in [
 ('FWT_7_21',next(x['entry'] for x in inv['original7'] if x['workload']=='FWT_7_21'),atomic['trace_files'],791609344,'f3695b85379fb762faaf9830bda449e0a5f1e4d3e351774cf33d90850059b460'),
 ('sgemm',sg.get('commandlist_path',next(x for x in da['results'] if x['workload']=='sgemm')['commandlist_path']),next(x for x in da['results'] if x['workload']=='sgemm')['files'],1658916864,sg['trace_content_sha256'])]:
 command=pathlib.Path(entry);cmd=command.read_bytes();assert len(cmd)<65536
 expected_command='9dfd2639f6660bef2feac69405597380835d4d08f1e0bdb9dd9b2022ed1a0f26' if name=='FWT_7_21' else sg['trace_content_manifest'][1]['sha256']
 assert sha(cmd)==expected_command
 commands=cmd.decode().splitlines();kernels=[x for x in commands if x.startswith('kernel')]
 assert len(kernels)==len(files)
 headers=[];ops=collections.Counter()
 for f in files:
  q=command.parent/f['name'];st=q.stat();assert st.st_size==f['bytes']
  with q.open('rb') as body:prefix=body.read(16384)
  text=prefix.decode();header=text.split('#BEGIN_TB',1)[0];md=dict(re.findall(r'^-([^=\n]+?)\s*=\s*(.*)$',header,re.M));md={k.strip():v.strip() for k,v in md.items()}
  assert md['binary version']=='70'
  ops.update(f['opcode_counts'])
  headers.append({'path':str(q),'bytes':st.st_size,'device':st.st_dev,'inode':st.st_ino,'mtime_ns':st.st_mtime_ns,'saved_complete_body_sha256':f['sha256'],'body_rehashed_this_review':False,'bounded_prefix_read_bytes':len(prefix),'metadata':md})
 missing=sorted({op.split('.')[0] for op in ops}-mapkeys);assert not missing,missing
 assert all(f.get('atomic_absence') and f.get('global_atomic_records')==0 and f.get('shared_atomic_records')==0 for f in files)
 inputs.append({'workload':name,'commandlist':str(command),'commandlist_sha256_recomputed':sha(cmd),'commands':commands,'kernel_count':len(kernels),'expected_lane_instructions_from_saved_full_proof':insns,'saved_trace_content_sha256':trace_hash,'body_bytes':sum(x['bytes'] for x in files),'all_saved_opcodes':dict(ops),'opcode_map_missing':missing,'global_and_shared_atomic_absent_saved_complete_proof':True,'physical_headers_and_stat':headers,'grammar_evidence':'saved full original-byte proof plus exact unchanged Framework parser/ISA and unchanged Core memory generator; not new runtime qualification'})
artifacts=[]
for ref in [release['identity']['main'],release['identity']['archive'],{'path':old['binary_path'],'sha256':old['binary_sha256']},old['production_archive']]:
 actual=physical(ref['path']);assert actual['sha256']==ref['sha256'];artifacts.append(actual)
# Central authority is read ONLY. Store reviewed nested qualification identities, not a new Q.
registry_path=pathlib.Path('/workspace/ep_l2_ft20261016_shared/RUN_REGISTRY.json')
raw=registry_path.read_bytes();reg=json.loads(raw);m=reg['mechanism_study_20261019_v1'];qs=[]
for key,item in m['qualifications'].items():
 q=item.get('qualification',{});qs.append({'qualification_id':key,'path':item.get('path'),'source_identity':q.get('source_identity'),'input_selection_id':q.get('input_selection_id'),'supported_profiles':list(q.get('supported_profiles',{})),'status':q.get('status')})
current=[q for q in qs if q['source_identity'] and q['source_identity'].get('binary_sha256')==release['identity']['main']['sha256']]
assert current and all(set(q['supported_profiles'])<={'S','S_L2_DATA_FREE_LARGE_CAPACITY'} for q in current)
fwttarget=[q for q in current if q['input_selection_id']=='D_V1_FWT_7_21'];assert not fwttarget
candidates_scope={'D_HEAD':DHEAD,'F_HEAD':FHEAD,'E_HEAD':EHEAD,'no_new_F_D_input_package_in_fetched_HEADs':True,'D_present_untracked_preserved':git(D,'status','--porcelain').decode(),'F_worktree_status':git(F,'status','--porcelain').decode(),'authoritative_candidate_intent':'E forward directive: FWT_7_21, SGEMM medium, then D-selected authentic irregular/iterative inputs. External names have no frozen local input package in this reviewed handoff.'}
result={'schema':'A2_DF_EXISTING_PRODUCER_COMPATIBILITY_READONLY_AUDIT_V1','observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'host':socket.gethostname(),'status':'REVIEW_COMPLETE_NOT_E_QUALIFICATION','candidate_scope':candidates_scope,'frozen_new_producer':release['identity'],'old_main61':{'core':'d010911e3174a3764791183cd108fe4664ba8731','framework':FW,'main_sha256':old['binary_sha256'],'archive':old['production_archive']},'physical_artifacts_verified':artifacts,'Framework_parser_and_ISA_bindings':source,'Core_unchanged_memory_generator':native_generator,'old_proof_decoder_delta_review':decoder_delta,'input_reviews':inputs,'FWT_old_qualification':{'identity':fwtq['source_identity'],'profiles':list(fwtq['supported_profiles']),'status':fwtq['status'],'app_history':'E011/E012 INCOMPLETE; no accepted full result or inferred exit0'},'E_current_native_cases':[(x['case_id'],x['actual_exit']) for x in replay['cases']],'central_read_only_snapshot':{'path':str(registry_path),'read_sha256':sha(raw),'actual_starts':m['actual_starts'],'controller':m['controller'],'current_binary_qualifications':current,'all_qualification_summary':qs,'exploratory_input_registrations':m.get('exploratory_input_registrations'),'policy':'No registry/runner/Q mutations or inferred authorization'},'evidence_references':refs,'work_done':{'new_compiles':0,'new_native_invocations':0,'new_app_starts':0,'new_mechanisms':0,'trace_full_scans':0,'E_registry_mutations':0},'qualification_boundary':'Unchanged parser/opcode/full-byte properties may be reviewed and rebound. Old runtime/native/application PASS does not transfer across Core/main identity. Capacity OFF/ON tests/qualifications do not qualify unified F or any new input.'}
(OUT/'AUDIT.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({'status':result['status'],'inputs':[(x['workload'],x['kernel_count'],len(x['all_saved_opcodes']),x['opcode_map_missing']) for x in inputs],'actual_artifact_sha_checks':len(artifacts),'E_current_binary_Q':len(current),'E_current_binary_F_Q':sum('F' in q['supported_profiles'] for q in current),'application_starts_this_audit':0}))
