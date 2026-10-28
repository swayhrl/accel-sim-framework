"""Strict evidence-only normalization for two explicit EP9dd complete-component schemas.
Never opens trace_entry or declared trace body paths. No actor/registry/controller imports.
"""
import copy,gzip,hashlib,io,json,zlib
from pathlib import Path as P
PARSER_SHA='9545c56336c8fa25cb7af842ce6955bf4e08b41835f9cfea2dcfa9a8a5802c28'
HEADER_SHA='f483cfef7b15d765f737d27d88b5d171231078c09da51cb6da23f1139da141dd'
FRAMEWORK='9dd1ee57a83d83b56b7874bc7c716185ab52c8f7'
SOURCE78={'core_source_commit':'78f4b59e865b136eede74df74c44c210f5b4ca04','framework_source_commit':FRAMEWORK,'vendor_pybind11_commit':'f90c430c3a1ce8f08c09942a5a1c3a797bb2295b','binary_sha256':'78d4e96bb79c776e27146bcf168d7c70cf3897ef9cb84d837d8974fec4c91b8a','archive_sha256':'e5a743a2bb796d82f58109251f43d5c1997d5c1f7fdeac61213416da3835b697'}
SOURCE_DIR=P('/root/data/ep_l2_multiworkload_event_timeline_20261027_v1/framework/gpu-simulator/trace-parser')
LARGE='EP9DD_COMPLETE_LARGE_INPUT_COMPONENT_PROOF_V2';REMAINING='EP9DD_COMPLETE_REMAINING_PRIMARY_INPUT_COMPONENT_PROOF_V1'
IDENTITY_KEYS=('member','path','bytes','sha256','command_ordinal','kernel_ordinal','name','expected_CTA','expected_instructions','expected_binary_version','expected_trace_version')
def need(v,m):
 if not v:raise ValueError(m)
def digest(b):return hashlib.sha256(b).hexdigest()
def positive(v):return type(v)is int and v>0
def ref_identity(r):return {k:r[k]for k in('path','sha256')}
def json_no_duplicate(raw):
 def pairs(items):
  d={}
  for k,v in items:need(k not in d,'duplicate JSON key '+k);d[k]=v
  return d
 return json.loads(raw,object_pairs_hook=pairs)
def verified_bytes(r,max_bytes=8<<20):
 p=P(r['path']);need(p.stat().st_size<=max_bytes,'evidence size cap');b=p.read_bytes();need(digest(b)==r['sha256'],'evidence SHA mismatch '+str(p));return b
def exact(r):return json_no_duplicate(verified_bytes(r))
def gzip_bytes(r):
 # Two existing receipt dialects, with all available stored/logical/CRC fields enforced.
 rr=dict(r);rr['sha256']=r.get('sha256',r.get('stored_sha256'));need(isinstance(rr['sha256'],str),'missing stored SHA')
 stored=verified_bytes(rr);raw=gzip.GzipFile(fileobj=io.BytesIO(stored)).read((8<<20)+1);need(len(raw)<=8<<20,'decoded evidence cap')
 for key in ['stored_bytes']:
  if key in r:need(len(stored)==r[key],'stored evidence length')
 length=r.get('raw_logical_bytes',r.get('raw_bytes'));h=r.get('raw_logical_sha256',r.get('raw_sha256'));need(type(length)is int and isinstance(h,str),'logical evidence identity missing');need(len(raw)==length and digest(raw)==h,'logical gzip SHA/length mismatch')
 if 'raw_crc32'in r:need(zlib.crc32(raw)==r['raw_crc32'],'raw evidence CRC mismatch')
 if 'truncated'in r:need(r['truncated']is False and r['complete_compressed_stream']is True,'truncated evidence')
 return raw
def body_basis_join(m,b):
 mr=ref_identity(m['content_SHA_reuse_basis']);br=ref_identity(b['DTC_complete_body_ref'])
 if mr==br:return dict(kind='EXACT_SAME_BODY_PROOF_REFERENCE',metadata_ref=mr,binding_ref=br)
 need(b['program']=='cutcp'and mr['sha256']=='e13cb2783a8897dd5c5be1804570068673549e0fbc54e82e990d7382cd22f848'and br['sha256']=='0cd5e331892881b54e984437198b0331f7f908d619993a11d598bd1137cdf4f7','unsupported body-proof continuation')
 current=exact(mr);old=exact(br);need(current['schema']=='DTC_CURRENT_SOURCE_FULL_INPUT_FORMAT_ADJUDICATION_V2'and old['schema']=='DTC_SWEEP_FULL_CURRENT_BODY_SHA_QUALIFICATION_V1','exact Cutcp body proof schemas')
 link=current['explicit_current_source_format_adjudication'];need(dict(path=link['original_qualification_path'],sha256=link['original_qualification_sha256'])==br and link['old_HOLD_not_erased']is True and link['performance_acceptance_granted']is False,'explicit backward link / scope')
 for key in ['input_digest','bundle_id','program','expected_commands','expected_instructions','expected_CTA','expected_kernels']:need(current[key]==old[key],'Cutcp same body proof metadata '+key)
 need(current['expected_commands']==b['expectedcommands']and current['expected_instructions']==b['expected_instructions']and current['expected_CTA']==b['expected_CTA'],'Cutcp complete command census')
 need(len(current['rows'])==len(old['rows'])==len(m['ordered_members']),'Cutcp full body continuation population')
 for x,y,z in zip(current['rows'],old['rows'],m['ordered_members']):
  for key in ['ordinal','path','sha256','kernel','binary_version','trace_version','complete_ctas','active_thread_instructions','full_SHA_current_size_mtime']:need(x[key]==y[key],'Cutcp original body identity changed '+key)
  need(x['ordinal']==z['kernel_ordinal']and P(x['path']).name==z['member']and x['sha256']==z['sha256']and x['full_SHA_current_size_mtime'][0]==z['bytes']and x['kernel']==z['name']and x['complete_ctas']==z['expected_CTA']and x['active_thread_instructions']==z['expected_instructions']and x['binary_version']==z['expected_binary_version']and x['trace_version']==z['expected_trace_version'],'Cutcp exact complete member identity continuation')
 return dict(kind='EXACT_CUTCP_BACKWARD_BOUND_BODY_IDENTITY_ONLY',metadata_ref=mr,binding_ref=br,original_DTC_status=old['status'],original_DTC_issues=old['issues'],new_DTC_adjudication_status=current['status'],DTC_adjudication_classification=link['classification'],DTC_adjudication_review_ref=dict(path=link['review_path'],sha256=link['review_sha256']),applicable_domain='Exact same 11 external body identities and actual Framework9dd parser/header fields only; original pending-domain HOLD is retained, EP timing generic-address domain not qualified by this helper',EP_generic_address_timing_semantic_qualification='UNKNOWN_MAIN_SEPARATE_REVIEW_REQUIRED',RO_or_F_permission=False,S_or_WV_application_permission=False,semantic_source_upgrade_granted=False)
def validate_loaded(binding,component,metadata,actual,wire_members,wire_summaries):
 b,c,m,a=binding,component,metadata,actual;schema=c['schema'];need(schema in(LARGE,REMAINING),'unsupported component schema')
 need(c['status']=='ACTUAL_PARSER_FULL_MEMBER_POPULATION_PASS_COMPONENT_ONLY','component not complete pass');need(c['framework_source_commit']==FRAMEWORK and c['source_parser_sha256']==PARSER_SHA and c['source_header_sha256']==HEADER_SHA,'consumer parser/header Source mismatch')
 for k in('scientific_acceptance_granted','application_start_permission'):need(c[k]is False,'component has authority flag')
 need(c['model_starts']==0,'component model start')
 need(c['input_identity_sha256']==b['input_identity_sha256']==m['full_command_identity_sha256'],'mixed input identity');need(c['program']==b['program']==m['program'],'mixed program')
 need(c['trace_entry']==b['trace_entry']==m['canonical_genuine164_trace_entry'],'canonical commandlist path identity');need(c['literal_commandlist_sha256']==b['literal_commandlist_sha256']==m['literal_commandlist_sha256'],'literal commandlist SHA identity')
 need(m['expectedcommands']==b['expectedcommands'],'complete ordered command sequence identity');basis=body_basis_join(m,b)
 ordered=m['ordered_members'];need(len(ordered)==len(b['ordered_kernel_identity'])and ordered,'ordered member population missing')
 need(len({r['member']for r in ordered})==len(ordered),'this finite normalizer requires unique declared member population')
 scopes=b['expected_kernel_scopes'];need(len(scopes)==len(ordered),'complete scopes population')
 for i,(declared,other,scope)in enumerate(zip(ordered,b['ordered_kernel_identity'],scopes)):
  for key in ('member','sha256','bytes','command_ordinal','kernel_ordinal'):need(declared[key]==other[key],'ordered declared identity mismatch: '+key)
  # Remaining-V1 InputBinding stores a compact identity; header/path are separately proven below.
  for key in IDENTITY_KEYS:
   if key in other:need(declared[key]==other[key],'optional complete candidate identity mismatch: '+key)
  need(declared['kernel_ordinal']==i+1,'kernel ordinal/order mismatch');co=declared['command_ordinal'];need(type(co)is int and 0<=co<len(m['expectedcommands'])and m['expectedcommands'][co]==declared['member'],'command ordinal/member mismatch')
  need(positive(declared['bytes'])and positive(declared['expected_CTA'])and positive(declared['expected_instructions']),'positive member census')
  for key,value in [('member',declared['member']),('name',declared['name']),('command_ordinal',co),('kernel_ordinal',i+1),('CTA',declared['expected_CTA']),('instructions',declared['expected_instructions'])]:need(scope[key]==value,'scope/header identity mismatch '+key)
 commands=[(i,x)for i,x in enumerate(m['expectedcommands'])if x.endswith('.traceg')];need(commands==[(x['command_ordinal'],x['member'])for x in ordered],'all commands and declared member order')
 n=len(ordered);need(m['expected_kernels']==n==m['ordered_kernel_launches']==b['expected_kernel_launches']==c['expected_kernel_count'],'kernel population count')
 need(sum(x['expected_CTA']for x in ordered)==m['expected_CTA']==b['expected_CTA'],'total CTA census');need(sum(x['expected_instructions']for x in ordered)==m['expected_instructions']==b['expected_instructions'],'total instruction census')
 members={r['member']:r for r in b['members']if r['member']!='kernelslist.g'};need(len(members)==len([r for r in b['members']if r['member']!='kernelslist.g'])==n,'binding member set population')
 for r in ordered:
  mm=members[r['member']];need(mm['path']==r['path']and mm['sha256']==r['sha256']and mm['size']==r['bytes'],'current binding body identity metadata')
 need(a['status']=='ALL_FINITE_MEMBERS_EP9DD_COMPONENT_PASS_ONLY'and a['returncode']==0 and a['stop_reason']is None and a['hold_members']==0,'actual component incomplete/failed')
 need(a['scientific_acceptance_granted']is False and a['Trace_copies']==0,'actual result authority or copy')
 need(a['member_count']==a['expected_member_count']==n==len(a['members'])==len(wire_members),'actual member census')
 for result_row,wire_row in zip(a['members'],wire_members):
  # Producer postprocessing adds exactly this derived boolean; all original driver fields stay exact.
  need(result_row.get('expected_header_identity_matches')is True,'producer derived header join flag')
  without_derived={k:v for k,v in result_row.items()if k!='expected_header_identity_matches'}
  need(without_derived==wire_row,'actual JSONL rows versus result rows: population/order/all original fields')
 need(a['summary']==wire_summaries and len(wire_summaries)==1,'complete summary population')
 summary=wire_summaries[0];need(summary['summary']is True and summary['status']=='ALL_ACTUAL_EP9DD_PARSE_COMPONENT_COMPATIBLE'and summary['members']==n and summary['hold_members']==0 and summary['total_input_bytes_read']==sum(r['bytes']for r in ordered),'summary complete population')
 if schema==LARGE:
  need(a['schema']=='EP9DD_LARGE_PASSIVE_COMPONENT_RESULT_V1'and a['source_after_sha256']==PARSER_SHA and a['header_after_sha256']==HEADER_SHA,'large actual source identity');need(a['body_hashes_computed']==0 and a['actual_simulator_runs']==0 and a['application_or_launch_permission']is False,'large actual scope')
  need(c['actual_unique_member_population_exact']is True and c['body_hashes_computed']==0 and c['complete_expected_command_count']==len(m['expectedcommands']),'large complete declaration')
  joins=a['input_member_joins'];need(len(joins)==n,'large actual-input join population')
  for i,(r,z)in enumerate(zip(ordered,joins)):
   need(z['actual_member_result_index']==i and z['input_identity_sha256']==b['input_identity_sha256']and z['member']==r['member']and z['path']==r['path']and z['expected_body_sha256_external_not_rehashed']==r['sha256']and z['status']=='EP9DD_ACTUAL_PARSE_COMPONENT_COMPATIBLE','large per-member result-to-input join');need(ref_identity(z['DTC_proof_ref'])==ref_identity(b['DTC_complete_body_ref']),'large DTC reference join')
 else:
  need(a['schema']=='EP9DD_FINITE_PRIMARY_COMPONENT_RESULT_V1'and a['source_parser_sha256']==PARSER_SHA and a['source_header_sha256']==HEADER_SHA,'remaining actual source identity');need(a['input_identity_sha256']==b['input_identity_sha256']and a['program']==b['program'],'remaining actual input');need(a['body_hashes']==0 and a['model_starts']==0 and a['application_start_permission']is False and a['population_exact']is True,'remaining scope')
  need(c['large_body_hashes_computed']==0 and c['every_member_header_grid_and_used_fields_checked']is True,'remaining complete source population')
 normalized=[]
 for r,v in zip(ordered,a['members']):
  need(v['status']=='EP9DD_ACTUAL_PARSE_COMPONENT_COMPATIBLE'and v['issues']=={}and v['first_issues']==[]and v['semantic_domain_issues']=={},'member actual compatibility issue')
  for key in ['actual_parser_fields_equal','expected_header_identity_matches']:
   if key in v:need(v[key]is True,'actual parser/header field mismatch')
  need(v['actual_parser_fields_equal']is True and v['source_parser_modified']is False and v['fresh_body_sha_computed']is False and v['new_scientific_permission']is False,'member parser/scope invariants')
  for key,value in [('program',b['program']),('path',r['path']),('expected_body_sha256_external_not_rehashed',r['sha256']),('kernel',r['name']),('bytes_read',r['bytes']),('complete_ctas',r['expected_CTA']),('active_thread_instructions',r['expected_instructions']),('binary_version',r['expected_binary_version']),('trace_version',r['expected_trace_version'])]:need(v[key]==value,'actual member source/header/body/count join '+key)
  normalized.append(dict(declared_member=copy.deepcopy(r),actual_member=copy.deepcopy(v)))
 return dict(schema='EP9DD_COMPLETE_COMPONENT_NORMALIZED_EVIDENCE_V1',status='STRICT_EVIDENCE_JOIN_PASS_COMPONENT_ONLY_MAIN_REVIEW_REQUIRED',input_identity_sha256=b['input_identity_sha256'],program=b['program'],expectedcommands=copy.deepcopy(m['expectedcommands']),ordered_members=normalized,expected_kernel_count=n,expected_CTA=b['expected_CTA'],expected_instructions=b['expected_instructions'],source_parser_sha256=PARSER_SHA,source_header_sha256=HEADER_SHA,framework_source_commit=FRAMEWORK,original_component_schema=schema,body_reuse_reference_join=basis,checks=dict(complete_commands=True,complete_ordered_declared_identity=True,complete_actual_member_results=True,all_body_identity_external_SHAs_joined_not_rehashed=True,all_headers_and_CTA_instruction_census=True,actual_JSONL_rows_exact_except_rederived_header_join_flag=True,exact_Source_parser_header=True),application_or_launch_permission_granted=False,scientific_acceptance_granted=False,capture_completeness='UNKNOWN',numeric_output='UNKNOWN',body_reads=0,new_body_hashes=0)
def load_evidence(binding_ref,expected_source_identity=None):
 b=exact(binding_ref);need(b['Source5_consumer_identity']==(SOURCE78 if expected_source_identity is None else expected_source_identity),'InputBinding consumer Source5 mismatch');need(b['Source5_consumer_identity']==SOURCE78,'this normalizer qualified only for actual Source78 consumer proof')
 c=exact(b['ep_component_ref']);schema=c['schema'];need(schema in(LARGE,REMAINING),'unsupported explicit component schema')
 ar=c['full_actual_results_ref']if schema==LARGE else c['full_actual_result_ref'];a=json_no_duplicate(gzip_bytes(ar));lr=a['actual_results_ref'];wire=[json_no_duplicate(x)for x in gzip_bytes(lr).splitlines()if x];wm=[x for x in wire if not x.get('summary')];ws=[x for x in wire if x.get('summary')]
 if schema==LARGE:
  mr=c['ordered_member_and_command_metadata_ref'];plan=exact(mr);need(mr['selector']=='selected[0] complete ordered metadata'and len(plan['selected'])==1,'unsupported exact metadata selector');m=plan['selected'][0]
 else:
  mr=c['ordered_declared_metadata_ref'];need(ref_identity(mr)==ref_identity(ar)and mr['selector']=='ordered_declared_metadata; members','remaining exact result metadata selector');m=a['ordered_declared_metadata']
 return b,c,m,a,wm,ws,dict(binding_ref=copy.deepcopy(binding_ref),component_ref=b['ep_component_ref'],ordered_metadata_ref=mr,full_actual_results_ref=ar,original_actual_JSONL_ref=lr)
def normalize_input_component(binding_ref,expected_source_identity=None):
 b,c,m,a,wm,ws,provenance=load_evidence(binding_ref,expected_source_identity)
 for name,wanted in [('trace_parser.cc',PARSER_SHA),('trace_parser.h',HEADER_SHA)]:need(digest((SOURCE_DIR/name).read_bytes())==wanted,'actual unchanged Framework Source file SHA')
 result=validate_loaded(b,c,m,a,wm,ws);result['provenance']=provenance;result['source_file_refs']=[dict(path=str(SOURCE_DIR/name),sha256=value)for name,value in [('trace_parser.cc',PARSER_SHA),('trace_parser.h',HEADER_SHA)]];result['consumer_source_identity']=copy.deepcopy(b['Source5_consumer_identity']);return result
