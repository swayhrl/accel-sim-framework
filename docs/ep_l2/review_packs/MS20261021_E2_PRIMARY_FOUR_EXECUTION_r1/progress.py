"""Single bounded observation, no daemon/lease/scheduling/acceptance."""
from pathlib import Path
import json,sys,time,os,re
P=Path(__file__).resolve().parent;ROOT=P.parents[3];sys.path.insert(0,str(ROOT/'util/ep_l2/mechanism_e'))
import coordinator as c
s=c.Coordinator().snapshot();rows=[]
for a in s['attempts'][32:]:
 raw=Path(a['result_directory'])/'raw.log';text=''
 if raw.exists():
  with raw.open('rb') as f:f.seek(max(0,raw.stat().st_size-262144));text=f.read().decode(errors='replace')
 r=dict(attempt=a['attempt_id'],profile=a['profile'],workload=a['identity']['workload'],state=a['state'],raw_bytes=raw.stat().st_size if raw.exists() else 0,recent_window_cycle=max([int(x) for x in re.findall(r'window_end_cycle=(\d+)',text)],default=None))
 if a['state']=='RUNNING':
  try:
   r['identity_matches']=c.process_identity(a['process']['pid'])==a['process'];st=Path('/proc',str(a['process']['pid']),'stat').read_text().rsplit(')',1)[1].split();r['native_state']=st[0];r['cpu_seconds']=round((int(st[11])+int(st[12]))/os.sysconf('SC_CLK_TCK'),2)
  except (FileNotFoundError,ProcessLookupError):r['process']='ABSENT_NOT_EXIT_PROOF'
 elif (raw.parent/'NATIVE_EXIT.json').exists():n=json.loads((raw.parent/'NATIVE_EXIT.json').read_text());r.update(native_exit=n['exit_code'],wait_status=n['wait_status'])
 rows.append(r)
r=dict(at_unix=time.time(),controller=s['controller']['state'],actual=s['actual_starts'],remaining=s['remaining_start_capacity'],rows=rows,resources=c.local_resources(),usage=c.output_usage(),progress_is_not_terminal_acceptance=True)
c.write_json(P/'CURRENT_PROGRESS.json',r);print(json.dumps(r))
