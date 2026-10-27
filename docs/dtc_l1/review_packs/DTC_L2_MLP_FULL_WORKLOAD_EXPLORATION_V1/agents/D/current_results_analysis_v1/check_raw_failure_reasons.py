"""Targeted closed raw sidecar only; preserve frozen parser/strict decisions."""
import pathlib,json,gzip,re,hashlib,datetime
R=pathlib.Path('/root/data/dtc_l2_mlp_exploration_20261027_v1');results=[]
for p in(R/'analysis').glob('*.RESULT.json'):
 v=json.loads(p.read_bytes())
 if v.get('state')!='PASS_L2MLP_STRICT_ARCHIVE_NATIVE_RESTORE':continue
 results.append((p,v))
selected=[(p,v)for p,v in results if v['proof']['program']=='heartwall'and v['proof']['cell']=='DH'and v['proof']['downstream_profile']in['P0','M8','M16']]
heavy=max(results,key=lambda pv:pv[1]['proof'].get('metrics',{}).get('L2_total_cache_reservation_fails',-1))
if heavy not in selected:selected.append(heavy)
rows=[]
for rp,v in selected:
 pr=v['proof'];out=R/'DTC/run/results'/v['uuid'];raw=out/'raw.log.gz';hh=hashlib.sha256()
 with raw.open('rb')as h:
  for b in iter(lambda:h.read(1024*1024),b''):hh.update(b)
 assert hh.hexdigest()==pr['raw_gzip_sha256'];uncomp=hashlib.sha256();matches=[];kernel=None;stream=None;seq=0
 with gzip.open(raw,'rb')as h:
  for line_no,b in enumerate(h,1):
   uncomp.update(b);line=b.decode()
   m=re.match(r'\s*kernel_launch_uid\s*=\s*(\d+)',line)
   if m:kernel=int(m[1]);seq+=1
   m=re.match(r'\s*kernel_stream_id\s*=\s*(\d+)',line)
   if m:stream=int(m[1])
   if'L2_cache_stats_fail_breakdown'in line:matches.append(dict(line=line_no,kernel_uid=kernel,stream_id=stream,stats_sequence=seq,text=line.rstrip()))
 assert uncomp.hexdigest()==pr['raw_uncompressed_sha256']
 rows.append(dict(program=pr['program'],cell=pr['cell'],profile=pr['downstream_profile'],input_digest=pr['input_digest'],uuid=v['uuid'],cohort=v['cohort'],cycles=v['cycles'],result_path=str(rp),result_sha256=hashlib.sha256(rp.read_bytes()).hexdigest(),raw_gzip_path=str(raw),raw_gzip_sha256=hh.hexdigest(),raw_uncompressed_sha256=uncomp.hexdigest(),strict_visible_L2_reservation_fails=pr.get('metrics',{}).get('L2_total_cache_reservation_fails'),matched_reason_lines=matches,all_closed_raw_lines_scanned=line_no))
print(json.dumps(dict(schema='DTC_L2_MLP_TARGETED_RAW_FAILURE_REASON_SIDECAR_V1',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),rows=rows,model_starts=0,strict_or_raw_modified=False,reason='Targeted distinction between not printed in raw and not extracted by frozen proof parser; positive-only printed fields, absence not zero.'),indent=2))
