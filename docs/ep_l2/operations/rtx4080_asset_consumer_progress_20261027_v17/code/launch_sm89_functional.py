
#!/usr/bin/env python3
"""CPU-only actual SM89 trace-simulator launcher.
Private fixed consumer/core/config; no CUDA workload launch and no budget/wrapper mutation.
Default 120s wall, 2M cycles, 4GiB address space, one CPU, 128MiB combined logs.
Accepted examples include exact source+aux retired-lane expectations. Custom full
indices are allowed, but completion alone never grants semantic qualification.
Unsupported: malformed/qualified0 Ada fields, mismatched predicate/active masks,
record/opcode width mismatch, multi-window raw64 PCs, nonzero ADA8 CFI.
CALL/RET target semantics, numerical GPU outputs and hardware performance are
unqualified. Constants use per-kernel cold symbolic bank+offset serialized loads.
"""
import argparse,pathlib,json,hashlib,subprocess,os,time,resource,signal,shutil,re,sys
P=pathlib.Path;HERE=P(__file__).resolve().parent
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def put(p,x):P(p).write_text(json.dumps(x,indent=2)+'\n')
def need(ok,msg):
 if not ok:raise RuntimeError(msg)
def main():
 ap=argparse.ArgumentParser(description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter)
 choice=ap.add_mutually_exclusive_group(required=True);choice.add_argument('--asset',choices=['gaussian16','cuda118-vector50k','sdk42-vector50k','cuda118-vector50k-derived','sdk42-vector50k-derived']);choice.add_argument('--trace-index',type=P,help='Complete kernelslist.g; may reach bounds; custom qualification is not implied')
 ap.add_argument('--output',type=P,required=True,help='ABSENT directory under the NAS traces root')
 ap.add_argument('--expected-retired-lane-uops',type=int,help='Optional external exact source+aux active-lane count for a custom index')
 args=ap.parse_args();pins=json.loads((HERE/'LAUNCHER_PINS.json').read_text());accepted=pins['accepted_full_examples'].get(args.asset)
 idx=P(accepted['trace_index'])if accepted else args.trace_index.resolve();need(idx.is_file(),'trace index missing')
 out=args.output.resolve();root=P(pins['NAS_output_root']).resolve();need(out!=root and root in out.parents,'output must be an absent child directory under NAS traces root');need(not out.exists(),'output exists; use a new directory')
 need(shutil.disk_usage('/').free>=5*2**30,'Native free space below 5GiB floor')
 for p in [pins['binary'],pins['core']]+pins['configs']:need(sha(p['path'])==p['sha256'],'frozen binary/core/config drift: '+p['path'])
 if accepted:
  need(sha(idx)==accepted['trace_index_sha256'],'accepted input index drift')
  for path,h in accepted['trace_file_sha256'].items():need(sha(path)==h,'accepted trace payload drift: '+path)
 out.mkdir(parents=True)
 binary=pins['binary']['path'];core=P(pins['core']['path'])
 env={'PATH':'/usr/bin:/bin','LANG':'C','LC_ALL':'C','CUDA_VISIBLE_DEVICES':'','OMP_NUM_THREADS':'1','LD_LIBRARY_PATH':str(core.parent)}
 binding=subprocess.run(['ldd',binary],env=env,capture_output=True,text=True,timeout=10)
 selected=next((l.split('=>',1)[1].split()[0]for l in binding.stdout.splitlines()if 'libcudart.so =>'in l),None)
 need(selected and P(selected).resolve()==core.resolve()and sha(selected)==pins['core']['sha256'],'dynamic loader did not resolve the pinned private core')
 put(out/'LOADER_BINDING.json',{'ldd_stdout':binding.stdout,'selected_core':selected,'selected_core_sha256':sha(selected)})
 cmd=[binary,'-config',pins['configs'][0]['path'],'-config',pins['configs'][1]['path'],'-trace',str(idx),'-gpgpu_max_cycle','2000000']
 expected=accepted['expected_retired_lane_uops']if accepted else args.expected_retired_lane_uops
 put(out/'COMMAND.json',{'argv':cmd,'env':env,'pins_sha256':sha(HERE/'LAUNCHER_PINS.json'),'trace_index_sha256':sha(idx),'accepted_asset':args.asset,'expected_retired_lane_uops':expected,'boundary':'CPU-only functional compatibility; 120s/2M cycles/4GiB/one CPU/128MiB total logs. No numerical-output, hardware/performance or unsupported CFI qualification.'})
 def limits():
  resource.setrlimit(resource.RLIMIT_CORE,(0,0));resource.setrlimit(resource.RLIMIT_AS,(4*2**30,4*2**30));resource.setrlimit(resource.RLIMIT_FSIZE,(128*2**20,128*2**20));os.sched_setaffinity(0,{min(os.sched_getaffinity(0))})
 start=time.monotonic();reason=None;observed=None
 with(out/'stdout.log').open('w')as o,(out/'stderr.log').open('w')as e:
  proc=subprocess.Popen(cmd,cwd=out,env=env,stdout=o,stderr=e,preexec_fn=limits,start_new_session=True)
  def interrupted(signum,frame):
   if proc.poll()is None:os.killpg(proc.pid,signal.SIGTERM)
   raise SystemExit(128+signum)
  signal.signal(signal.SIGINT,interrupted);signal.signal(signal.SIGTERM,interrupted)
  while proc.poll()is None:
   if observed is None:
    try:
     lines=(P('/proc')/str(proc.pid)/'maps').read_text().splitlines()
     libs={l.split()[-1]for l in lines if '/libcudart.so'in l}
     if libs:
      need(libs=={str(core.resolve())},'running process mapped a different core')
      observed={'pid':proc.pid,'proc_stat_starttime':(P('/proc')/str(proc.pid)/'stat').read_text().split()[21],'mapped_core_path':str(core.resolve()),'mapped_core_sha256':sha(core),'matching_maps_lines':[l for l in lines if '/libcudart.so'in l]}
      put(out/'ACTUAL_PROCESS_CORE_MAP.json',observed)
    except FileNotFoundError:pass
    except Exception as error:reason="PROCESS_CORE_MAP_CHECK_FAILURE:"+str(error)
   if time.monotonic()-start>120:reason='WALL_CAP'
   if sum(p.stat().st_size for p in [out/'stdout.log',out/'stderr.log'])>128*2**20:reason='COMBINED_LOG_CAP'
   if reason:
    os.killpg(proc.pid,signal.SIGTERM)
    try:proc.wait(timeout=3)
    except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL)
    break
   time.sleep(.02)
  rc=proc.wait()
 text=(out/'stdout.log').read_text();ins=[int(x)for x in re.findall('gpu_tot_sim_insn[ ]*=[ ]*([0-9]+)',text)];ctas=[int(x)for x in re.findall('ctas_completed ([0-9]+)',text)];ks=len(re.findall('kernel_launch_uid[ ]*=',text))
 checks={'rc0':rc==0,'within_wall_log_bounds':reason is None,'normal_exit':'GPGPU-Sim: *** simulation thread exiting ***'in text,'nonzero_retirement':bool(ins)and ins[-1]>0,'mapped_private_core_observed':observed is not None,'expected_lane_retirement':expected is not None and bool(ins)and ins[-1]==expected}
 if accepted:checks.update(expected_kernel_count=ks==accepted['expected_kernels'],expected_completed_ctas=bool(ctas)and ctas[-1]==accepted['expected_ctas'])
 status='PASS_ACCEPTED_EXACT_FUNCTIONAL_REPLAY'if accepted and all(checks.values())else'COMPLETED_CUSTOM_UNQUALIFIED'if not accepted and rc==0 and reason is None else'FAILED_OR_BOUNDED_INCOMPLETE'
 report={'status':status,'checks':checks,'rc':rc,'stop_reason':reason,'wall_seconds':time.monotonic()-start,'retired_active_lane_uops':ins[-1]if ins else None,'kernel_stats_count':ks,'completed_ctas':ctas[-1]if ctas else None,'actual_process_core_map':str(out/'ACTUAL_PROCESS_CORE_MAP.json')if observed else None,'output':str(out),'numerical_hardware_performance_scientific_qualification':False,'custom_source_record_conservation_qualification':False if not accepted else 'preaccepted exact input only'}
 put(out/'RESULT.json',report);print(json.dumps(report,indent=2));return 0 if status in('PASS_ACCEPTED_EXACT_FUNCTIONAL_REPLAY','COMPLETED_CUSTOM_UNQUALIFIED')else 2
if __name__=='__main__':
 try:sys.exit(main())
 except Exception as e:print(json.dumps({'status':'PRECONDITION_OR_LAUNCH_FAILURE','error':str(e)}),file=sys.stderr);sys.exit(2)
