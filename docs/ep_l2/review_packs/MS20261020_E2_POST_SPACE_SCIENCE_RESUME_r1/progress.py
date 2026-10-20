"""One bounded read-only progress observation; never schedules or accepts work."""
from pathlib import Path
import sys, json, time, os, re
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P.parents[3]/'util/ep_l2/mechanism_e'))
import coordinator as c
s=c.Coordinator().snapshot(); rows=[]
for a in s['attempts'][14:]:
    raw=Path(a['result_directory'])/'raw.log'; text=''
    if raw.exists():
        with raw.open('rb') as f:
            f.seek(max(0,raw.stat().st_size-262144)); text=f.read().decode(errors='replace')
    row=dict(id=a['attempt_id'],workload=a['identity']['workload'],profile=a.get('profile'),
             state=a['state'],raw_bytes=raw.stat().st_size if raw.exists() else 0,
             recent_window_cycle=max([int(x) for x in re.findall(r'window_end_cycle=(\d+)',text)],default=None))
    native_receipt=raw.parent/'NATIVE_EXIT.json'
    if a['state'] not in ('RESERVED','RUNNING','START_INTENT_UNRECONCILED') and native_receipt.exists():
        native=json.loads(native_receipt.read_text())
        row.update(persisted_exit_code=native['exit_code'],persisted_wait_status=native['wait_status'])
    elif a.get('process'):
        try:
            row['native_identity_matches']=c.process_identity(a['process']['pid'])==a['process']
            st=Path('/proc',str(a['process']['pid']),'stat').read_text().rsplit(')',1)[1].split()
            row.update(native_state=st[0],cpu_seconds=round((int(st[11])+int(st[12]))/os.sysconf('SC_CLK_TCK'),2))
        except (FileNotFoundError,ProcessLookupError):row['process_snapshot']='NO_LIVE_PID_NOT_EXIT_PROOF'
    rows.append(row)
report=dict(at_unix=time.time(),controller=s['controller']['state'],starts=s['actual_starts'],
            remaining=s['remaining_start_capacity'],progress=rows,resources=c.local_resources(),
            usage=c.output_usage(),accepted_pairs=[k for k,v in s['accepted_pairs'].items() if v['status']=='CURRENT_ACCEPTED'],
            raw_progress_is_not_terminal_acceptance=True)
(P/'CURRENT_PROGRESS.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
