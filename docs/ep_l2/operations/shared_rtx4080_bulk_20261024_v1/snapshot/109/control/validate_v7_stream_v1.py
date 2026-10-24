#!/usr/bin/env python3
"""ADA7 ordinary records, bounded per-kernel state and full commandlist closure."""
import pathlib,json,hashlib,collections,re,lzma,argparse,csv,importlib.util,time
H=pathlib.Path('/data/c16/ada_trace_semantics_20261024_v1/frozen/ada7_contract_v1/validate_v7.py')
spec=importlib.util.spec_from_file_location('ada7_frozen_parse',H);helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
def sha(p):return helper.sha(p)
def validate(root,mapfile):
 m=json.loads(mapfile.read_text());rows={(x['function'],x['pc']):x for x in m['instructions']}
 assert len(rows)==len(m['instructions']),'duplicate static function/PC'
 ctxlists=sorted((root/'traces').glob('kernelslist_ctx_*'));assert len(ctxlists)==1,'ordinary domain requires exactly one context commandlist'
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
 for name in declared:
  f=raw[name];warps={};counts=collections.Counter();header={};function=None
  with lzma.open(f,'rt') as inp:
   for line in inp:
    if line.startswith('-kernel name = '):function=line.split(' = ',1)[1].strip()
    if line.startswith('-grid dim = '):header['grid']=tuple(map(int,re.findall(r'\d+',line)))
    if line.startswith('-block dim = '):header['block']=tuple(map(int,re.findall(r'\d+',line)))
    if line.startswith('-binary version = '):header['binary_version']=int(line.split('=',1)[1])
    if line.startswith('-accelsim tracer version = '):header['tracer_version']=int(line.split('=',1)[1])
    if line.startswith('-cuda stream id = '):header['stream_id']=int(line.split('=',1)[1])
    if not re.match(r'^\d+ \d+ \d+ \d+ ',line):continue
    key=line.split(maxsplit=4);cta=tuple(map(int,key[:3]));warp=int(key[3]);r=helper.parse(key[4]);exp=rows[(function,r['pc'])]
    opbase=r['opcode'].split('.')[0]
    assert not any(opbase.startswith(x) for x in ['CALL','RET','JMX','BRX','LDGSTS','CPASYNC','TEX','TLD','SULD','SUST','SUATOM','UTMA','WGMMA','WARPSYNC']),'PENDING_SPECIALIST_EXTENSION '+r['opcode']
    assert not r['opcode'].startswith('BAR.WARP'),'PENDING_SPECIALIST_EXTENSION BAR.WARP'
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
  assert threads<=1024 and len(warps)==gx*gy*gz*nwarps
  for (cta,warp),w in warps.items():
   assert 0<=cta[0]<gx and 0<=cta[1]<gy and 0<=cta[2]<gz and 0<=warp<nwarps
   assert w['exited']==(1<<min(32,threads-warp*32))-1
  peak_warps=max(peak_warps,len(warps));streams.add(header.get('stream_id',0))
  bykernel.append({'name':name,'function':function,'header':header,'ctas':gx*gy*gz,'warps':len(warps),'counts':dict(counts),'all_declared_warps_terminate':True})
  total.update(counts);files[str(f)]=sha(f);del warps
 statsfiles=sorted((root/'traces').glob('stats_ctx_*'));assert len(statsfiles)==1
 with statsfiles[0].open() as f:stats=list(csv.reader(f))
 stats=[x for x in stats[1:] if x]
 assert len(stats)==len(declared)
 named_stats={x[0].strip():x for x in stats};assert set(named_stats)==set(declared)
 for k in bykernel:assert int(named_stats[k['name']][-1])==k['counts']['sass_records'],'reported record count mismatch'
 return {'schema':'ADA7_STREAM_FULL_RECORD_VERIFICATION_V1','status':'ADA7_ORDINARY_FULL_RECORD_PASS','counts':dict(total),'ctas':sum(x['ctas'] for x in bykernel),'warps':sum(x['warps'] for x in bykernel),'kernels':len(bykernel),'all_declared_warps_terminate':True,'kernel_commandlist_exact_set':True,'stats_record_counts_match':True,'context_count':1,'stream_ids':sorted(streams),'per_kernel':bykernel,'peak_live_warp_states':peak_warps,'source_files':files,'map_sha256':sha(mapfile),'frozen_parser_sha256':sha(H),'validator_sha256':sha(pathlib.Path(__file__)),'lane_address_lists_retained':False}
def main():
 p=argparse.ArgumentParser();p.add_argument('attempt');p.add_argument('map');p.add_argument('--output',default='FULL_RECORD_STREAM_VALIDATION.json');a=p.parse_args()
 root=pathlib.Path(a.attempt);out=root/a.output;assert not out.exists()
 result=validate(root,pathlib.Path(a.map))
 with out.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
 print(json.dumps(result))
if __name__=='__main__':main()

