import subprocess,json,hashlib,re,datetime,os
from pathlib import Path
O=Path(__file__).parent;probes=[]
for cmd in [['crontab','-l'],['systemctl','list-timers','--all','--no-pager'],['tmux','list-panes','-a','-F','#{pane_pid}\t#{pane_current_path}']]:
 try:
  r=subprocess.run(cmd,capture_output=True,timeout=3);b=r.stdout+r.stderr;paths=sorted(set(x.decode() for x in re.findall(rb'/(?:workspace|tmp|root/(?:data|share))/[A-Za-z0-9_./+@:=,~-]+',b)));probes.append(dict(command=cmd,returncode=r.returncode,stdout_bytes=len(r.stdout),sha256=hashlib.sha256(b).hexdigest(),path_references=paths,error_category='NO_LOCAL_CRONTAB' if b'no crontab' in b.lower() else None))
 except (OSError,subprocess.TimeoutExpired) as e:probes.append(dict(command=cmd,status=type(e).__name__))
for p in [Path('/etc/crontab'),*Path('/etc/cron.d').glob('*')]:
 if p.is_file() and p.stat().st_size<65536:
  b=p.read_bytes();probes.append(dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),c16_marker=b'c16' in b.lower(),paths=sorted(set(x.decode() for x in re.findall(rb'/(?:workspace|tmp|root/(?:data|share))/[A-Za-z0-9_./+@:=,~-]+',b)))))
(O/'scheduled_consumer_snapshot.json').write_text(json.dumps(dict(at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),probes=probes,scope='Original174 local scheduler metadata only; remote 109/164, user UI goals and untracked plans not cleared',no_commands_started_or_changed=True),indent=2)+'\n');print('scheduler probes',[(p.get('command',p.get('path')),p.get('returncode',p.get('status')),len(p.get('path_references',p.get('paths',[])))) for p in probes])
# Exact package scripts use defaults which may be relative; collect named current checked files, no workload execution.
E=O/'evidence';references=[]
for name in ['A_c16_background_asset_supervisor.py','A_c16_local_prep.py','G_P2_PACKAGE_CONSUMPTION_RECEIPT.json','G_P3_PACKAGE_CONSUMPTION_RECEIPT.json','OLD174_MODEL_AUTHORITY.tsv','FINAL_MIGRATION_STATUS.tsv','RAW_REPLAY_CURRENT_SCOPE_AND_GATES.md']:
 p=E/name;lines=p.read_text().splitlines();hits=[]
 for i,l in enumerate(lines):
  if re.search(r'RAW_ROOT|AWQ_ROOT|file_bytes|P2_READY|P3_READY|local_path|Retain source|retain recovery source|SOURCE_RETAIN|immutable|layer streaming|exact archived|P2_TRANSFER|P3_TRANSFER',l,re.I):hits.append(dict(line=i+1,excerpt=l[:500]))
 references.append(dict(file=name,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),selected_lines=hits[:40]))
(O/'source_owner_decisive_lines.json').write_text(json.dumps(references,indent=2)+'\n')
