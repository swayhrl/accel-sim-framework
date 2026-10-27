#!/usr/bin/env python3
"""Display only: C-validated EPET JSON -> ordinal VCD, UID CSV/JSON/HTML. No model."""
import sys
sys.dont_write_bytecode=True
import argparse,csv,hashlib,json,pathlib
P=pathlib.Path;ROOT=P('/root/data/ep_l2_multiworkload_event_timeline_20261027_v1/agent_b')
U64=(1<<64)-1;FIELDS=['ordinal','core_cycle','L2_edge','DRAM_edge','address','generation','aux','packet_or_requester_uid','parent_uid','slice','set','kind','domain','way','sector_mask']
def need(ok,msg):
 if not ok:raise ValueError(msg)
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def read(p):return json.loads(P(p).read_bytes(),parse_constant=lambda s:(_ for _ in()).throw(ValueError('nonfinite JSON')))
def number(x):
 need(type(x)is int or type(x)is str and x.isdigit(),'integer required');n=int(x);need(0<=n<=U64,'uint64 range');return n
def render(verified,contract,outdir):
 d=read(verified);k=read(contract);status=d.get('status','')
 need(status=='VALIDATED_EPET_WIRE_COMPONENT_ONLY_NOT_APPLICATION_ACCEPTED','exact C validated component JSON required')
 need(d.get('science_granted')is False or d.get('scientific_acceptance_granted')is False,'explicit no-authority component required')
 need(d['contract_sha256']==sha(contract)and k['record_bytes']==80 and k['schema']=='EP_L2_ENDPOINT_TIMELINE_V1','exact80-byte contract')
 out=P(outdir).resolve();need(out.is_relative_to(ROOT.resolve())and not out.exists(),'fresh output inside agent_b required')
 events={};members={};slots={};namespaces={}
 for s in d['snapshots']:
  m=s['metadata'];slot=number(m['slot']);need(slot<4 and slot not in slots,'slot cap/unique');slots[slot]={'metadata':m,'ordinals':[]}
  for src in s['events']:
   need(set(FIELDS)<=set(src),'never fill absent event fields');e={f:number(src[f])for f in FIELDS};n=e['ordinal'];need(n!=U64 and(n not in events or events[n]==e),'ordinal invalid/conflict')
   events[n]=e;namespaces[n]=src.get('generation_namespace','UNKNOWN');members.setdefault(n,set()).add(slot);slots[slot]['ordinals'].append(n)
  a=slots[slot]['ordinals'];need(a==sorted(set(a)),'recorded slot order only')
 need(len(slots)<=4,'bounded slots');ordered=[events[n]for n in sorted(events)];out.mkdir(parents=True)
 rows=[]
 for e in ordered:
  r={f:('UNKNOWN'if e[f]==U64 else str(e[f]))for f in FIELDS}
  for f in ['slice','set','way','sector_mask']:
   if e[f]==(65535 if f in ['slice','set']else 255):r[f]='UNKNOWN'
  r['kind_name']=k['kinds'][str(e['kind'])];r['generation_namespace']=namespaces[e['ordinal']]
  r['snapshot_slots']=','.join(map(str,sorted(members[e['ordinal']])));rows.append(r)
 with (out/'EVENTS.csv').open('w',newline='')as f:
  w=csv.DictWriter(f,fieldnames=FIELDS+['kind_name','generation_namespace','snapshot_slots']);w.writeheader();w.writerows(rows)
 uid={}
 for r,e in zip(rows,ordered):
  if e['packet_or_requester_uid']!=U64:uid.setdefault(str(e['packet_or_requester_uid']),[]).append(r)
 edges=[{'child':str(e['packet_or_requester_uid']),'parent':str(e['parent_uid']),'ordinal':str(e['ordinal']),'parent_retained':str(e['parent_uid'])in uid}for e in ordered if e['kind']in[9,23]and e['parent_uid']!=U64 and e['packet_or_requester_uid']!=U64]
 (out/'UID_TIMELINES.json').write_text(json.dumps({'scope':'CAPTURED_WINDOWS_ONLY','raw_sha256':d['raw_sha256'],'uids':uid,'known_creation_edges_only':edges},indent=2)+'\n')
 fields=[('capture_active',1),('reserved_known',1),('reserved_tags',5),('kind',8),('uid',64),('generation',64),('core_cycle',64),('L2_edge',64),('DRAM_edge',64)]
 ids={(slot,name):f's{slot}_{i}'for slot in slots for i,(name,width)in enumerate(fields)};actions={};states={slot:None for slot in slots}
 for slot,s in slots.items():
  for n in s['ordinals']:actions.setdefault(n,[]).append((slot,events[n]))
  if s['ordinals']:actions.setdefault(s['ordinals'][-1]+1,[]).append((slot,None))
 with (out/'SYNTHETIC_ORDINAL.vcd').open('w')as f:
  f.write('$comment X AXIS = GLOBAL NOTIFICATION ORDINAL. 1s IS ONLY A VCD FORMAT UNIT, NOT PHYSICAL SECONDS OR ns/ps. $end\n$timescale 1s $end\n$scope module windows $end\n')
  for slot in sorted(slots):
   f.write(f'$scope module slot{slot} $end\n')
   for name,width in fields:f.write(f'$var wire {width} {ids[slot,name]} {name} $end\n')
   f.write('$upscope $end\n')
  f.write('$upscope $end\n$enddefinitions $end\n')
  for n in sorted(actions):
   f.write(f'#{n}\n')
   for slot,e in actions[n]:
    v={name:U64 for name,width in fields};v.update(capture_active=0,reserved_known=0)
    if e is not None:
     st=number(slots[slot]['metadata']['set']);ways=number(slots[slot]['metadata']['ways'])
     if e['set']==st and e['kind']in[24,25]:
      r=e['aux']&0xffffffff;states[slot]=r if r<=ways else None
     elif e['set']==st and e['kind']==6 and states[slot]is not None:
      r=states[slot]+int(e['sector_mask']!=0)-int((e['aux']&15)!=0);need(0<=r<=ways,'retained mask delta/anchor inconsistent');states[slot]=r
     v.update(capture_active=1,reserved_known=int(states[slot]is not None),reserved_tags=states[slot]if states[slot]is not None else U64,kind=e['kind'],uid=e['packet_or_requester_uid'],generation=e['generation'],core_cycle=e['core_cycle'],L2_edge=e['L2_edge'],DRAM_edge=e['DRAM_edge'])
    else:states[slot]=None
    for name,width in fields:f.write('b'+('x'if v[name]==U64 else format(v[name],f'0{width}b'))+' '+ids[slot,name]+'\n')
 payload=json.dumps(rows,separators=(',',':')).replace('<','\\u003c')
 html='''<!doctype html><meta charset="utf-8"><title>Captured UID events</title><style>body{font:14px system-ui;margin:24px}aside{background:#fff3c4;padding:12px}td,th{padding:5px;text-align:left;border-bottom:1px solid #ddd}table{font:12px monospace}</style><h1>Captured UID events</h1><aside>Captured windows only. Order is recorded global ordinal, not physical ns/ps. Actual CORE/L2/DRAM counters are separate. Missing ancestry and censored spans remain unknown.</aside><p><input id="q" placeholder="Exact decimal UID"><button id="filter">Filter</button><span id="count"></span></p><table><thead id="head"></thead><tbody id="body"></tbody></table><script>const DATA=__DATA__;const C=["ordinal","core_cycle","L2_edge","DRAM_edge","kind_name","packet_or_requester_uid","parent_uid","slice","set","way","generation","snapshot_slots"];const h=document.createElement("tr");for(const c of C){const t=document.createElement("th");t.textContent=c;h.append(t)}head.append(h);function draw(){body.textContent="";const v=q.value.trim();const a=DATA.filter(e=>!v||e.packet_or_requester_uid===v||e.parent_uid===v);for(const e of a.slice(0,1000)){const r=document.createElement("tr");for(const c of C){const t=document.createElement("td");t.textContent=e[c];r.append(t)}body.append(r)}count.textContent=" "+a.length+" events (first1000 displayed; CSV contains all)"}filter.onclick=draw;draw();</script>'''.replace('__DATA__',payload)
 (out/'UID_TIMELINE.html').write_text(html)
 (out/'README.txt').write_text('Display artifacts only; no model replay, science/source qualification or acceptance.\nVCD time is recorded notification ordinal. VCD1s is a synthetic format unit, not elapsed seconds/ns/ps. SameCORE R6->7->6 remains separate steps. Real clock counters are signals.\nR is UNKNOWN until a recorded pressure anchor; exact retained same-set old/new mask deltas may update it. Every slot becomes inactive/unknown at its endpoint. No unobserved gap or ancestry is invented.\nParent links use only actual RO_LOWER_CREATE/PACKET_SPLIT source links. Generation namespaces are distinct; RO_DETACH aux is a third RO Tag-binding generation and is never a parent UID or payload slot.\nUIDs/generations are decimal strings in browser views to avoid JavaScript precision loss.\n')
 r={'status':'OFFLINE_DISPLAY_ONLY_NOT_SCIENTIFIC_ACCEPTANCE','verified_component_path':str(P(verified)),'verified_component_sha256':sha(verified),'raw_sha256':d['raw_sha256'],'contract_sha256':sha(contract),'events':len(ordered),'uid_count':len(uid),'known_parent_edges':len(edges),'coordinate':'recorded ordinal synthetic steps; real core/L2/DRAM counters retained','same_tick_order_preserved':True,'model_executed':False,'scientific_acceptance_granted':False,'files':{p.name:{'path':str(p),'sha256':sha(p),'bytes':p.stat().st_size}for p in out.iterdir()}}
 (out/'VIEW_MANIFEST.json').write_text(json.dumps(r,indent=2)+'\n');return r
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--verified-json',required=True);p.add_argument('--contract',required=True);p.add_argument('--out-dir',required=True);a=p.parse_args()
 try:r=render(a.verified_json,a.contract,a.out_dir);print(json.dumps({'status':r['status'],'events':r['events'],'manifest':str(P(a.out_dir)/'VIEW_MANIFEST.json')}))
 except(ValueError,KeyError,TypeError,OSError)as e:print(json.dumps({'status':'VIEW_REJECTED','reason':str(e)}),file=sys.stderr);raise SystemExit(2)
