from pathlib import Path
import importlib.util,json,hashlib,copy
P=Path('/root/data/dtc_stage_iia_first16_20261104_v1/tools/stage2_resources.py');O=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_stage_iia_first16_execution_20261104_v1/agents/C');sp=importlib.util.spec_from_file_location('C_private_resource',P);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);G=m.G;M=m.M;p=m.policy();q={'reserved_write_bytes':2560*M};spec={'cohort':'CPU_FIXTURE'}
S={'monotonic':2.,'host_MemAvailable_bytes':100*G,'cgroup_effective_headroom_bytes':90*G,'native_free_bytes':12*G,'free_inodes':200000,'host_pswpout_pages':0,'host_oom_kill_count':0,'cgroup_memory_events':{'oom':0,'oom_kill':0,'max':0},'cgroup_swap_current_bytes':0,'page_size':4096,'cpu_pressure':{'full':{'avg10':0}},'memory_pressure':{'some':{'avg10':0},'full':{'avg10':0}},'io_pressure':{'full':{'avg10':0}},'host_memory_pressure':{'some':{'avg10':0},'full':{'avg10':0}},'host_cpu_pressure':{'full':{'avg10':0}},'host_io_pressure':{'full':{'avg10':0}}};PREV=copy.deepcopy(S);PREV['monotonic']=1.
b={'peer_reservations':[{'request':m.STAGE1_REQ,'reserved_write_bytes':24*G},{'request':m.REQ,'reserved_write_bytes':2560*M},{'request':'OTHER','reserved_write_bytes':G}],'required_free_bytes':5*G+24*G+2560*M+G,'reserved_additional_live_and_candidate_RAM_bytes':0,'per_scope_write_ceiling_pass':{'OLD':True},'known_remaining_writes_by_request':{}}
st={'projected_write_bytes':G,'additional_RAM_bytes':0,'projection_within_registered_ceiling':True};own={'projected_write_bytes':256*M,'actual_unarchived_output_bytes':256*M,'additional_RAM_bytes':4*G,'ram':[],'writes':[],'projection_within_registered_ceiling':True};rows=[]
def call(mut=None,fresh=True,mutown=None):
 s=copy.deepcopy(S);o=copy.deepcopy(own)
 if mut:mut(s)
 if mutown:mutown(o)
 return m._evaluate(spec,fresh,s,PREV,b,st,o,q,p)
def case(n,d,test):rows.append({'case':n,'PASS':bool(test(d)),'decision':{k:d[k] for k in ['physical_RAM_pass','physical_disk_pass','admission_disk_pass','pressure_pause_new','required_free_bytes','policy_scope']}})
case('CleanAdmission',call(),lambda d:d['physical_RAM_pass']and d['physical_disk_pass'])
case('ExactStaticReservationReplacement',call(),lambda d:d['required_free_bytes']==7*G+256*M)
for name,mut in [('LowHost',lambda s:s.update(host_MemAvailable_bytes=G)),('LowCgroup',lambda s:s.update(cgroup_effective_headroom_bytes=G)),('HostMemoryPSI',lambda s:s['host_memory_pressure']['full'].update(avg10=.75)),('CgroupMemoryPSI',lambda s:s['memory_pressure']['full'].update(avg10=1)),('HostOOM',lambda s:s.update(host_oom_kill_count=1)),('CgroupOOM',lambda s:s['cgroup_memory_events'].update(oom_kill=1)),('CgroupSwap',lambda s:s.update(cgroup_swap_current_bytes=128*M)),('ActiveHostSwap',lambda s:s.update(host_pswpout_pages=128*M//4096))]:
 case(name+'HoldsNewAdmission',call(mut),lambda d:not d['physical_RAM_pass']and d['pressure_pause_new'])
 case(name+'DoesNotStopHealthyRuntime',call(mut,fresh=False),lambda d:d['physical_RAM_pass']and d['physical_disk_pass']and d['pressure_pause_new'])
case('ProjectedRAMGrowthHoldsAdmission',call(mutown=lambda o:o.update(additional_RAM_bytes=100*G)),lambda d:not d['physical_RAM_pass'])
case('RuntimeAboveFloorBelowRestoreReserveContinuesButArchiveHolds',call(lambda s:s.update(native_free_bytes=6*G),fresh=False),lambda d:d['physical_disk_pass']and not d['admission_disk_pass'])
case('FreshBelowRestoreReserveHolds',call(lambda s:s.update(native_free_bytes=6*G)),lambda d:not d['physical_disk_pass'])
case('RuntimeHard5GiBDiskStop',call(lambda s:s.update(native_free_bytes=5*G),fresh=False),lambda d:not d['physical_disk_pass'])
case('RuntimeActualOutputCeilingStop',call(fresh=False,mutown=lambda o:o.update(actual_unarchived_output_bytes=3*G)),lambda d:not d['physical_disk_pass'])
out={'schema':'DTC_STAGE_IIA_C_INDEPENDENT_CPU_RESOURCE_EVALUATION_V1','source_path':str(P),'source_sha256':hashlib.sha256(P.read_bytes()).hexdigest(),'all_PASS':all(x['PASS'] for x in rows),'cases':rows,'models_started':0,'registrations':0,'scope':'Actual production _evaluate/memory_admission/pressure functions with synthetic samples and reservation evidence; no live resources(), authority/owner mutation or model. Real peer archive-join implementation source-reviewed, not replaced in production.'};(O/'CPU_RESOURCE_EVALUATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'cases':len(rows),'allPASS':out['all_PASS'],'source_sha256':out['source_sha256'],'failures':[x for x in rows if not x['PASS']]},indent=2))
