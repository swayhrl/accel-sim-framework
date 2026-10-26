from pathlib import Path
import os,json,hashlib,importlib.util,copy,collections,re
allowed=sorted(os.sched_getaffinity(0));os.sched_setaffinity(0,set(allowed[:2]))
OUT=Path('/root/share/mnt164/huangrulin/traces/receipts/rtx4080_specialist_adaptation_20261026_v1/isa_return_prepare')
IN=OUT.parent/'profile_input_prepare'
MAPBASE=Path('/root/share/mnt164/huangrulin/traces/rtx4080_sm89/bulk_20261024_v1/private_candidates/specialist_mapper_repair_20261026_v1/fresh_maps_v1')
def canon(x):return(json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode()
def sha(raw):return hashlib.sha256(raw).hexdigest()
def ref(p):raw=p.read_bytes();return dict(path=str(p),sha256=sha(raw),bytes=len(raw))
def put(name,x):p=OUT/name;p.write_bytes(canon(x));return ref(p)
s=importlib.util.spec_from_file_location('candidate',OUT/'isa_control_candidate_v1.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
ledgerpath=IN/'EXACT161_PROFILE_INPUT_GAP_LEDGER_V2.json';ledger=json.loads(ledgerpath.read_bytes())
assert len(ledger['rows'])==161
keyset=['50fad6fdc65b005af1384c83a1b825df405f7b894ed649b98ee145a0b7cd01d1','99297b4fc7c51701fe4063fd0c8e909d9f81bc9683e0a9f2c6366b08492764af','beb96cde3e5f2a10319454ef64da1ba9a2b828144eb254baf986f440ffb016ee']
source=Path('/root/data/ada_native_extensions_stage4_20261024_v1/evidence/attempts/jit_compute70_full_capture_v8_attempt2/TOOL_SOURCES/ada_semantics.h')
assert ref(source)['sha256']=='3177287d1e550d3e4c5d4c558c8d18c67f6c07cb82941378ae9def5fcb320cde'
snap=OUT/'frozen_old_ada_semantics_3177287d.h';snap.write_bytes(source.read_bytes())
consumer=Path('/root/data/ada_trace_extensions_v8_20261024_v1/consumer/trace-parser/trace_parser.cc')
(OUT/'frozen_control_parser_source.cc').write_bytes(consumer.read_bytes())
selected=[];old_indirect_risk=[];classifications=collections.Counter()
for key in keyset:
 root=MAPBASE/key;manifest=json.loads((root/'manifest.json').read_bytes())
 match=next(r for r in ledger['rows']if(r.get('fresh67_cpu_static_evidence')or{}).get('sha256')==key)
 assert ref(root/'manifest.json')['sha256']==match['fresh67_cpu_static_evidence']['manifest_sha256']
 assert manifest['binary_sha256']==key
 pcs=collections.defaultdict(set)
 for row in manifest['instructions']:pcs[row['function']].add(row['pc'])
 controls=[]
 for row in manifest['instructions']:
  text=row['sass'];tok=text.split();opcode=tok[1]if tok[0].startswith('@')else tok[0]
  if not opcode.startswith(('CALL','RET')):continue
  owner=key+'::'+row['function'];out=dict(row)
  try:
   plan=m.control_plan(text,row['src'],row['dst'],owner,pcs[row['function']])
   out.update(candidate_classification='STATIC_SUBSET_PARSE_CANDIDATE_ONLY',plan=plan)
   classifications[plan['kind']]+=1
  except m.Unsupported as e:out.update(candidate_classification='FAIL_CLOSED_OUTSIDE_SUBSET',reason=str(e));classifications[str(e)]+=1
  if opcode=='CALL.REL.NOINC'and re.search(r'\bR\d+\s+0x',text):
   oldtarget=m.old_call_target_candidate(text)
   old_indirect_risk.append(dict(binary_sha256=key,function=row['function'],pc=row['pc'],sass=text,PLR_src=row['src'],PLR_dst=row['dst'],old_regex_static_target=oldtarget,old_branch_clears_src_and_dst_by_source=True,actual_old_GPU_trace_corruption_proven=False))
  controls.append(out)
 selected.append(dict(binary_sha256=key,manifest_ref=ref(root/'manifest.json'),PLR_refs=[ref(p)for p in root.glob('*.liveness')],semantic_map_ref=ref(root/'semantic-map.tsv'),actual_loaded_qualification=False,control_sites=controls))
realref=put('REAL_THREE_IMAGE_CONTROL_STATIC_AUDIT_V1.json',dict(schema='CPU_ONLY_THREE_SELECTED_STATIC_CONTROL_MAP_AUDIT',ledger_ref=ref(ledgerpath),selected_binary_count=3,no_large_asset_rescan=True,selected=selected,static_classification_counts=dict(classifications),old_helper_indirect_operand_risk_sites=old_indirect_risk,ordinary55_boundary='Existing ordinary static profile rejects CALL/RET; this task does not enable or run it',GPU_or_consumer_application_qualification_granted=False))
# Positive and negative grammar/arithmetic/fixture checks.
tests=[];pcset={0x280,0x290,0x2e0,0x2f0,0x960};owner='fixture_sha::owner';base=0x123456780000
def pos(name,fn):
 result=fn();tests.append(dict(name=name,status='PASS_CPU_ONLY'));return result
def neg(name,fn):
 try:fn()
 except m.Unsupported as e:tests.append(dict(name=name,status='REFUSED_AS_REQUIRED_CPU_ONLY',reason=str(e)));return
 raise AssertionError('unexpected acceptance '+name)
call=pos('direct_numeric_CALL_exact',lambda:m.control_plan('CALL.REL.NOINC 0x2f0',[0,1],[0,3],owner,pcset))
ret=pos('RET_preserves_full_GPR_pair',lambda:m.control_plan('RET.REL.NODEC R6 0x0',[6,7],[],owner,pcset));assert ret['physical_src']==[6,7]
pred=pos('predicate_token_separate_from_ABI_summary',lambda:m.control_plan('@!P2 CALL.REL.NOINC 0x2f0',[0,1,322],[0],owner,pcset));assert pred['physical_src']==[322]and pred['guard_negated']
pos('uniform_predicate_namespace',lambda:m.control_plan('@UP1 CALL.REL.NOINC 0x2f0',[0,329],[0],owner,pcset))
pos('RET_pair_upper_supported_boundary252',lambda:m.control_plan('RET.REL.NODEC R252 0x0',[252,253],[],owner,pcset))
for name,text,src,dst in [
 ('first_hex_not_register_target','CALL.REL.NOINC R8 0x0',[0,1,8,9],[0,3]),
 ('nonzero_anchor_indirect_not_direct','CALL.REL.NOINC R8 0x2f0',[0,1,8,9],[0]),
 ('ABS_pair_stays_unsupported','CALL.ABS.NOINC R2',[0,1,2,3],[0]),
 ('unknown_CALL_suffix','CALL.REL.INC 0x2f0',[],[]),
 ('unknown_RET_suffix','RET.REL.DEC R6 0x0',[6,7],[]),
 ('target_zero_ambiguity','CALL.REL.NOINC 0x0',[],[]),
 ('cross_owner_target_missing','CALL.REL.NOINC 0x400',[],[]),
 ('unaligned_direct_target','CALL.REL.NOINC 0x2f1',[],[]),
 ('extra_operand_cannot_be_ignored','CALL.REL.NOINC 0x2f0 R8',[],[]),
 ('nonzero_RET_anchor','RET.REL.NODEC R6 0x100',[6,7],[]),
 ('RET_missing_high_dependency','RET.REL.NODEC R6 0x0',[6],[]),
 ('RET_pair_into_RZ','RET.REL.NODEC R254 0x0',[254,255],[]),
 ('RET_odd_pair_outside_subset','RET.REL.NODEC R253 0x0',[253,254],[]),
 ('RET_UREG_outside_subset','RET.REL.NODEC UR6 0x0',[262,263],[]),
 ('RET_unexplained_destination','RET.REL.NODEC R6 0x0',[6,7],[0]),
 ('unknown_predicate_token','@P7 CALL.REL.NOINC 0x2f0',[],[])]:
 neg(name,lambda text=text,src=src,dst=dst:m.control_plan(text,src,dst,owner,pcset))
def complete_fixture():
 o=m.LaneOracle(owner,base,pcset,0x1f)
 o.step(base+0x280,0x1f,0x15,call)
 o.step(base+0x2f0,0x15,0x15)
 o.step(base+0x960,0x15,0x15,ret,{i:(0x290,0)for i in [0,2,4]})
 o.step(base+0x290,0x1f,0x1f)
 o.step(base+0x2e0,0x1f,0x1f,exit=True);o.finish()
pos('full64_owner_PC_predicated_lane_stack_and_terminal_fixture',complete_fixture)
def zero_fixture():
 o=m.LaneOracle(owner,base,pcset,1);o.step(base+0x280,1,0,call);o.step(base+0x960,1,0,ret,{})
 o.step(base+0x2e0,1,1,exit=True);o.finish()
pos('zero_effective_call_return_no_stack_effect',zero_fixture)
def badreturn(high=0,low=0x291):
 o=m.LaneOracle(owner,base,pcset,1);o.step(base+0x280,1,1,call);o.step(base+0x2f0,1,1);o.step(base+0x960,1,1,ret,{0:(low,high)})
neg('return_wrong_low_offset',badreturn)
neg('return_high_half_not_silently_truncated',lambda:badreturn(1,0x290))
def wrongnext():
 o=m.LaneOracle(owner,base,pcset,1);o.step(base+0x280,1,1,call);o.step(base+0x290,1,0)
neg('next_active_predicated_off_still_checks_successor',wrongnext)
neg('uint64_base_target_overflow',lambda:m.checked_add((1<<64)-1,1))
def wrongowner():
 o=m.LaneOracle(owner,base,pcset,1);p=dict(call,owner='other_image::owner');o.step(base+0x280,1,1,p)
neg('cross_image_owner_rejected',wrongowner)
def extrazero():
 o=m.LaneOracle(owner,base,pcset,1);o.step(base+0x960,1,0,ret,{0:(0,0)})
neg('zero_effective_payload_must_empty',extrazero)
# Reproduce exact old regex risk without importing or running NVBit/GPU.
assert old_indirect_risk and all(x['old_regex_static_target']==0 for x in old_indirect_risk)
testref=put('CPU_CONTROL_SUBSET_QUALIFICATION_V1.json',dict(status='PASS_CPU_STATIC_GRAMMAR_AND_SYNTHETIC_CONTROL_CONTRACT_ONLY',candidate_ref=ref(OUT/'isa_control_candidate_v1.py'),tests=tests,tests_count=len(tests),real_static_audit_ref=realref,affinity=list(os.sched_getaffinity(0)),CPU_limit=2,actual_hardware_branch_or_ABI_validation=False,old_helper_risk_sites=len(old_indirect_risk),old_trace_error_claimed=False,source_or_queue_or_scientific_mutation=False,GPU_SIM_109_starts=0))
print(json.dumps(dict(real_static_audit=realref,CPU_tests=testref,tests=len(tests),risk_sites=len(old_indirect_risk),classifications=dict(classifications))))
