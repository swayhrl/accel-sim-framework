import subprocess,re,time,json,pathlib,os,signal
root=pathlib.Path(os.environ['TASK_DATA']);pid=3070386
s=subprocess.check_output(['ss','-tinp'],text=True);lines=s.splitlines();seen={}
for i,l in enumerate(lines):
 if f'pid={pid},' in l and i+1<len(lines):
  m=re.search(r'bytes_received:(\d+)',lines[i+1])
  if m:seen[l.split('users:')[0].strip()]=int(m.group(1))
route=subprocess.check_output(['ip','route','get','1.1.1.1'],text=True).split();iface=route[route.index('dev')+1];counter=pathlib.Path('/sys/class/net')/iface/'statistics/rx_bytes';baseline=int(counter.read_text());initial=sum(seen.values());reserve=512*2**20
record={'interface':iface,'initial_active_resolver_socket_received_bytes':initial,'initial_rx_counter':baseline,'prior_setup_and_unobserved_connection_reserve_bytes':reserve,'cap_bytes':8*2**30,'safety_stop_threshold_bytes':int(7.75*2**30),'method':'Initial active resolver TCP receive counters + conservative 512MiB prior reserve + subsequent whole-interface receive bytes; upper bound includes TLS/SSH and any other traffic. No resolver restart.'}
(root/'raw/network_guard_initial.json').write_text(json.dumps(record,indent=2)+'\n')
while not (root/'NETWORK_GUARD_DONE').exists():
 current=int(counter.read_text());upper=initial+reserve+max(0,current-baseline);record.update(observed_additional_interface_rx_bytes=current-baseline,dependency_download_conservative_upper_bound_bytes=upper)
 (root/'raw/network_guard_latest.json').write_text(json.dumps(record,indent=2)+'\n')
 if upper>=record['safety_stop_threshold_bytes']:
  record['status']='BUDGET_STOP_DOWNLOAD_8GIB';(root/'raw/network_budget_stop.json').write_text(json.dumps(record,indent=2)+'\n')
  # Kill only dependency resolver/downloader or source-builder processes in this isolated task directory.
  for p in pathlib.Path('/proc').iterdir():
   if not p.name.isdigit():continue
   try:args=(p/'cmdline').read_bytes().replace(b'\0',b' ').decode()
   except OSError:continue
   if str(root) in args and any(x in args for x in ['uv pip compile','pip download','pip install','gpu_pipeline.sh','environment_steps.sh']):
    if int(p.name)!=os.getpid():
     try:os.kill(int(p.name),signal.SIGTERM)
     except ProcessLookupError:pass
  break
 time.sleep(1)
