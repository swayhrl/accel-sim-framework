"""Strict read-only mapper for one exact foreign PHYS768 first4 resource contract.
No source/registry/budget/process mutation. Only loaded EP resource module objects are wrapped.
"""
from pathlib import Path
import copy,hashlib,json,os,importlib.util
HERE=Path(__file__).resolve().parent;ROOT=Path('/root/data/dtc_perf_first_parallel_exploration_20261104_v1');REQUEST='DTC_PERF_FIRST_PHYS768_FIRST4_20261104_V1';M=1<<20
PINS=HERE/'EXACT_FOREIGN_AUTHORITY_SOURCE_PINS.json'
def need(v,m):
 if not v:raise ValueError(m)
def read(p):return json.loads(Path(p).read_bytes())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def pin_source_contract(q):
 pins=read(PINS)
 need(q.get('request')==REQUEST and q.get('schema')=='DTC_PERF_FIRST_PHYS768_FIRST4_REGISTERED_REQUEST_V1','foreign request schema')
 need(q['budget']==4 and q['remaining']==4-len(q['consumed'])and q['admitted_specs']==pins['admitted_specs'],'exact first4 scope/budget arithmetic')
 need(q['execution_plan_sha256']==pins['plan_sha256'],'foreign plan identity')
 for r in pins['pins']:need(sha(r['path'])==r['sha256'],'foreign source/plan/spec pin drift '+r['path'])
 plan=read(ROOT/'control/EXECUTION_PLAN.json');need(plan['request']==REQUEST and plan['no_extensions']is True and plan['expected_new_starts']==4 and set(plan['initial_native_qualification_cohorts'])==set(q['admitted_specs']),'exact first4 plan')
 need(plan['parent_pid']==q['owner_pid']and plan['parent_start_ticks']==q['owner_start_ticks'],'foreign controller generation binding')
 need(q['controller_path']==str(ROOT/'tools/perf4_ops.py')and sha(q['controller_path'])==q['controller_sha256'],'foreign controller SHA')
 return plan,read(ROOT/'control/RESOURCE_POLICY.json')
def growth(estimate,hard,rss):
 need(all(type(x)is int and x>=0 for x in [estimate,hard,rss])and estimate<=hard,'invalid foreign growth inputs')
 return max(0,min(hard,max(estimate,rss))-rss)
def future_writes(cap,used,done=False):
 need(type(cap)is int and cap>0 and type(used)is int and 0<=used<=cap,'foreign output cap/used bound')
 return used+16*M if done else max(0,2*cap-used)
def cpu_siblings(cpu):
 p=Path('/sys/devices/system/cpu')/('cpu'+str(cpu))/'topology/thread_siblings_list';out=set()
 for token in p.read_text().strip().split(','):
  if '-'in token:a,b=map(int,token.split('-'));out.update(range(a,b+1))
  else:out.add(int(token))
 return sorted(out)
def generation_check(pid,start):
 p=Path('/proc')/str(pid)
 if not p.exists():return False
 stat=(p/'stat').read_text().rsplit(')',1)[1].split();need(int(stat[19])==start,'foreign PID generation changed; no guessing')
 return stat[0]not in ['Z','X']
def map_request(q,m,existing):
 plan,policy=pin_source_contract(q);cp=ROOT/'control/POOL_DISPATCH_RESERVATIONS.json';cp_sha=sha(cp);claims=read(cp)['claims'];need(set(claims)<=set(q['admitted_specs']),'foreign unadmitted claim')
 owner=m.process(q['owner_pid'],q['owner_start_ticks']);need(owner['live'],'foreign controller lease not live')
 ram=[];writes=[];models=[];cpus=[];cpu_claims=[];evidence=[];binary_checked={}
 for c in sorted(set(q['consumed'])|set(claims)):
  s=read(ROOT/'control/specs'/(c+'.json'));need(s['request']==REQUEST and s['cohort']==c and s['profile']=='PHYS768_TAG64x8','foreign spec request/profile')
  cap=s['limits']['max_result_directory_bytes'];hard=s['limits']['max_process_tree_rss_bytes'];estimate=s['estimated_peak_model_RAM_bytes'];need(0<estimate<=hard,'foreign estimate bound')
  claim=claims.get(c);row=q['consumed'].get(c);pr=dict(live=False,RSS_bytes=0,PSS_bytes=0);used=0;done=False;archived=False;cpu=None;kind='UNCONSUMED_CLAIM'
  if claim:
   need(claim['predicted_peak_RAM_bytes']==estimate and claim['RAM_cap_bytes']==hard and claim['result_cap_bytes']==cap and claim['workload']==s['workload'],'foreign claim/spec resource mismatch');cpu=claim['host_cpu']
  if row:
   ip=Path(row['intent']);need(ip==ROOT/'control/qualification_ledger'/(c+'.INTENT.json')and sha(ip)==row['intent_sha256'],'foreign exact INTENT pin');intent=read(ip);out=ROOT/'DTC/run/results'/row['uuid'];need(intent['uuid']==row['uuid']and intent['cohort']==c and intent['output']==str(out)and intent['spec_sha256']==q['admitted_specs'][c],'foreign consumed UUID/output/spec binding')
   need(intent['batch_lease_pid']==q['owner_pid']and intent['batch_lease_start_ticks']==q['owner_start_ticks']and intent['l2_mlp_execution_binding']['request']==REQUEST and intent['l2_mlp_execution_binding']['plan_sha256']==q['execution_plan_sha256'],'foreign lease/plan intent binding')
   db=ROOT/'control/dispatch_bindings'/(c+'.json');binding=read(db);need(sha(db)==intent['dispatch_binding_sha256']and binding['canonical_spec_sha256']==q['admitted_specs'][c]and binding['cohort']==c,'foreign dispatch binding')
   if cpu is not None:need(cpu==binding['host_cpu'],'foreign claim/binding CPU mismatch')
   cpu=binding['host_cpu'];mp=out/'NATIVE_SIMULATOR_PID_AND_MAPS.json';ident=read(mp)if mp.exists()else None
   if ident:
    pid,start=ident['pid'],ident['start_ticks'];live=generation_check(pid,start);pr=m.process(pid,start)
    if live:
     proc=Path('/proc')/str(pid);argv=[x.decode()for x in(proc/'cmdline').read_bytes().split(b'\0')if x];expected=[str(ROOT/'common-lib/ld-linux-x86-64.so.2'),'--inhibit-cache','--library-path',str(ROOT/'DTC/env/lib'),*s['native_simulator_argv']]
     need(argv==expected,'foreign loader/model/config argv mismatch');need(str(Path(os.readlink(proc/'cwd')).resolve())==str(out.resolve()),'foreign actual cwd/UUID mismatch');need(sorted(os.sched_getaffinity(pid))==[cpu]==ident['host_cpu_affinity_actual'],'foreign actual CPU binding mismatch')
     need(ident['dispatch_binding_sha256']==sha(db)and ident['mnt_namespace']==s['execution_mnt_namespace']==os.readlink(proc/'ns/mnt'),'foreign PID-map binding/domain mismatch')
     need(Path(os.readlink(proc/'exe')).resolve()==(ROOT/'common-lib/ld-linux-x86-64.so.2').resolve(),'foreign loader executable mismatch')
     binary=s['native_simulator_argv'][0]
     if binary not in binary_checked:binary_checked[binary]=sha(binary)
     need(binary_checked[binary]==s['binary_sha256'],'foreign model ELF pin drift');need(any(len(x.split())>=6 and x.split()[-1]==binary for x in(proc/'maps').read_text().splitlines()),'foreign model ELF not mapped')
     asline=next(x for x in(proc/'limits').read_text().splitlines()if x.startswith('Max address space'));need(asline.split()[3:5]==[str(s['limits']['max_process_tree_vms_bytes'])]*2,'foreign actual AS bound mismatch')
     need(pr['RSS_bytes']<=hard,'foreign RSS over own hard cap; admission HOLD')
     pr['cgroup']=(proc/'cgroup').read_text().strip();pr['boot_id']=Path('/proc/sys/kernel/random/boot_id').read_text().strip();models.append(dict(request=REQUEST,cohort=c,uuid=row['uuid'],pid=pid,start_ticks=start,CPU_affinity=[cpu],RSS_bytes=pr['RSS_bytes'],cgroup=pr['cgroup']));kind='LIVE_FOREIGN_MODEL'
    else:kind='CONSUMED_GENERATION_ENDED_PENDING_DONE'
   done=bool(row.get('execution_receipt'))
   if done:
    dp=ip.with_name(c+'.DONE.json');need(read(dp)==row['execution_receipt']==read(out/'NATIVE_EXIT.json')and row['execution_receipt']['uuid']==row['uuid']and not pr['live'],'foreign exact DONE/generation closure');kind='DONE_UNARCHIVED'
   archived=m.archived(ROOT,c,row)
   if archived:need(done and not pr['live'],'foreign archived while live');continue
   used=m.size(out)
  else:need(claim is not None,'foreign unconsumed without exact claim')
  need(type(cpu)is int and cpu in plan['new_dispatcher_cpu_allowance'],'foreign CPU outside owned allowance');siblings=cpu_siblings(cpu);cpus+=siblings;cpu_claims.extend(dict(request=REQUEST,cohort=c,cpu=reserved,state='FOREIGN_CPU_OR_SMT_RESERVED',actual_claim_cpu=cpu)for reserved in siblings)
  growth_bytes=0 if done else growth(estimate,hard,pr['RSS_bytes']);remaining=future_writes(cap,used,done)
  ram.append(dict(request=REQUEST,cohort=c,kind=kind,additional_RAM_bytes=growth_bytes,estimate_bytes=estimate,hard_bytes=hard,**pr));writes.append(dict(request=REQUEST,cohort=c,bytes=remaining,already_written_bytes=used,kind='EXACT_FUTURE_SOURCE_REMAINDER_PLUS_RESTORE',formula='2*cap-used while active; used+16MiB after DONE; archived zero'))
  evidence.append(dict(cohort=c,uuid=row['uuid']if row else None,host_cpu=cpu,SMT_exclusions=siblings,estimated_RAM_bytes=estimate,hard_RSS_bytes=hard,current_RSS_bytes=pr['RSS_bytes'],additional_RAM_bytes=growth_bytes,output_cap_bytes=cap,current_output_bytes=used,future_write_bytes=remaining,live=pr['live']))
 # Reuse original controller growth formula, subtracting any already-accounted same PID/generation.
 prior=m._phys4_prior_resource_module;extra,margin=prior.controller_margin(owner,policy,existing+ram)
 if extra:ram.append(dict(request=REQUEST,kind='SHARED_CONTROLLER_GROWTH_DEDUP_PID_GENERATION',additional_RAM_bytes=extra,pid=owner['pid'],start_ticks=owner['start_ticks'],RSS_bytes=owner['RSS_bytes']))
 if q.get('state')not in ['COMPLETE','CLOSED','SEALED']:writes.append(dict(request=REQUEST,kind='EXACT_FOREIGN_FUTURE_METADATA',bytes=policy['metadata_reserve_bytes']))
 need(sum(x['bytes']for x in writes)<=q['reserved_write_bytes']==policy['own_registered_write_ceiling_bytes'],'foreign derived future writes exceed advertised ceiling')
 need(sha(cp)==cp_sha,'foreign claims transitioned; resample')
 return dict(ram=ram,writes=writes,models=models,reserved_cpus=sorted(set(cpus)),CPU_claims=cpu_claims,evidence=evidence,controller_extra_growth_bytes=extra,controller_total_margin_bytes=margin,pin=dict(path=str(cp),sha256=cp_sha,claims=len(claims)),confirmed_foreign_host_floor_bytes=policy['min_host_headroom_bytes'],confirmed_foreign_cgroup_floor_bytes=policy['min_cgroup_headroom_bytes'],confirmed_foreign_native_floor_bytes=policy['native_safety_floor_bytes'],advertised_lifetime_write_ceiling_bytes=q['reserved_write_bytes'],derived_future_write_bytes=sum(x['bytes']for x in writes),current_used_bytes_not_added_again=True)

def attach(resource):
 original_runtime=resource.runtime;original_snapshot=resource.snapshot
 def runtime():
  v=original_runtime();factory=v.qualified_math
  def qualified():
   h=factory();basefactory=h.base
   def base():
    m=basefactory();foreign=m.foreign_commitments;m._phys4_prior_resource_module=resource.load(resource.PRIOR,'phys4_qualified_controller_growth',resource.PRIOR_SHA)
    def mapped(reg):
     q=reg['registered_future_requests'].get(REQUEST)
     if q is None:return foreign(reg)
     legacy=copy.deepcopy(reg);legacy['registered_future_requests'].pop(REQUEST);f=foreign(legacy)
     try:d=map_request(q,m,f['foreign_RAM_entries'])
     except Exception as ex:
      f=foreign(reg);f['foreign_metadata_errors'].append('PHYS4_STRICT_MAPPING_HOLD '+repr(ex));return f
     f['foreign_RAM_entries']+=d['ram'];f['foreign_write_entries']+=d['writes'];f['foreign_claims_pins'][REQUEST]=d['pin'];f['PHYS4_accounting']=d
     for k in ['confirmed_foreign_host_floor_bytes','confirmed_foreign_cgroup_floor_bytes','confirmed_foreign_native_floor_bytes']:f[k]=max(f.get(k,0),d[k])
     f['foreign_additional_RAM_bytes']=sum(x['additional_RAM_bytes']for x in f['foreign_RAM_entries']);f['foreign_remaining_write_bytes']=sum(x['bytes']for x in f['foreign_write_entries']);return f
    m.foreign_commitments=mapped;return m
   h.base=base;return h
  v.qualified_math=qualified;return v
 def snapshot(request):
  s=original_snapshot(request);d=s.get('PHYS4_accounting')
  if d:
   s['occupied_model_or_claim_cpus']=sorted(set(s.get('occupied_model_or_claim_cpus',[]))|set(d['reserved_cpus']));s['EP_CPU_claims']+=d['CPU_claims']
  return s
 resource.runtime=runtime;resource.snapshot=snapshot;return resource
