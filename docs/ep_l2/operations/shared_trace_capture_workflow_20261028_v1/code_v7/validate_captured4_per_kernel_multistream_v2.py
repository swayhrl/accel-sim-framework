#!/usr/bin/env python3
"""ADA7 exact captured4 per-kernel record checks only; inter-stream happens-before unknown."""
import pathlib,json,hashlib,collections,re,lzma,argparse,csv,types,time,os,stat
H=pathlib.Path(__file__).with_name('frozen_parser_f4.py')
_parser_raw=H.read_bytes()
assert hashlib.sha256(_parser_raw).hexdigest()=='f4a811c779e9b106c0977af45634d1b7dc01025c9e9b2805b74de6c6c82b879b','frozen parser identity changed'
helper=types.ModuleType('ada7_frozen_parse');helper.__file__=str(H);exec(compile(_parser_raw,str(H),'exec'),helper.__dict__)
PROFILE='ADA7_CAPTURED4_PER_KERNEL_MULTISTREAM_RECORD_PROFILE_V2'
STATUS='PER_KERNEL_MULTISTREAM_FULL_RECORD_CHECKS_PASS'
CASE_ALLOWLIST_SHA='10339b363aa507858122e8c3c7160c828ba141c51be3a494071484cc75ffff63'
def sha(p):return helper.sha(p)
def _validate_records(root,mapfile,tap=None,expected_headers=None):
 m=json.loads(mapfile.read_text());rows={(x['function'],x['pc']):x for x in m['instructions']}
 assert len(rows)==len(m['instructions']),'duplicate static function/PC'
 execution=json.loads((root/'EXECUTION.json').read_text())
 assert execution['binary_sha256']==m['binary_sha256'],'capture/map binary SHA mismatch'
 assert execution['tool_sha256']=='55c6f4829e8c92e11e0ab54496bf8f507f6cfa3a10cd01a857c6de147ee68b73','pinned55 producer identity mismatch'
 ctxlists=sorted((root/'traces').glob('kernelslist_ctx_*'));assert len(ctxlists)==1,'per-kernel multi-stream profile requires exactly one context commandlist'
 declared=[]
 for line in ctxlists[0].read_text().splitlines():
  name=line.strip()
  if not name or name.startswith('Memcpy'):continue
  assert pathlib.PurePosixPath(name).name==name and name.startswith('kernel-') and name.endswith('.trace.xz'),'invalid raw command member'
  declared.append(name)
 assert declared and len(set(declared))==len(declared),'zero or duplicate declared kernel'
 raw={p.name:p for p in (root/'traces').glob('kernel*.trace.xz')}
 assert set(declared)==set(raw),'missing or undeclared raw kernel'
 contexts={re.search(r'ctx_(0x[0-9a-fA-F]+)',p).group(1) for p in declared};assert len(contexts)==1,'multiple CUDA contexts'
 total=collections.Counter();bykernel=[];files={};streams=set();peak_warps=0
 for command_index,name in enumerate(declared):
  f=raw[name];warps={};counts=collections.Counter();header={};function=None
  with lzma.open(f,'rt') as inp:
   for line in inp:
    if line.startswith('-kernel name = '):function=line.split(' = ',1)[1].strip()
    if line.startswith('-grid dim = '):header['grid']=tuple(map(int,re.findall(r'\d+',line)))
    if line.startswith('-block dim = '):header['block']=tuple(map(int,re.findall(r'\d+',line)))
    if line.startswith('-binary version = '):header['binary_version']=int(line.split('=',1)[1])
    if line.startswith('-accelsim tracer version = '):header['tracer_version']=int(line.split('=',1)[1])
    if line.startswith('-cuda stream id = '):
     sid=re.fullmatch(r'-cuda stream id = ([0-9]+)\s*',line)
     assert sid is not None and 'stream_id'not in header,'explicit unique nonnegative stream_id header required'
     header['stream_id']=int(sid[1])
    if not re.match(r'^\d+ \d+ \d+ \d+ ',line):continue
    assert type(header.get('stream_id'))is int and header['stream_id']>=0,'explicit stream_id required before every kernel body'
    if expected_headers is not None:
     actual=dict(header,function=function);actual['grid']=list(actual['grid']);actual['block']=list(actual['block'])
     assert actual==expected_headers[name]['header'],'actual per-kernel header differs from frozen captured input'
    key=line.split(maxsplit=4);cta=tuple(map(int,key[:3]));warp=int(key[3]);r=helper.parse(key[4]);exp=rows[(function,r['pc'])]
    if tap is not None:tap.observe(r,name,cta,warp,header)
    opbase=r['opcode'].split('.')[0]
    assert not any(opbase.startswith(x) for x in ['CALL','RET','JMX','BRX','LDGSTS','CPASYNC','TEX','TLD','SULD','SUST','SUATOM','UTMA','WGMMA','WARPSYNC']),'PENDING_SPECIALIST_EXTENSION '+r['opcode']
    assert not r['opcode'].startswith('BAR.WARP'),'PENDING_SPECIALIST_EXTENSION BAR.WARP'
    expected_tokens=exp['sass'].split()
    expected_opcode=expected_tokens[1] if expected_tokens[0].startswith('@') else expected_tokens[0]
    assert r['opcode']==expected_opcode,('opcode/static mismatch',r['opcode'],expected_opcode,name,r['pc'])
    cb=re.search(r'c\[\s*(0x[0-9a-fA-F]+|\d+)\s*\]\[\s*(-?0x[0-9a-fA-F]+|-?\d+)\s*\]',exp['sass'])
    if cb:
     bank=int(cb[1],0);offset=int(cb[2],0)
     assert r['bank']==bank and r['offset']==offset,'direct CBANK bank/static offset mismatch'
     assert all(x==offset for x in r['constant_offsets'].values()),'direct CBANK lane offset mismatch'
    assert r['src']==exp['src'] and r['dst']==exp['dst'],('dependency mismatch',name,cta,warp,r['pc'])
    w=warps.setdefault((cta,warp),{'records':0,'exited':0});assert not r['mask']&w['exited'],'executed instruction after EXIT'
    w['records']+=1
    if r['opcode']=='EXIT':w['exited']|=r['mask']
    counts['sass_records']+=1;counts['active_lane_instructions']+=r['mask'].bit_count();counts['zero_mask_records']+=r['mask']==0;counts['predicate_mixed_records']+=r['pred'] not in (0,0xffffffff)
    if r['bank']>=0 and r['mask']:
     counts['constant_source_records']+=1;counts['constant_lane_accesses']+=r['mask'].bit_count();counts['aux_uops']+=opbase not in ('LDC','ULDC')
    if r['width']:counts['explicit_memory_records']+=1;counts['explicit_memory_lane_accesses']+=len(r['addrs'])
  assert header['binary_version']==89 and header['tracer_version']==7
  gx,gy,gz=header['grid'];bx,by,bz=header['block'];threads=bx*by*bz;nwarps=(threads+31)//32
  assert all(x>0 for x in [gx,gy,gz,threads]) and threads<=1024 and counts['sass_records']>0 and len(warps)==gx*gy*gz*nwarps
  for (cta,warp),w in warps.items():
   assert 0<=cta[0]<gx and 0<=cta[1]<gy and 0<=cta[2]<gz and 0<=warp<nwarps
   assert w['exited']==(1<<min(32,threads-warp*32))-1
  peak_warps=max(peak_warps,len(warps));streams.add(header['stream_id'])
  bykernel.append({'producer_command_index':command_index,'original_kernel_index':int(re.fullmatch(r'kernel-(\d+)-ctx_0x[0-9a-fA-F]+\.trace\.xz',name)[1]),'name':name,'function':function,'header':header,'ctas':gx*gy*gz,'warps':len(warps),'counts':dict(counts),'all_declared_warps_terminate':True})
  total.update(counts);files[str(f)]=sha(f);del warps
 assert len(streams)>=2,'MULTISTREAM_INPUT_REQUIRES_AT_LEAST_TWO_EXPLICIT_STREAM_IDS'
 statsfiles=sorted((root/'traces').glob('stats_ctx_*'));assert len(statsfiles)==1
 with statsfiles[0].open() as f:stats=list(csv.reader(f))
 stats=[x for x in stats[1:] if x]
 assert len(stats)==len(declared)
 named_stats={x[0].strip():x for x in stats};assert set(named_stats)==set(declared)
 for k in bykernel:assert int(named_stats[k['name']][-1])==k['counts']['sass_records'],'reported record count mismatch'
 return {'schema':'ADA7_CAPTURED4_PER_KERNEL_RECORD_VERIFICATION_V2','status':STATUS,'profile':PROFILE,'counts':dict(total),'ctas':sum(x['ctas'] for x in bykernel),'warps':sum(x['warps'] for x in bykernel),'kernels':len(bykernel),'all_declared_warps_terminate':True,'kernel_commandlist_exact_set':True,'stats_record_counts_match':True,'context_count':1,'stream_ids':sorted(streams),'per_kernel':bykernel,'peak_live_warp_states':peak_warps,'source_files':files,'map_sha256':sha(mapfile),'frozen_parser_sha256':sha(H),'validator_sha256':sha(pathlib.Path(__file__)),'lane_address_lists_retained':False,'capture_map_binary_binding':True,'frozen_parser_identity_asserted':True,'direct_cbank_static_and_lane_offsets_verified':True,'strict_single_stream_ordinary':False,'inter_stream_happens_before':'UNKNOWN_NOT_CAPTURED_OR_VALIDATED','command_order_semantics':'PRODUCER_RECORDED_COMMAND_ORDER_ONLY_NOT_CUDA_HAPPENS_BEFORE','producer_kernel_command_order':declared,'full_application_concurrent_model':False,'producer_semantic_qualification':'PER_KERNEL_RECORDS_ONLY','applicable_consumer_qualification':False,'whole_input_functional_qualified':False,'canonical161_complete':False,'numeric_qualified':False,'performance_qualified':False,'scientific_qualified':False}
def _pinned_json(ref):
 p=pathlib.Path(ref['path']);assert 0<ref['bytes']<=2**20,'bounded exact source metadata'
 fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC)
 try:
  before=os.fstat(fd);assert stat.S_ISREG(before.st_mode)and before.st_size==ref['bytes'],'regular exact source metadata'
  parts=[];total=0
  while True:
   b=os.read(fd,min(65536,ref['bytes']+1-total))
   if not b:break
   total+=len(b);assert total<=ref['bytes'],'source metadata read bound';parts.append(b)
  after=os.fstat(fd);key=lambda q:(q.st_dev,q.st_ino,q.st_size,q.st_mtime_ns,q.st_ctime_ns);assert key(before)==key(after),'sameFD source metadata'
 finally:os.close(fd)
 raw=b''.join(parts);assert len(raw)==ref['bytes']and hashlib.sha256(raw).hexdigest()==ref['sha256'],'exact source metadata rawSHA'
 return json.loads(raw)
def identity_guard(queue_id,root,mapfile):
 cases=_pinned_json(dict(path=str(pathlib.Path(__file__).with_name('EXACT_FOUR_CASES.json')),bytes=61598,sha256=CASE_ALLOWLIST_SHA))['cases'];assert queue_id in cases,'not an admitted exact captured4 input'
 c=cases[queue_id];b=c['binding'];i=c['task_identity'];root=pathlib.Path(root);mapfile=pathlib.Path(mapfile)
 assert str(root)==b['source_root']and str(mapfile)==b['map_ref']['path'],'only exact original captured source/map paths'
 j=_pinned_json(b['frozen_job_ref']);leaf=_pinned_json(b['capture_receipt_ref']);ex=_pinned_json(c['execution_ref']);_pinned_json(b['map_ref'])
 assert j['id']==queue_id==ex['job_id']==leaf['job_id'],'exact case qid'
 assert j['task']['argv']==i['argv']==ex['task']['argv']and j['task']['binary_sha256']==i['binary_sha256']==ex['binary_sha256'],'exact case binary and original argv'
 assert leaf['job_sha256']==b['frozen_job_ref']['sha256']and leaf['execution_sha256']==c['execution_ref']['sha256']and leaf['map_manifest_sha256']==b['map_ref']['sha256'],'original capture metadata join'
 assert leaf['capture_exit']==ex['exit_code']==0 and leaf['producer_sha256']==ex['tool_sha256']=='55c6f4829e8c92e11e0ab54496bf8f507f6cfa3a10cd01a857c6de147ee68b73','original capture0/pinned producer'
 return c
def _preflight_headers(root,c):
 raw=pathlib.Path(__file__).with_name('bounded_raw_header_prefix_v2.py').read_bytes()
 assert hashlib.sha256(raw).hexdigest()=='d87c0d47d70f738c069b7c39809e7edd35c8519e7c563128a322172901806c6d','bounded prefix helper pin'
 H=types.ModuleType('bounded_header');exec(compile(raw,'bounded_raw_header_prefix_v2.py','exec'),H.__dict__)
 contract=c['header_contract'];_pinned_json(contract['source_census_ref'])
 lists=list((root/'traces').glob('kernelslist_ctx_*'));assert len(lists)==1
 names=[n.strip()for n in lists[0].read_text().splitlines()if n.strip()and not n.startswith('Memcpy')]
 assert names==contract['command_names']and set(names)==set(contract['files']),'frozen original command order/header set'
 assert set(names)=={p.name for p in(root/'traces').glob('kernel*.trace.xz')},'exact raw header source set'
 results=[]
 for name in names:
  assert pathlib.PurePosixPath(name).name==name,'relative raw member'
  x=H.read_header(root/'traces'/name);e=contract['files'][name]
  assert x['header']==e['header']and x['prefix_sha256']==e['prefix_sha256'],'frozen actual header/first-record prefix bytes'
  assert tuple(x['source_metadata'][k]for k in['bytes','mtime_ns','ctime_ns'])==tuple(e[k]for k in['source_bytes','mtime_ns','ctime_ns']),'original raw stable metadata'
  results.append(dict(name=name,**x))
 streams=sorted({x['header']['stream_id']for x in results})
 assert streams==contract['stream_ids']and len(streams)>=2,'exact admitted multistream set before any record loop'
 return dict(status='EXACT_HEADER_PREFIX_PREFLIGHT_ONLY_NOT_FULL_CRC',files=results,stream_ids=streams,record_loop=False,CRC_qualified=False)

def validate_exact(queue_id,root,mapfile,tap=None):
 c=identity_guard(queue_id,root,mapfile)
 headers=_preflight_headers(pathlib.Path(root),c)
 result=_validate_records(pathlib.Path(root),pathlib.Path(mapfile),tap,c['header_contract']['files'])
 assert result['stream_ids']==headers['stream_ids'],'validated stream IDs equal preflight'
 result['header_prefix_preflight']=headers
 assert result['map_sha256']==c['binding']['map_ref']['sha256'],'map remained exact throughout verification'
 result.update(queue_id=queue_id,exact_binary_sha256=c['task_identity']['binary_sha256'],original_argv=c['task_identity']['argv'],original_capture_history=c['capture_history'],exact_capture_metadata_join=True)
 return result
if __name__=='__main__':
 raise SystemExit('Component only: actual POST requires a new Root-reviewed bounded caller and exact data scope; no standalone actual validation is executed.')
