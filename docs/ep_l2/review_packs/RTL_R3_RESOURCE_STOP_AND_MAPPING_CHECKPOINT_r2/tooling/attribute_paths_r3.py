from pathlib import Path
import re,gzip,json,csv,collections,argparse,hashlib
p=argparse.ArgumentParser();p.add_argument('--cost',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False);rows=[];details=[]
for mode in ('B16','S64','UNIFIED'):
 run=a.cost/mode;path=run/'mapped.v.gz';raw=gzip.decompress(path.read_bytes()) if path.exists() else (run/'mapped.v').read_bytes();toplines=[];current='';inst={}
 for l in raw.decode().splitlines(keepends=True):
  m=re.match(r'\s*module\s+(\S+)\s*\(',l)
  if m:current=m[1].lstrip('\\')
  if current=='ep_l2_slice_ctrl':toplines.append(l)
  if l.strip()=='endmodule':current=''
 top=''.join(toplines)
 for m in re.finditer(r'^\s*(\S+)\s+(\S+)\s*\(\s*\n',top,re.M):inst[m[2].lstrip('\\')]=m[1].lstrip('\\')
 def group(path):
  cellpath=path.rsplit('/',1)[0]
  if '/' not in cellpath:return 'slice_top'
  first=cellpath.split('/')[0];typ=inst.get(first,'UNKNOWN_INSTANCE:'+first)
  return next((s for s in ('ep_l2_metadata_word','ep_l2_tag_map_word','ep_l2_generation_step','ep_l2_index_mux','ep_l2_first_one','ep_l2_bank_arbiter','ep_l2_control_buffer','ep_l2_control_inverter') if s in typ),typ)
 for period in ('target_1132MHz','exploration_2ns'):
  rp=run/'sta-portable-v1'/period/'critical_paths.rpt';text=rp.read_text()
  for idx,block in enumerate(re.split(r'(?=^Startpoint:)',text,flags=re.M)):
   if not block.startswith('Startpoint:'):continue
   start=block.splitlines()[0][12:];end=re.search(r'^Endpoint: (.+)$',block,re.M)[1];slack=float(re.search(r'(-?\d+\.\d+)\s+slack\b',block)[1]);arrival=float(re.search(r'^\s*(-?\d+\.\d+)\s+data arrival time\s*$',block,re.M)[1]);sums=collections.Counter();counts=collections.Counter();cells=[]
   for line in block.splitlines():
    m=re.match(r'^\s*(.*?)\s+[\^v]\s+(\S+)\s+\(([^)]+)\)\s*$',line)
    if not m:continue
    nums=re.findall(r'-?\d+(?:\.\d+)?',m[1])
    if len(nums)<3:continue
    delay=float(nums[-2]);g=group(m[2]) if '/' in m[2] else 'port';sums[g]+=delay;counts[g]+=1;cells.append({'pin':m[2],'cell_type':m[3],'arc_delay_ns':delay,'group':g})
   row={'mode':mode,'clock':period,'path_rank':idx,'startpoint':start,'endpoint':end,'path_slack_ns':slack,'arrival_ns':arrival,'cell_arc_sum_ns':sum(sums.values()),'external_or_clock_difference_ns':arrival-sum(sums.values()),'report_sha256':hashlib.sha256(rp.read_bytes()).hexdigest()}
   details.append({**row,'module_arc_delay_ns':dict(sums),'module_cell_arc_rows':dict(counts),'actual_cell_path':cells})
   for g,v in sums.items():rows.append({**row,'module_group':g,'module_arc_delay_ns':v,'arc_rows':counts[g]})
(a.out/'CRITICAL_PATH_MODULE_ATTRIBUTION.json').write_text(json.dumps({'scope':'actual top10 setup paths from existing STA reports; cell arc delay partition by real mapped hierarchy, not separate independent module WNS or physical interconnect attribution; no STA rerun/no constraint change','paths':details},indent=2)+'\n')
with (a.out/'CRITICAL_PATH_MODULE_ATTRIBUTION.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
print(json.dumps([{k:v for k,v in d.items() if k!='actual_cell_path'} for d in details if d['path_rank']==1],indent=2))
