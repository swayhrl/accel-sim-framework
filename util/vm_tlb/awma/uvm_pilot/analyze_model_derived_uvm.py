#!/usr/bin/env python3
from __future__ import annotations
import csv,json,sqlite3
from collections import Counter
from pathlib import Path
ROOT=Path('/data/c16/awma/uvm_model_derived_characterization_20260926')
def read(p):return list(csv.DictReader(p.open(),delimiter='\t'))
def write(p,rows):
 with p.open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t');w.writeheader();w.writerows(rows)
def enum(db,t):return {r[0]:r[1] for r in db.execute(f'select id,name from {t}')}
def main():
 events=[];steps=[]
 for m in read(ROOT/'RUN_MATRIX.tsv'):
  base={'point_id':m['point_id'],'pattern':m['pattern'],'layout_point':m['layout_point'],'mode':m['mode'],'status':m['status']}
  if m['status']!='COMPLETE':events.append({**base,'migration_count':'','migration_bytes':'','migration_time_ns':'','htod_bytes':'','dtoh_bytes':'','prefetch_runtime_calls':'','gpu_fault_events':'UNAVAILABLE','cpu_fault_events':'UNAVAILABLE','observability':'NOT_APPLICABLE','breakdown_json':'{}'});continue
  d=ROOT/'runs'/m['point_id'];db=sqlite3.connect(f'file:{d/"profile.sqlite"}?mode=ro',uri=True);tables={x[0] for x in db.execute("select name from sqlite_master where type='table'")};memkind=enum(db,'ENUM_CUDA_MEM_KIND');copykind=enum(db,'ENUM_CUDA_MEMCPY_OPER');mig=enum(db,'ENUM_CUDA_UNIF_MEM_MIGRATION');copies=[]
  for r in db.execute('select start,end,bytes,copyKind,srcKind,dstKind,migrationCause,virtualAddress from CUPTI_ACTIVITY_KIND_MEMCPY'):
   copies.append({'start':r[0],'end':r[1],'bytes':r[2],'copy':copykind.get(r[3],str(r[3])),'src':memkind.get(r[4],str(r[4])),'dst':memkind.get(r[5],str(r[5])),'cause':mig.get(r[6],str(r[6]))})
  strings=dict(db.execute('select id,value from StringIds'));prefetch=sum('Prefetch' in strings.get(r[4],'') for r in db.execute('select start,end,correlationId,globalTid,nameId from CUPTI_ACTIVITY_KIND_RUNTIME'))
  ranges=[]
  for st,en,txt in db.execute("select start,end,text from NVTX_EVENTS where text like 'MODEL_UVM=%' order by start"):
   ranges.append((st,en,dict(x.split('=',1) for x in txt.split(';'))))
  breakdown=Counter();htod=dtoh=0
  for c in copies:
   breakdown[(c['copy'],c['src'],c['dst'],c['cause'])]+=c['bytes'];ss,dd,ck=c['src'].upper(),c['dst'].upper(),c['copy'].upper()
   if 'UVM_HTOD' in ck or ('DEVICE' in dd and 'DEVICE' not in ss):htod+=c['bytes']
   if 'UVM_DTOH' in ck or ('DEVICE' in ss and 'DEVICE' not in dd):dtoh+=c['bytes']
  events.append({**base,'migration_count':len(copies),'migration_bytes':sum(c['bytes'] for c in copies),'migration_time_ns':sum(c['end']-c['start'] for c in copies),'htod_bytes':htod,'dtoh_bytes':dtoh,'prefetch_runtime_calls':prefetch,'gpu_fault_events':'UNAVAILABLE','cpu_fault_events':'UNAVAILABLE','observability':'MIGRATION_MEMCPY_AVAILABLE_FAULT_COUNTERS_UNAVAILABLE','breakdown_json':json.dumps({'|'.join(k):v for k,v in breakdown.items()},sort_keys=True)})
  src=read(d/'steps.tsv')
  for i,s in enumerate(src):
   cs=[]
   if i<len(ranges):st,en,_=ranges[i];cs=[c for c in copies if st<=c['start']<=en]
   steps.append({**s,'point_id':m['point_id'],'allocated_bytes':m['allocated_bytes'],'migration_count':len(cs),'migration_bytes':sum(c['bytes'] for c in cs),'migration_time_ns':sum(c['end']-c['start'] for c in cs),'gpu_fault_events':'UNAVAILABLE'})
  db.close()
 write(ROOT/'UVM_EVENT_MATRIX.tsv',events);write(ROOT/'STEPWISE_BEHAVIOR.tsv',steps)
 print(json.dumps({'points':len(events),'migration_count':sum(int(x['migration_count'] or 0) for x in events),'migration_bytes':sum(int(x['migration_bytes'] or 0) for x in events),'steps':len(steps)},sort_keys=True))
if __name__=='__main__':main()
