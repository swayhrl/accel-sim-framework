#!/usr/bin/env python3
"""Bind only the actually published C small candidate blobs; no native/runtime calls."""
import hashlib,json,pathlib,shlex,subprocess,datetime
P=pathlib.Path(__file__).resolve().parent
C='93f6db1881bb7bbb59f5e7f53196b7441ef3268b'
CP='docs/ep_l2/review_packs/MS20261021_C_SGEMM_FALLBACK_BFS_HOST_r1/'
def sha(b):return hashlib.sha256(b).hexdigest()
def get(path,expected):
 b=subprocess.check_output(['git','show',C+':'+path]);assert len(b)<1024*1024 and sha(b)==expected;return b

def save(n,d):(P/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')

def opts(paths):
 d={}
 for p in paths:
  ts=shlex.split(p.read_text(),comments=True);assert len(ts)%2==0
  d.update(zip(ts[::2],ts[1::2]))
 return d
packet_raw=get(CP+'CANDIDATE_PACKET.json','ad83a54b2b8584084c21e99b94fdaae0d839c5e452300e782b38149691cdd21f');packet=json.loads(packet_raw);sg=packet['SGEMM']
assert packet['status']=='PREPARED_NOT_E_QUALIFIED_NOT_ADOPTED' and sg['underlying_RO_opportunity']=='UNKNOWN_NOT_MEASURED_ZERO'
refs=[];copied={};(P/'C_INPUT').mkdir(exist_ok=True)
for source,dest,h in [
 (CP+'CANDIDATE_PACKET.json','CANDIDATE_PACKET.json','ad83a54b2b8584084c21e99b94fdaae0d839c5e452300e782b38149691cdd21f'),
 (sg['candidate_manifest']['path'],'manifest.candidate.json',sg['candidate_manifest']['sha256']),
 (sg['oracle_binding_options']['-gpgpu_ep_l2_ro_ranges'],'certified_ranges.csv',sg['oracle_binding_options']['-gpgpu_ep_l2_ro_ranges_sha256']),
 (CP+'SGEMM_COMMANDLIST.txt','SGEMM_COMMANDLIST.txt','0a0d21711ff3f3de1604fc0a243d5be2df5155147bb09bc4533bd017b62f5913')]:
 raw=get(source,h);target=P/'C_INPUT'/dest
 if target.exists():assert target.read_bytes()==raw
 else:target.write_bytes(raw)
 ref={'repo':'swayhrl/accel-sim-framework','commit':C,'path':source,'sha256':h,'role':'C_published_SGEMM_candidate_not_E_qualification'};refs.append(ref);copied[dest]={'path':str(target),'sha256':h,'bytes':len(raw),'source_ref':ref}
m=json.loads((P/'C_INPUT/manifest.candidate.json').read_text());raw=(P/'C_INPUT/certified_ranges.csv').read_bytes();prop=json.loads((P/'PROPOSAL.json').read_text())
assert raw.splitlines()==[b'first_line,last_line_inclusive']
assert m['status']=='SAFE_FALLBACK_NO_CERTIFIED_LINES' and m['scope']=='NO_READONLY_CERTIFICATION' and m['epoch']=='whole_commandlist'
assert m['address_domain']=='CANONICAL_GPU_GLOBAL_VA_NO_TRANSLATION_ALIAS'
assert m['artifacts']['certified_ranges.csv']==sha(raw)
assert m['commandlist_sha256']==sha((P/'C_INPUT/SGEMM_COMMANDLIST.txt').read_bytes())==prop['input']['trace_manifest'][1]['sha256']
assert m['kernels'][0]['sha256']==prop['input']['trace_manifest'][0]['sha256'] and m['kernel_count']==1
assert sg['proposed_runtime']['core_source_commit']==prop['source_identity']['core_source_commit'] and sg['proposed_runtime']['binary_sha256']==prop['source_identity']['binary_sha256']
assert sg['trace_content_sha256']==prop['input']['trace_content_sha256']
binding={'-gpgpu_ep_l2_ro_ranges':copied['certified_ranges.csv']['path'],'-gpgpu_ep_l2_ro_ranges_sha256':copied['certified_ranges.csv']['sha256'],'-gpgpu_ep_l2_ro_manifest':copied['manifest.candidate.json']['path'],'-gpgpu_ep_l2_ro_manifest_sha256':copied['manifest.candidate.json']['sha256'],'-gpgpu_ep_l2_ro_scope':'NO_READONLY_CERTIFICATION'}
core_opts=opts([P/'CONFIGS/F_MECHANISM_UNSEALED.config']);fraw='# PREPARED_NOT_E_QUALIFIED_NOT_ADOPTED: exact main61 SGEMM full F with published C empty candidate.\n'+''.join(f'{k} {v}\n' for k,v in core_opts.items())+''.join(f'{k} {v}\n' for k,v in binding.items())
(P/'CONFIGS/F.config').write_text(fraw)
paths=[P/'CONFIGS'/n for n in ['base-0.config','base-1.config','base-2.config']];S=opts(paths+[P/'CONFIGS/S.config']);F=opts(paths+[P/'CONFIGS/F.config'])
assert all(F[k]==v for k,v in binding.items()) and F['-gpgpu_ep_l2_ro_tag_detach']==F['-gpgpu_ep_l2_ro_line_mshr_bypass']=='1'
old=json.loads((P/'OPTION_DIFF_AND_INVARIANTS.json').read_text());assert len(F)==154 and len(S)==149
assert {k:v for k,v in F.items() if k not in binding}==old['F_mechanism_effective_options_without_input_binding']
diff={k:{'S':S.get(k),'F':F.get(k)} for k in sorted(set(S)|set(F)) if S.get(k)!=F.get(k)};assert len(diff)==10
old.update(status='PREPARED_BOUND_TO_PUBLISHED_C_NOT_E_QUALIFIED_NOT_ADOPTED',F_profile={'path':str(P/'CONFIGS/F.config'),'sha256':sha(fraw.encode())},F_effective_options=F,complete_option_diff=diff,pending_F_binding_options=[],C_binding_options=binding,raw_identity_note='Exact raw configuration proposal only; E owns final relocation/config/runtime/run key and qualification.')
save('OPTION_DIFF_AND_INVARIANTS.json',old)
cr={'schema':'A2_BYTE_IDENTICAL_PUBLISHED_C_SGEMM_BINDING_V1','status':'PREPARED_NOT_E_QUALIFIED_NOT_ADOPTED','C_publication_commit':C,'source_refs':refs,'copied_artifacts':copied,'bound_options':binding,'candidate_empty_ranges':True,'actual_RO_opportunity':'UNKNOWN_NOT_MEASURED_ZERO','F_WVTM_ON':True,'commandlist_metadata_copy':'Reference only; actual full-input entry remains original trace directory, not this small packet directory','metadata_lineage_note':{'C_manifest_framework_source_commit':m['framework_source_commit'],'runtime_framework_source_commit':prop['source_identity']['framework_source_commit'],'interpretation':'Preserved verbatim C metadata schema/preparation lineage, NOT runtime source identity. C packet proposed_runtime and this proposal bind actual9dd/d010/main61. E independently reviews this explicit distinction; no field rewritten to hide it.'},'E_review_and_adoption_required':True,'bound_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()};save('C_CANDIDATE_BINDING.json',cr)
prop.update(status='PREPARED_NOT_E_QUALIFIED_NOT_ADOPTED',assigned_preparation='DONE',C_fallback_binding='C_CANDIDATE_BINDING.json',F_binding_file='CONFIGS/F.config',complete_F_config_available=True,old_unsealed_mechanism_file='Retained intermediate preparation only; authoritative proposed F is CONFIGS/F.config',shared_auxiliary_assets_for_both_S_and_F=[copied['manifest.candidate.json'],copied['certified_ranges.csv']],input_specific_qualification='PENDING_E_ONLY');save('PROPOSAL.json',prop)
q=json.loads((P/'QUALIFICATION_COVERAGE_MAP.json').read_text());g=q['input_specific_gaps'][0];g['status']='A2_PREPARATION_DONE_ACTUAL_PUBLISHED_C_BOUND_E_REVIEW_PENDING';g['C_candidate_ref']=refs[0];save('QUALIFICATION_COVERAGE_MAP.json',q)
r=json.loads((P/'REFERENCES.json').read_text());r['source_refs']+=refs;save('REFERENCES.json',r)
print(json.dumps({'assigned_preparation':'DONE','status':prop['status'],'S_options':len(S),'F_options':len(F),'option_difference_count':len(diff),'C_original_bytes_preserved':True,'new_build_native_app':0}))
