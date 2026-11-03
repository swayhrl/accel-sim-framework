from pathlib import Path
import importlib.util,json,copy,hashlib,types
P=Path('/root/data/dtc_stage_iia_first16_20261104_v1/tools/stage2_guard_policy.py');O=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_stage_iia_first16_execution_20261104_v1/agents/C');sp=importlib.util.spec_from_file_location('C_independent_stage2_policy',P);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);G=m.GIB;START=10**9
class R:
 def __init__(self,b,o):self.first=b
BASE={'monotonic_ns':START,'host_MemAvailable_bytes':20*G,'cgroup':{'memory.max':str(30*G),'memory.current':str(5*G),'memory.swap.current':'0','events':{'oom':0,'oom_kill':0,'max':0}},'pressure':{'memory':{'full':{'avg10':0}},'io':{'full':{'avg10':0}}},'cgroup_pressure_parsed':{'memory':{'full':{'avg10':0}},'io':{'full':{'avg10':0}}},'pswpout':0,'disk_free_bytes':20*G,'output_filesystem_device':2128,'host_oom_kill':0}
SAFE={k:True for k in m.SAFETY_KEYS};IO={'known_scope':True,'harm_detected':False,'conservative_host_episode_profile_accepted':True};rows=[]
def call(mut=None,safe=None,io=None,prog=None):
 p=m.RuntimePolicyB(copy.deepcopy(BASE),'/fake/cpu-only',resource_module=types.SimpleNamespace(Runtime=R),started_ns=START,opt_in=True);x=copy.deepcopy(BASE);x['monotonic_ns']=START+10*10**9
 if mut:mut(x)
 pr={'mono_ns':x['monotonic_ns'],'end':'NONE','completed':1} if prog is None else prog(x)
 return p.observe(x,0,0,progress=pr,safety_checks=safe if safe is not None else SAFE,io_impact=io if io is not None else IO)
def case(n,d,pred):rows.append({'case':n,'PASS':bool(pred(d)),'decision':d})
case('Healthy',call(),lambda d:d['decision']=='CONTINUE')
case('LowHostHeadroomWarnNoStop',call(lambda x:x.update(host_MemAvailable_bytes=G)),lambda d:d['decision']=='WARN' and not d['stop_reasons'])
case('LowCgroupHeadroomWarnNoStop',call(lambda x:x['cgroup'].update({'memory.current':str(29*G)})),lambda d:d['decision']=='WARN' and not d['stop_reasons'])
case('HostMemoryPSIWarnNoStop',call(lambda x:x['pressure']['memory']['full'].update(avg10=2)),lambda d:d['decision']=='WARN' and not d['stop_reasons'])
case('CgroupMemoryPSIWarnNoStop',call(lambda x:x['cgroup_pressure_parsed']['memory']['full'].update(avg10=2)),lambda d:d['decision']=='WARN' and not d['stop_reasons'])
case('HostOOMWarnNoStop',call(lambda x:x.update(host_oom_kill=1)),lambda d:d['decision']=='WARN' and not d['stop_reasons'])
case('SwapWarnNoStop',call(lambda x:x.update(pswpout=1)),lambda d:d['decision']=='WARN' and not d['stop_reasons'])
for key in ['oom','oom_kill','max']:
 case('CgroupEventWarnNoStop:'+key,call(lambda x,k=key:x['cgroup']['events'].update({k:1})),lambda d:d['decision']=='WARN' and not d['stop_reasons'])
case('CgroupSwapWarnNoStop',call(lambda x:x['cgroup'].update({'memory.swap.current':'4096'})),lambda d:d['decision']=='WARN' and not d['stop_reasons'])
case('MissingRequiredCgroupEventsStop',call(lambda x:x['cgroup'].pop('events')),lambda d:d['decision']=='STOP')
case('Disk5GiBHardStop',call(lambda x:x.update(disk_free_bytes=5*G)),lambda d:d['decision']=='STOP')
case('OutputDeviceDriftHardStop',call(lambda x:x.update(output_filesystem_device=999)),lambda d:d['decision']=='STOP')
for k in SAFE:
 s=dict(SAFE);s[k]=False;case('SafetyHardStop:'+k,call(safe=s),lambda d:d['decision']=='STOP' and bool(d['stop_reasons']))
case('UnknownIOHardStop',call(io={}),lambda d:d['decision']=='STOP')
case('MalformedMemorySampleHardStop',call(lambda x:x['pressure']['memory']['full'].update(avg10=float('nan'))),lambda d:d['decision']=='STOP')
case('FutureProgressHardStop',call(prog=lambda x:{'mono_ns':x['monotonic_ns']+1,'end':'NONE','completed':1}),lambda d:d['decision']=='STOP')
case('LimitProducerHardStop',call(prog=lambda x:{'mono_ns':x['monotonic_ns'],'end':'LIMIT','completed':1}),lambda d:d['decision']=='STOP')
p=m.RuntimePolicyB(copy.deepcopy(BASE),'/fake',resource_module=types.SimpleNamespace(Runtime=R),started_ns=START,opt_in=True)
for t in range(10,601,10):
 x=copy.deepcopy(BASE);x['monotonic_ns']=START+t*10**9;d=p.observe(x,0,0,progress={'mono_ns':x['monotonic_ns'],'end':'NONE','completed':1},safety_checks=SAFE,io_impact=IO)
case('FreshSameValueDoesNotReset600sRetirement',d,lambda d:d['decision']=='STOP' and 'NO_SEMANTIC_RETIREMENT_600S' in d['stop_reasons'])
out={'schema':'DTC_STAGE_IIA_C_INDEPENDENT_CPU_POLICY_FIXTURES_V1','tested_policy_source':str(P),'tested_policy_sha256':hashlib.sha256(P.read_bytes()).hexdigest(),'new_models':0,'registrations':0,'real_resource_module_or_output_used':False,'scope':'Pure policy API fake Runtime baseline. Does not prove scheduler actually pauses, real receiver, integration or final source version.','all_PASS':all(x['PASS'] for x in rows),'cases':rows};(O/'CPU_POLICY_FIXTURES_FINAL_CANDIDATE.json').write_text(json.dumps(out,indent=2)+'\n');print('cases',len(rows),'allpass',out['all_PASS'],'sha',out['tested_policy_sha256'])

