"""Read only closed accepted application summaries once; no science/Native changes."""
from pathlib import Path
import gzip,json,hashlib
PREFIXES=('EPL2TVDV3|METADATA_COST|','EPL2TVDV2|SUMMARY|','EPL2ROV1|SUMMARY|','EPL2ROP5|ADMISSION|')
COUNTERS={
'EPL2TVDV3|METADATA_COST|':['frontend_cam_queries','completion_cam_queries','indexed_wb_accept','indexed_rollback','native_install_commits','native_promotion_commits'],
'EPL2TVDV2|SUMMARY|':['clean_installs','dirty_installs','read_responses','dirty_forward_responses','served_sectors','served_sector_bytes','promotions','retention_slot_cycles','clean_retention_slot_cycles','total_retention_slot_cycles','lookup_wait_cycles','wb_wait_cycles','bank_wait_cycles','icnt_wait_cycles','directory_queries'],
'EPL2ROV1|SUMMARY|':['accepted_global_reads','accepted_oracle_candidates','accepted_ro','transactions','merges','detached','lower_sectors','concurrent_duplicate_sectors','responses','ro_bank_fill_ops','ro_bank_response_ops'],
'EPL2ROP5|ADMISSION|':['activations','native_before_activation']}
def read(p):return json.loads(Path(p).read_bytes())
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb')as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def collect(case,spec,row,control):
 assert row['state']=='CLOSED_ACCEPTED'
 done=read(row['done_ref']['path']);raw=done['raw_compressed_ref'];cache=Path(control)/'CLOSED_COUNTERS';cache.mkdir(exist_ok=True);path=cache/(case+'.json')
 if path.exists():
  r=read(path);assert r['raw_compressed_ref']==raw;return r
 assert sha(raw['path'])==raw['sha256'],'closed raw SHA changed'
 groups={k:{}for k in PREFIXES};line_counts={k:0 for k in PREFIXES}
 with gzip.open(raw['path'],'rt',encoding='utf-8',errors='strict')as f:
  for line in f:
   if not line.startswith(PREFIXES):continue
   key=next(k for k in PREFIXES if line.startswith(k));d={}
   for field in line.rstrip('\n').split('|')[2:]:
    if '='not in field:continue
    k,v=field.split('=',1);assert k not in d,'duplicate counter key'
    d[k]=v
   assert 'slice'in d and d['slice'].isdigit()
   sliceid=int(d['slice']);assert 0<=sliceid<64
   groups[key][sliceid]=d;line_counts[key]+=1
 out={}
 for key,by in groups.items():
  if not by:out[key]=dict(status='NOT_EMITTED_NO_SYNTHETIC_ZERO',last_per_slice={},emitted_lines=line_counts[key]);continue
  assert set(by)==set(range(64)),'incomplete final slice population'
  totals={}
  for name in COUNTERS[key]:
   assert all(name in d and d[name].isdigit()for d in by.values()),'counter missing or noninteger'
   totals[name]=sum(int(d[name])for d in by.values())
  out[key]=dict(status='FINAL_CUMULATIVE64_SLICE_SUMMARIES',emitted_lines=line_counts[key],totals=totals,last_per_slice={str(k):v for k,v in sorted(by.items())})
 result=dict(schema='V5_READONLY_FINAL_CUMULATIVE_MECHANISM_SUMMARY_V1',cohort=case,source_identity=spec['source_identity'],input_identity_sha256=spec['input_identity_sha256'],raw_compressed_ref=raw,accepted_point_ref=row['accepted_point_ref'],groups=out,semantics='last cumulative summary per slice; never sum repeated per-kernel cumulative snapshots',cold_bypass_counter='NOT_EXPORTED_BY_FROZEN_A_SOURCE; compare observed frontend query totals, do not invent exact per-access bypass attribution',scientific_actor=False)
 path.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n');return result
