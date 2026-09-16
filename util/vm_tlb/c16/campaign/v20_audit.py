import hashlib,json,re,struct
from collections import Counter
from pathlib import Path
H=struct.Struct('<8sIIQQQ');R=struct.Struct('<6I32Q')
scenario=__import__('os').environ['C16_V20_SCENARIO'];label=__import__('os').environ.get('C16_V20_CAPTURE_LABEL',scenario);base=Path('/data/c16/qwen3_runtime_v14/v20');root=base/f'{label}_formal_capture';expected={'S2_TEXT':16392,'S3_TEXT':65544}[scenario]
terminal=re.compile(r'C16_WARP_TERMINAL static=(\d+) occurrence=(\d+) records=(\d+) overflow=(\d+)')
def sha(p):
 h=hashlib.sha256();
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
shards=[];allctas=set();totalevents=0;alladdr=[]
for d in sorted(root.glob('mref_*'),key=lambda x:int(x.name[5:])):
 idx=int(d.name[5:]);raw=(d/'trace.bin').read_bytes();magic,si,occ,callbacks,overflow,kept=H.unpack_from(raw)
 if magic!=b'C16WARP1' or si!=idx or len(raw)!=H.size+kept*R.size or overflow or callbacks!=kept:raise SystemExit(f'container fail {idx}')
 m=terminal.findall((d/'stdout.log').read_text())
 if len(m)!=1 or tuple(map(int,m[0]))!=(idx,occ,kept,overflow):raise SystemExit(f'terminal fail {idx}')
 ctx=json.loads((d/'ADDRESS_CONTEXT.json').read_text());ranges={r['class']:(int(r['address_start_hex'],16),int(r['address_start_hex'],16)+int(r['storage_bytes'])) for r in ctx['ranges']}
 ctas=set();warps=set();events=[];addr=[]
 for off in range(H.size,len(raw),R.size):
  rec=R.unpack_from(raw,off);_,mask,x,y,z,w,*vals=rec;ctas.add((x,y,z));warps.add(w);allctas.add((x,y,z))
  for lane,a in enumerate(vals):
   if mask>>lane&1:events.append(a);addr.append(a);alladdr.append(a)
 source=sum(ranges['KV_POST_UPDATE_K'][0]<=a<ranges['KV_POST_UPDATE_K'][1] for a in addr);derived=sum(ranges['KV_DERIVED_REPEAT_K'][0]<=a<ranges['KV_DERIVED_REPEAT_K'][1] for a in addr)
 shards.append({'static_index':idx,'trace_sha256':sha(d/'trace.bin'),'address_context_sha256':sha(d/'ADDRESS_CONTEXT.json'),'records':kept,'callback_records':callbacks,'overflow':overflow,'classification':'EXECUTED_SHARD' if kept else 'ZERO_EXECUTION_PROVEN','active_lane_events':len(events),'unique_ctas':len(ctas),'cta_x_min':min((c[0] for c in ctas),default=None),'cta_x_max':max((c[0] for c in ctas),default=None),'warp_ids':sorted(warps),'address_min_hex':hex(min(addr)) if addr else None,'address_max_hex':hex(max(addr)) if addr else None,'kv_post_update_k_events':source,'kv_derived_repeat_k_events':derived,'unique_4k_pages':len({a>>12 for a in addr}),'unique_64k_pages':len({a>>16 for a in addr}),'unique_2m_pages':len({a>>21 for a in addr}),'unique_128b_lines':len({a>>7 for a in addr})});totalevents+=len(events)
executed=[x for x in shards if x['classification']=='EXECUTED_SHARD'];source_shards=[x for x in executed if x['kv_post_update_k_events']>0];full=bool(source_shards) and min(c[0] for c in allctas)==0 and max(c[0] for c in allctas)==expected-1 and all(x['kv_post_update_k_events']==x['active_lane_events'] for x in source_shards)
r={'schema_version':1,'scenario':scenario,'target':'layer0.self_attn.repeat_kv(K)','evidence_class':'KV_STORAGE_DIRECT_READ','expected_grid_x':expected,'captured_static_shards':len(shards),'executed_shards':len(executed),'zero_shards':len(shards)-len(executed),'source_read_shards':len(source_shards),'overflow_total':sum(x['overflow'] for x in shards),'active_lane_events':totalevents,'union_cta_x_min':min(c[0] for c in allctas),'union_cta_x_max':max(c[0] for c in allctas),'union_unique_ctas':len(allctas),'full_scope_gate':'PASS' if full else 'FAIL','shards':shards,'aggregate_unique_4k_pages':len({a>>12 for a in alladdr}),'aggregate_unique_64k_pages':len({a>>16 for a in alladdr}),'aggregate_unique_2m_pages':len({a>>21 for a in alladdr}),'aggregate_unique_128b_lines':len({a>>7 for a in alladdr})}
(base/f'{label}_full_scope_audit.json').write_text(json.dumps(r,indent=2,sort_keys=True)+'\n');print(json.dumps(r,sort_keys=True))
if not full:raise SystemExit(1)
