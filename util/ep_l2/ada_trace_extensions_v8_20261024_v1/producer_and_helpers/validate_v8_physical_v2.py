import argparse,collections,hashlib,importlib.util,json,lzma,pathlib,re
H=pathlib.Path('/data/c16/ada_trace_semantics_20261024_v1/frozen/ada7_contract_v1/validate_v7.py')
loader=importlib.util.spec_from_file_location('ordinary_parser',H);old=importlib.util.module_from_spec(loader);loader.loader.exec_module(old)
def parse(line):
 t=line.split();at=t.index('ADA8');mask=int(t[1],16);n=mask.bit_count();bank=int(t[at+3]);end=at+8+(n if bank>=0 else 0)
 head=t[:end];head[at]='ADA7';r=old.parse(' '.join(head));kind=int(t[end]);tail=list(map(int,t[end+1:]));assert len(tail)==(n if kind else 0)
 r['control_kind']=kind;r['control_targets']=dict(zip([i for i in range(32)if mask>>i&1],tail));return r
def main():
 p=argparse.ArgumentParser();p.add_argument('attempt');p.add_argument('map');p.add_argument('--embedded-call',action='store_true');a=p.parse_args();R=pathlib.Path(a.attempt)
 source=json.loads(pathlib.Path(a.map).read_text());original={(x['function'],x['pc']):x for x in source['instructions']};static={};bases={}
 for line in (R/'traces/ada-static.tsv').read_text().splitlines():
  t=line.split('\t');absolute=int(t[0],16);pc=int(t[1],16);fn=t[2];qualified=int(t[7]);kind=int(t[8]);base=absolute-pc
  if fn in bases:assert bases[fn]==base
  bases[fn]=base
  if qualified:
   assert (fn,pc)in original and original[(fn,pc)]['sass']==t[3]
   assert absolute not in static
   static[absolute]=dict(row=original[(fn,pc)],kind=kind,base=base,summary_src=t[10],summary_dst=t[11])
 counts=collections.Counter();warps={};headers={}
 for f in sorted((R/'traces').glob('kernel*.trace.xz')):
  headers[f.name]={}
  with lzma.open(f,'rt')as stream:
   for line in stream:
    if line.startswith('-grid dim = '):headers[f.name]['grid']=tuple(map(int,re.findall(r'\d+',line)))
    if line.startswith('-block dim = '):headers[f.name]['block']=tuple(map(int,re.findall(r'\d+',line)))
    if line.startswith('-binary version = '):headers[f.name]['binary_version']=int(line.split('=',1)[1]);assert headers[f.name]['binary_version']==89
    if line.startswith('-accelsim tracer version = '):headers[f.name]['tracer_version']=int(line.split('=',1)[1]);assert headers[f.name]['tracer_version']==8
    if not re.match(r'^\d+ \d+ \d+ \d+ ',line):continue
    words=line.split(maxsplit=4);cta=tuple(map(int,words[:3]));warp=int(words[3]);r=parse(words[4]);s=static[r['pc']];exp=s['row'];kind=r['control_kind'];assert s['kind']==kind
    h=headers[f.name];gx,gy,gz=h['grid'];bx,by,bz=h['block'];threads=bx*by*bz;assert 0<=cta[0]<gx and 0<=cta[1]<gy and 0<=cta[2]<gz and 0<=warp<(threads+31)//32;launched=(1<<min(32,threads-warp*32))-1;assert not((r['mask']|r['active']|r['pred'])&~launched),'record exceeds physical launched lane mask';counts['physical_mask_records_verified']+=1
    op=exp['sass'].split();expected=op[1]if op[0].startswith('@')else op[0];assert r['opcode']==expected
    if kind==1:
     assert a.embedded_call and r['src']==r['dst']==[]
     assert [int(x)for x in s['summary_src'].split(',')if x]==exp['src']
     assert [int(x)for x in s['summary_dst'].split(',')if x]==exp['dst']
    else:assert r['src']==exp['src'] and r['dst']==exp['dst']
    w=warps.setdefault((f.name,cta,warp),dict(exited=0,stack=[[]for _ in range(32)],pending=[None]*32))
    assert not r['mask']&w['exited']
    lanes=[i for i in range(32)if r['mask']>>i&1]
    for lane in lanes:
     if w['pending'][lane]is not None:assert r['pc']==w['pending'][lane];w['pending'][lane]=None
    if kind==1:
     target=int(re.search(r'0x([0-9a-fA-F]+)',exp['sass'])[1],16)
     for lane,value in r['control_targets'].items():
      assert value==target;w['stack'][lane].append(r['pc']+16);w['pending'][lane]=s['base']+value
     counts['call_lane_targets_verified']+=len(lanes)
    elif kind==2:
     assert a.embedded_call
     for lane,value in r['control_targets'].items():
      assert w['stack'][lane]and w['stack'][lane].pop()==s['base']+value;w['pending'][lane]=s['base']+value
     counts['return_lane_targets_verified']+=len(lanes)
    elif kind==3:
     for lane,value in r['control_targets'].items():assert value&(1<<lane)
     counts['warpsync_lane_masks_captured']+=len(lanes)
    elif kind:raise ValueError('unsupported control kind')
    if r['opcode']=='EXIT':
     for lane in lanes:assert not w['stack'][lane] and w['pending'][lane]is None
     w['exited']|=r['mask']
    counts['source_sass_records']+=1;counts['source_active_lane_instances']+=len(lanes);counts['zero_mask_records']+=r['mask']==0
    if r['bank']>=0 and lanes:
     counts['constant_lane_accesses']+=len(lanes)
     if r['opcode'].split('.')[0]not in('LDC','ULDC'):counts['aux_uops']+=1;counts['aux_lane_instances']+=len(lanes)
 for fname,h in headers.items():
  assert h['binary_version']==89 and h['tracer_version']==8
  gx,gy,gz=h['grid'];bx,by,bz=h['block'];threads=bx*by*bz;nwarps=(threads+31)//32;items=[(cta,warp,w)for(name,cta,warp),w in warps.items()if name==fname]
  assert len(items)==gx*gy*gz*nwarps
  for cta,warp,w in items:assert 0<=warp<nwarps and w['exited']==(1<<min(32,threads-warp*32))-1 and not any(w['stack'])and not any(x is not None for x in w['pending'])
 api=(R/'traces/ada-api.tsv').read_text().splitlines();launch=(R/'traces/ada-launch.tsv').read_text().splitlines()
 entries=[x for x in launch if x.split('\t')[1]=='0'];exits=[x for x in launch if x.split('\t')[1]=='1'];assert len(entries)==len(exits)==len(headers)
 assert len({x.split('\t')[2]for x in launch})==1
 out=dict(schema='ADA8_EMBEDDED_CONTROL_QUALIFICATION_DEV_V1',counts=dict(counts),warps=len(warps),kernels=len(headers),source_binary_sha256=source['binary_sha256'],call_summary_not_physical_rf=True,all_per_lane_call_return_targets_and_successors_verified=True,launch_api_event_counts_match=True,api_events=len(api),source_files={f.name:old.sha(f)for f in (R/'traces').glob('kernel*.trace.xz')})
 with(R/'FULL_RECORD_V8_PHYSICAL_VALIDATION.json').open('x')as f:json.dump(out,f,indent=2);f.write('\n')
 print(json.dumps(out))
if __name__=='__main__':main()
