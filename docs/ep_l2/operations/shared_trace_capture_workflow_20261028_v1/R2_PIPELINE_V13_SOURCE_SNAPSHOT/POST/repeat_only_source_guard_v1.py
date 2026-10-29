"""Repeat-only capture closed metadata guard. No raw record decode or science qualification."""
from pathlib import Path
import json,os,stat,hashlib,types,re
NB=Path('/root/share/mnt164/huangrulin/traces/rtx4080_sm89/bulk_20261024_v1')
ST=Path('/data/c16/rtx4080_suite_fill_20261024_v1/nas_fast_sc_copy_st_20261029_v2')
RB=Path('/data/c16/rtx4080_suite_fill_20261024_v1/nas_rtx4080')
def need(v,m):
 if not v:raise AssertionError(m)
def metadata_path(p):
 p=Path(p);need(p.is_absolute() and '..'not in p.parts,'ABSOLUTE_NO_TRAVERSAL')
 for base in [NB,ST,RB]:
  if p.is_relative_to(base):return (NB if Path(__file__).is_relative_to(NB)else ST)/p.relative_to(base)
 raise AssertionError('EXACT_NAS_PROFILE_METADATA_DOMAIN')
def pinned(r):
 p=metadata_path(r['path']);fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC)
 try:
  a=os.fstat(fd);need(stat.S_ISREG(a.st_mode)and a.st_size==r['bytes']and 0<=a.st_size<=4*2**20,'BOUNDED_REGULAR_METADATA')
  parts=[];n=0
  while True:
   b=os.read(fd,min(65536,r['bytes']+1-n))
   if not b:break
   n+=len(b);need(n<=r['bytes'],'METADATA_BOUND');parts.append(b)
  z=os.fstat(fd);sig=lambda s:(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns);need(sig(a)==sig(z),'SAMEFD_META_STABLE')
 finally:os.close(fd)
 b=b''.join(parts);need(len(b)==r['bytes']and hashlib.sha256(b).hexdigest()==r['sha256'],'PINNED_META_SHA');return json.loads(b)
def contract(c):
 need(type(c['qid']) is str and re.fullmatch(r'[A-Za-z0-9_]{1,180}',c['qid']),'SAFE_EXACT_QID')
 need(type(c['header_count'])is int and 1<=c['header_count']<=128,'ALL_ORIGINAL_EXPECTED_KERNELS_MAX128')
 need(type(c['declared_source_records'])is int and 0<c['declared_source_records']<2**63,'POSITIVE_PRODUCER_DECLARED_RECORDS_NOT_TINY_CUTOFF')
 need(c['stream_ids']==[0],'ONLY_SINGLE_EXPLICIT_STREAM')
 need(len(c['command_names'])==c['header_count'] and len(set(c['command_names']))==c['header_count'],'EXACT_UNIQUE_COMMANDS')
 need(set(c['command_names'])==set(c['raw_source_metadata']),'EXACT_RAW_METADATA_SET')
 need(all(re.fullmatch(r'kernel-\d+-ctx_0x[0-9a-fA-F]+\.trace\.xz',n)for n in c['command_names']),'SAFE_KERNEL_NAMES')
 for x in c['raw_source_metadata'].values():
  need(all(type(x[k])is int for k in ['bytes','mtime_ns','ctime_ns']) and x['bytes']>0,'REAL_RAW_STAT_NOT_HEADER_INVENTION')
 return True
def metadata_guard(c):
 contract(c)
 m={k:pinned(v)for k,v in c['metadata_refs'].items()};j=m['job'];leaf=m['leaf'];ex=m['execution'];mp=m['map']
 need(j['id']==leaf['job_id']==ex['job_id']==c['qid'],'JOB_ID_JOIN')
 need(j['task']['binary_sha256']==ex['binary_sha256']==mp['binary_sha256']==c['binary_sha256'],'BINARY_JOIN')
 need(j['task']['argv']==ex['task']['argv']==c['argv'],'EXACT_ARGV')
 need(leaf['job_sha256']==c['metadata_refs']['job']['sha256'] and leaf['execution_sha256']==c['metadata_refs']['execution']['sha256'] and leaf['map_manifest_sha256']==c['metadata_refs']['map']['sha256'],'LEAF_PIN_JOIN')
 need(leaf['capture_exit']==ex['exit_code']==0 and leaf['producer_sha256']==ex['tool_sha256']=='55c6f4829e8c92e11e0ab54496bf8f507f6cfa3a10cd01a857c6de147ee68b73','CANONICAL55_CAPTURE0')
 d={k:pinned(v)for k,v in c['original_positive_closure_refs'].items()}
 proposal=d['REMOTE_CLOSED_PROPOSAL.json'];ack=d['NATIVE_CLEANUP_ACK.json'];consumed=d['REMOTE_ACK_CONSUMED.json'];released=d['NATIVE_RELEASED.json']
 need(proposal['status']=='CAPTURED_POST_PENDING' and proposal['error']is None and proposal['owned_descendants']==[],'POSITIVE_OWNED_CAPTURE_CLOSURE')
 need(ack['proposal_sha256']==c['original_positive_closure_refs']['REMOTE_CLOSED_PROPOSAL.json']['sha256'] and consumed['ACK_sha256']==c['original_positive_closure_refs']['NATIVE_CLEANUP_ACK.json']['sha256'],'ACTUAL_HANDSHAKE')
 need(released['status']=='ASSET_FOUR_LOCKS_CLOSED_AFTER_REMOTE_GPU_IO_CLOSURE','SOURCE_ASSET4_RELEASED')
 need(all(d[k]['scope_sha256']==c['source_scope_sha256']for k in ['REMOTE_CLOSED_PROPOSAL.json','NATIVE_CLEANUP_ACK.json','REMOTE_ACK_CONSUMED.json','NATIVE_RELEASED.json']),'SAME_CAPTURE_SCOPE')
 proof=pinned(c['Root_POST_input_admission_ref'])
 need(proof['schema']=='ROOT_REPEAT_ONLY4_ACTUAL_CAPTURE_QA_POST_INPUT_ADMISSION_V1' and proof['status']=='ROOT_ACTUAL_QA_CAPTURE_IDENTITY_AND_OWNED_CLOSED_ACCEPTED','REAL_ROOT_ADMISSION_NOT_TEMPLATE')
 need(proof['qid']==c['qid'] and proof['source_scope_sha256']==c['source_scope_sha256'] and proof['binary_sha256']==c['binary_sha256'] and proof['argv']==c['argv'],'ROOT_EXACT_IDENTITY')
 need(all(proof[k]is True for k in ['original_program_checks_PASS','no_QA_tracer_injection','QA_capture_binary_argv_input_contract_join','capture_exit0_complete_expected_launches','all_Native_asset_locks_independently_free','all_owned_remote_PIDs_absent_cgroups_empty','input_lifecycle_and_libc_contract_accepted']),'ROOT_REAL_QA_INPUT_CAPTURE_CLOSURE_REQUIRED')
 need(proof['metadata_refs']==c['metadata_refs'] and proof['positive_closure_refs']==c['original_positive_closure_refs'],'EXACT_ROOT_RAW_REFS')
 need(proof['expected_kernels']==c['header_count'] and proof['actual_declared_records']==c['declared_source_records'] and proof['actual_command_names']==c['command_names'],'ROOT_ALL_LAUNCH_STATS')
 source=pinned(c['source_contract_ref'])
 need(proof['source_contract_ref']==c['source_contract_ref'] and source['qid']==c['qid'] and source['binary_sha256']==c['binary_sha256'] and source['argv']==c['argv'] and source['expected_kernels']==c['header_count'],'FROZEN_NEW_SOURCE_CONTRACT_JOIN')
 need(source['purpose']=='REPEAT_ONLY_ORIGINAL_SPATIAL_WORKSET' and source['no_spatial_or_kernel_algorithm_change']is True,'EXACT_APPROVED_REPEAT_ONLY_PURPOSE')
 need(j['task']['profile']==c['profile']==source['profile'],'PROFILE_EXACT')
 # Proof is a fresh Root acceptance of the actual unmodified numerical QA/result refs.
 # No FNV marker or wholeinput SHA is inferred for programs that never emit one.
 need(proof['input_checksum_qualification']==c['input_checksum_qualification'],'HONEST_INPUT_QUALIFICATION')
 need(proof['native_QA_scope']==source['native_QA_scope']==c['native_QA_scope'],'EXACT_ORIGINAL_PROGRAM_QA_SCOPE_NOT_GENERIC_ORACLE')
 selected_capture_closed(c,pinned(c['selected_capture_closed_ref']))
 return True
def selected_capture_closed(c,closed):
 if closed['schema']=='ROOT_SCAN_R2_ACTUAL66_CAPTURE_QA_METADATA_AND_OWNED_ACCEPTANCE_V1':
  need(closed['status']=='CAPTURE_COMPLETE66_ORIGINAL_QA17_PASS_OWNED_CLOSED_PENDING_F9','ROOT_SELECTED_SCAN_ACTUAL_CAPTURE_CLOSURE')
  qid=closed['job_id'];profile=closed['actual_applicable_profile'];records=closed['producer_declared_warp_records']
 else:
  need(closed['schema']=='ROOT_REPEAT_ONLY_SELECTED_CAPTURE_CLOSURE_V1'and closed['status']=='ROOT_SELECTED_CAPTURE_COMPLETE_OWNED_CLOSED_PENDING_F9','ROOT_SELECTED_PROGRAM_ACTUAL_CAPTURE_CLOSURE')
  # Exact Root normalized projection retains original acceptance identity; not a replacement original.
  pinned(closed['original_acceptance_ref'])
  qid=closed['qid'];profile=closed['actual_profile'];records=closed['producer_declared_records']
 need(qid==c['qid']and closed['actual_complete_launches']==c['header_count']and records==c['declared_source_records'],'SELECTED_FULL_CAPTURE_COUNT_JOIN')
 need(profile==c['profile']and closed['owned_closed']is True and closed['Native4_independently_free']is True,'SELECTED_PROFILE_AND_OWNED_CLOSED')
 need(closed['leaf']['sha256']==c['metadata_refs']['leaf']['sha256']and closed['execution']['sha256']==c['metadata_refs']['execution']['sha256'],'SELECTED_ACCEPTED_LEAF_EXECUTION_JOIN')
 return True
def preflight_headers(c):
 metadata_guard(c);P=Path(__file__).parent;p=P/'bounded_raw_header_prefix_v2.py';b=p.read_bytes()
 need(hashlib.sha256(b).hexdigest()=='d87c0d47d70f738c069b7c39809e7edd35c8519e7c563128a322172901806c6d','HEADER_HELPER_PIN')
 H=types.ModuleType('header');exec(compile(b,str(p),'exec'),H.__dict__);root=metadata_path(c['source_root']);ls=list((root/'traces').glob('kernelslist_ctx_*'));need(len(ls)==1,'ONE_COMMAND_LIST')
 names=[n.strip()for n in ls[0].read_text().splitlines()if n.strip()and not n.startswith('Memcpy')]
 need(names==c['command_names'] and set(names)=={p.name for p in(root/'traces').glob('kernel*.trace.xz')},'ALL_KERNELS_NO_SAMPLING')
 result=[]
 for name in names:
  x=H.read_header(root/'traces'/name);e=c['raw_source_metadata'][name]
  need(x['header']['stream_id']==0 and x['header']['binary_version']==89 and x['header']['tracer_version']==7,'REAL_HEADER_STREAM_BV_TV')
  need(all(x['source_metadata'][k]==e[k]for k in ['bytes','mtime_ns','ctime_ns']),'REAL_RAW_STAT_BOUND')
  result.append(dict(name=name,**x))
 return dict(status='REAL_EXPLICIT_HEADERS_ONLY_NOT_FULL_RECORD_QA',files=result)
