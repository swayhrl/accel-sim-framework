from pathlib import Path
import subprocess,json,time,os,resource,hashlib
C=Path(__file__).resolve().parent;rows=[]
def cap():os.sched_setaffinity(0,{28});os.nice(10);resource.setrlimit(resource.RLIMIT_AS,(1536<<20,1536<<20));resource.setrlimit(resource.RLIMIT_CORE,(0,0));resource.setrlimit(resource.RLIMIT_CPU,(30,30))
for mhz in [850,1275,1700]:
 binding=C/f'ro_binding_{mhz}.config';binding.write_text((C/'ro_binding.config').read_text().replace('1132.0:1132.0:1132.0:850.0',f'1132.0:1132.0:1132.0:{float(mhz)}'))
 for bypass in [0,1]:
  args=[str(C/'new_ro_modes'),'/root/data/ep_tag_capacity_scaling_20261027_v1/cpu_fixture_inputs/base.config',str(binding),str(binding),'/root/data/ep_tag_capacity_scaling_20261027_v1/cpu_fixture_inputs/commandlist.g',str(bypass)]
  t=time.monotonic();r=subprocess.run(args,capture_output=True,text=True,cwd=C,timeout=35,preexec_fn=cap,env=dict(os.environ,EPL2_LIFE_WIRE='SUMMARY_STAGE',EPL2_DETACH_DIAG='0',EPL2_TAGPRESSURE_DIAG='0',EPL2_TAG_LIFETIME='0',EP_L2_EVENT_TIMELINE='0'))
  label=f'RO_{mhz}_M{bypass}';out=C/(label+'.stdout');err=C/(label+'.stderr');out.write_text(r.stdout);err.write_text(r.stderr);p=dict(mhz=mhz,M=bypass,T=1,returncode=r.returncode,PASS=r.returncode==0,seconds=time.monotonic()-t,markers=[l for l in r.stdout.splitlines()if 'PASS'in l][-12:],stderr_tail=r.stderr[-1500:],stdout_sha256=hashlib.sha256(out.read_bytes()).hexdigest());rows.append(p);print(json.dumps(p))
x=dict(status='PASS'if all(r['PASS']for r in rows)else'PARTIAL',rows=rows,source='862376f62ab19f9a677abe31c6a422028b44fcd0',full_application_NI='NOT_MEASURED_NOT_INHERITED_FROM_SOURCE78',models_started=0)
(C/'NEW_SOURCE_RO_MODE_CPU_MATRIX.json').write_text(json.dumps(x,indent=2)+'\n')
