"""Exact repaired smallPoly capture metadata+original QA identity. No body qualification."""
from pathlib import Path
import json,os,stat,hashlib,types,re,csv,io
NB=Path('/root/share/mnt164/huangrulin/traces/rtx4080_sm89/bulk_20261024_v1')
ST=Path('/data/c16/rtx4080_suite_fill_20261024_v1/nas_fast_sc_copy_st_20261029_v2')
def need(v,m):
 if not v:raise AssertionError(m)
def metadata_path(p):
 p=Path(p);need(p.is_absolute()and '..'not in p.parts,'ABSOLUTE_NO_TRAVERSAL')
 for b in [NB,ST]:
  if p.is_relative_to(b):return(NB if Path(__file__).is_relative_to(NB)else ST)/p.relative_to(b)
 raise AssertionError('EXACT_NAS_METADATA_DOMAIN')
def pinned(r):
 p=metadata_path(r['path']);fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC|os.O_NONBLOCK)
 try:
  a=os.fstat(fd);need(stat.S_ISREG(a.st_mode)and 0<a.st_size==r['bytes']<=4*2**20,'BOUNDED_REGULAR_META')
  raw=b''
  while len(raw)<=r['bytes']:
   x=os.read(fd,min(65536,r['bytes']+1-len(raw)))
   if not x:break
   raw+=x
  z=os.fstat(fd);key=lambda q:(q.st_dev,q.st_ino,q.st_size,q.st_mtime_ns,q.st_ctime_ns);need(key(a)==key(z),'SAMEFD_META')
 finally:os.close(fd)
 need(len(raw)==r['bytes']and hashlib.sha256(raw).hexdigest()==r['sha256'],'PINNED_META_SHA');return json.loads(raw)

def contract(c):
 counts={'SDK429_ALIGNEDTYPES_ORIGINAL50MB_TYPES12_REPEAT2_V1':24,'SDK429_TRANSPOSE_ORIGINAL1024_OUTER2_INNER2_ALL8_V1':32}
 need(c['qid']in counts and c['header_count']==counts[c['qid']],'EXACT_SDK42924_32')
 need(c['declared_source_records']in [60768064,39485440]and c['stream_ids']==[0],'EXACT_DECLARED_SOURCE_COUNTS_SINGLE_STREAM')
 need(len(c['command_names'])==len(set(c['command_names']))==c['header_count']and set(c['command_names'])==set(c['raw_source_metadata'])==set(c['actual_bounded_header_files']),'ALL_RAW_HEADERS')
 need(c['actual_input_byte_SHA_observed']is False and c['input_identity_basis']=='SDK429_REPEAT2_DETERMINISTIC_SOURCE_RECIPE_ONLY_NO_ACTUAL_INPUT_BYTE_SHA_NO_CUDA118_EQUIVALENCE','HONEST_SOURCE_DOMAIN')
 return True
def ref_equal(a,b):
 return a['bytes']==b['bytes']and a['sha256']==b['sha256']and metadata_path(a['path'])==metadata_path(b['path'])
def selected_capture_closed(c,proof):
 need(proof['schema']=='ROOT_SDK429_RAW_REPEAT2_FULL_CAPTURE2_INDEPENDENT_ACCEPTANCE_V1'and proof['status']=='ROOT_ACCEPTED_EXACT_CAPTURE24_AND32_QA_AND_OWNED_CLOSED_POST_PENDING','REAL_ROOT_CAPTURE2')
 need(proof['Native8_exact_locks_fresh_free']is True and proof['Native_same_owner_absent']is True and proof['remote_owned_independent_reopen']['cgroups_empty']is True and all(x['same_owned_PID_absent']is True for x in proof['remote_owned_independent_reopen']['owned']),'ROOT_REAL_OWNED_AND_NATIVE8')
 need(proof['scope_sha256']==c['source_scope_sha256'],'ORIGINAL_CAPTURE_SCOPE')
 rows=[r for r in proof['rows']if r['job_id']==c['qid']];need(len(rows)==1,'ROOT_EXACT_ROW');r=rows[0]
 need(r['launches']==c['header_count']and r['declared_records']==c['declared_source_records']and ref_equal(r['leaf_ref'],c['metadata_refs']['leaf'])and ref_equal(r['stats_ref'],c['raw_stats_ref']),'ROOT_ALL_LAUNCHES_DECLARATION')
 need(ref_equal(r['Native_release_ref'],c['original_positive_closure_refs']['NATIVE_RELEASED.json'])and ref_equal(r['remote_closure_ref'],c['original_positive_closure_refs']['REMOTE_CLOSURE_OBSERVATION.json']),'ROOT_REAL_RELEASE_REFS')
 return True
def metadata_guard(c):
 contract(c);m={k:pinned(v)for k,v in c['metadata_refs'].items()};j=m['job'];l=m['leaf'];e=m['execution'];mp=m['map'];q=c['qid']
 need(j['id']==l['job_id']==e['job_id']==q and j['task']['binary_sha256']==e['binary_sha256']==mp['binary_sha256']==c['binary_sha256']and j['task']['argv']==e['task']['argv']==c['argv'],'EXACT_ELF_ARGV_JOB')
 need(l['job_sha256']==c['metadata_refs']['job']['sha256']and l['execution_sha256']==c['metadata_refs']['execution']['sha256']and l['map_manifest_sha256']==c['metadata_refs']['map']['sha256'],'LEAF_RAW_META_SHA')
 need(l['capture_exit']==e['exit_code']==0 and l['producer_sha256']==e['tool_sha256']=='55c6f4829e8c92e11e0ab54496bf8f507f6cfa3a10cd01a857c6de147ee68b73'and l['numerical_status']=='NATIVE_AND_CAPTURE_QA_PASS','ACTUAL55_CAPTURE_AND_QA')
 d={k:pinned(v)for k,v in c['original_positive_closure_refs'].items()};p=d['REMOTE_CLOSED_PROPOSAL.json']
 need(p['job_id']==q and p['status']=='CAPTURED_POST_PENDING'and p['error']is None and p['owned_descendants']==[]and p['remote_GPU_LOCAL_IO_closed']is True,'REAL_CAPTURE_REMOTE_CLOSED')
 need(d['NATIVE_CLEANUP_ACK.json']['proposal_sha256']==c['original_positive_closure_refs']['REMOTE_CLOSED_PROPOSAL.json']['sha256']and d['REMOTE_ACK_CONSUMED.json']['ACK_sha256']==c['original_positive_closure_refs']['NATIVE_CLEANUP_ACK.json']['sha256'],'ACTUAL_HANDSHAKE')
 need(d['NATIVE_RELEASED.json']['status']=='ASSET_FOUR_LOCKS_CLOSED_AFTER_REMOTE_GPU_IO_CLOSURE'and d['REMOTE_CLOSURE_OBSERVATION.json']['owned_closed']is True and all(x['scope_sha256']==c['source_scope_sha256']for x in d.values()),'ACTUAL_NATIVE_RELEASE_SAME_SCOPE')
 source=pinned(c['source_contract_ref']);need(source['qid']==q and source['profile']==j['task']['profile']==c['profile']and source['source_files']==j['task']['source_files']and source['binary_sha256']==c['binary_sha256']and source['argv']==c['argv'],'CORRECTED_SOURCE_IDENTITY_NOT_MOTHER_DESCRIPTIVE_TAGS')
 need(c['provenance_erratum']['original_raw_record_unchanged']is True and c['provenance_erratum']['incorrect_inherited_descriptive_fields']==['sample_path','task_id','binary_cubin_listing','historical_relation'],'ERRATUM_EXPLICIT_NO_HISTORY_REWRITE')
 qa=pinned(c['actual_native_QA_acceptance_ref']);need(qa['schema']=='ROOT_REPEAT_ONLY4_ACTUAL_QA_AND_OWNED_ACCEPTANCE_V1'and qa['owned_closed']is True and qa['Native_asset8_independently_free']is True,'ROOT_QA2_OWNED')
 qr=qa['rows'][q];need(qr['exit_code']==0 and qr['original_gold_QA_PASS']is True and qr['no_tracer_injection']is True and qr['binary_sha256']==c['binary_sha256']and qr['argv']==c['argv'],'ACTUAL_ORIGINAL_QA_BINARY_SCOPE')
 result=pinned(qr['qa_result_ref']);need(result['job_id']==q and result['binary_sha256']==c['binary_sha256']and result['argv']==c['argv']and result['exit_code']==0 and result['no_tracer_injection']is True,'QA_RAW_RESULT')
 need(m['declaration']['producer_declared_warp_records']==c['declared_source_records']and m['declaration']['record_count_truncation_policy']is False,'FULL_PRODUCER_DECLARED_RECORDS_NOT_F9')
 stats=pinned(c['stats_json_ref'])
 for key in ['raw_stats_ref','raw_index_ref']:
  rr=c[key];p=metadata_path(rr['path']);need(p.is_file()and not p.is_symlink()and p.stat().st_size==rr['bytes']<=65536,'BOUNDED_STATS_INDEX');rb=p.read_bytes();need(hashlib.sha256(rb).hexdigest()==rr['sha256'],'RAW_STATS_INDEX_SHA')
 actual=list(csv.reader(io.StringIO(metadata_path(c['raw_stats_ref']['path']).read_text())))[1:];actual=[x for x in actual if x]
 need([x[0].strip()for x in actual]==stats['names']==c['command_names']and [int(x[-1])for x in actual]==stats['records']and sum(stats['records'])==c['declared_source_records'],'ACTUAL_ALL_STATS_DECLARATIONS')
 selected_capture_closed(c,pinned(c['Root_POST_input_admission_ref']))
 return True

def preflight_headers(c):
 metadata_guard(c);p=Path(__file__).with_name('bounded_raw_header_prefix_v2.py');raw=p.read_bytes();need(hashlib.sha256(raw).hexdigest()=='d87c0d47d70f738c069b7c39809e7edd35c8519e7c563128a322172901806c6d','ORIGINAL_HEADER_PIN')
 H=types.ModuleType('header');exec(compile(raw,str(p),'exec'),H.__dict__)
 root=metadata_path(c['source_root']);ls=list((root/'traces').glob('kernelslist_ctx_*'));need(len(ls)==1,'ONE_CONTEXT_COMMANDLIST')
 names=[n.strip()for n in ls[0].read_text().splitlines()if n.strip()and not n.startswith('Memcpy')]
 need(names==c['command_names']and set(names)=={x.name for x in(root/'traces').glob('kernel*.trace.xz')},'ALL_KERNELS_NO_SAMPLING')
 result=[]
 for n in names:
  x=H.read_header(root/'traces'/n);e=c['actual_bounded_header_files'][n]
  need(x['header']==e['header']and x['prefix_sha256']==e['prefix_sha256'],'EXACT_ACTUAL_HEADERS_PREFIX')
  need(all(x['source_metadata'][k]==c['raw_source_metadata'][n][k]for k in ['bytes','mtime_ns','ctime_ns']),'ORIGINAL_RAW_STAT_STABLE')
  result.append(dict(name=n,**x))
 return dict(status='BOUNDED_EXPLICIT_HEADER_PREFLIGHT_NOT_RECORD_OR_FULL_CRC',files=result)
