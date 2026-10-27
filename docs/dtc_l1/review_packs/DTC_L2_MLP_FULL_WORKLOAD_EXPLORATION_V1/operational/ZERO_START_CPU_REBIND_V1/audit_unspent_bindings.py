from pathlib import Path as P
import importlib.util,json,hashlib,datetime
R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1');B=P(__file__).parent
sp=importlib.util.spec_from_file_location('readonly_cpu_res',R/'tools/l2_resources.py');res=importlib.util.module_from_spec(sp);sp.loader.exec_module(res)
read=lambda p:json.loads(P(p).read_bytes());q=read('/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/NATIVE_SCIENCE_REGISTRY.json')['registered_future_requests']['DTC_L2_MLP_FULL_WORKLOAD_EXPLORATION_20261027_V1'];claims=read(R/'control/POOL_DISPATCH_RESERVATIONS.json')['claims'];sample=res.sample_system();legal=res.cpu_candidates(sample,claims,None);rows=[]
for c in q['admitted_specs']:
 db=R/'control/dispatch_bindings'/(c+'.json');ip=R/'control/qualification_ledger'/(c+'.INTENT.json')
 if c in q['consumed']or c in claims or ip.exists()or not db.exists():continue
 b=read(db);occupied=[{k:p.get(k)for k in ['pid','start_ticks','cpus','cmdline']}for p in sample.get('observed_affinity_claims',[])if b['host_cpu']in p['cpus']]
 rows.append(dict(cohort=c,old_cpu=b['host_cpu'],old_binding_sha256=hashlib.sha256(db.read_bytes()).hexdigest(),old_cpu_currently_legal=b['host_cpu']in legal,occupied_by=occupied))
out=dict(schema='READONLY_UNSPENT_STALE_CPU_BINDING_AUDIT_V1',UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),rows=rows,unspent_unclaimed_no_intent_existing_bindings=len(rows),blocked_old_cpu=sum(not x['old_cpu_currently_legal']for x in rows),legal_available_cpu_count=len(legal),legal_available_cpus=legal,production_mutations=0,model_starts=0)
(B/'READONLY_AUDIT.json').write_text(json.dumps(out,sort_keys=True,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items()if k not in['rows','legal_available_cpus']}))
