"""CPU-only postprocessing of already collected data."""
from pathlib import Path
import json,sqlite3,collections
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'docs/ai_workload_research/runs/QWEN_DECODE_COST_MEMORY_MECHANISM_109_V9'
def main():
 p=OUT/'TIMELINE_ANALYSIS.json';a=json.loads(p.read_text())
 db=sqlite3.connect('file:'+str(OUT/'.private/NSYS/trace.sqlite')+'?mode=ro',uri=True);db.row_factory=sqlite3.Row
 strings={v['id']:v['value'] for v in db.execute('select * from StringIds')}
 nv=[dict(v) for v in db.execute('select * from NVTX_EVENTS')]
 for v in nv:v['label']=v.get('text') or strings.get(v.get('textId'),'')
 for item in a['requests']:
  candidates=[v for v in nv if item['point'] in v['label'] and v.get('end') and v['label'].startswith('V9_REQUEST')]
  if len(candidates)!=1:continue
  rr=candidates[0];groups=collections.defaultdict(lambda:[0,0])
  for v in db.execute('select * from CUPTI_ACTIVITY_KIND_RUNTIME'):
   if rr['start']<=v['start'] and v['end']<=rr['end']:
    name=strings.get(v['nameId'],str(v['nameId']));groups[name][0]+=1;groups[name][1]+=v['end']-v['start']
  item['CPU_API_groups']=[dict(name=k,count=v[0],summed_ms=v[1]/1e6) for k,v in sorted(groups.items(),key=lambda x:x[1][1],reverse=True)]
 p.write_text(json.dumps(a,indent=2)+'\n')
 p=OUT/'HARDWARE_COUNTERS.json';a=json.loads(p.read_text());m=a['metrics']
 def value(k):return float(m[k]['value'].replace(',',''))
 read=value('dram__bytes_read.sum');duration=value('gpu__time_duration.sum')
 a['parsed_DRAM_read_bytes']=int(read);a['parsed_duration_ns']=duration
 a['replayed_node_read_GB_s']=read/duration
 a['read_over_model_QKV_weight_bytes']=read/a['model_QKV_weight_bytes']
 p.write_text(json.dumps(a,indent=2)+'\n')
if __name__=='__main__':main()
