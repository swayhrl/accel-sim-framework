from pathlib import Path as P
import json,hashlib,datetime,importlib.util,statistics
R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1');B=P(__file__).parent
read=lambda p:json.loads(P(p).read_bytes());sha=lambda p:hashlib.sha256(P(p).read_bytes()).hexdigest()
q=read('/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/NATIVE_SCIENCE_REGISTRY.json')['registered_future_requests']['DTC_L2_MLP_FULL_WORKLOAD_EXPLORATION_20261027_V1'];claims=read(R/'control/POOL_DISPATCH_RESERVATIONS.json')['claims'];hist=read(R/'control/HISTORICAL_RSS.json');policy=read(R/'control/RESOURCE_POLICY.json');sp=importlib.util.spec_from_file_location('canary_readonly_resource',R/'tools/l2_resources.py');res=importlib.util.module_from_spec(sp);sp.loader.exec_module(res);sample=res.sample_system();legal=res.cpu_candidates(sample,claims,None);specs={};history={}
for c,digest in q['admitted_specs'].items():
 p=R/'control/specs'/(c+'.json');assert sha(p)==digest;specs[c]=read(p)
for c,row in q['consumed'].items():
 rp=R/'analysis'/(c+'.RESULT.json');dp=R/'control/qualification_ledger'/(c+'.DONE.json')
 if not(rp.exists()and dp.exists())or c not in specs:continue
 result=read(rp);done=read(dp);s=specs[c]
 if result.get('state')!='PASS_L2MLP_STRICT_ARCHIVE_NATIVE_RESTORE'or not result.get('proof',{}).get('performance_accepted')or done.get('stop_reason')is not None or done.get('launcher_wait_returncode')!=0:continue
 assert done==row['execution_receipt']and done['uuid']==row['uuid']
 key=tuple(s.get(k)for k in['input_digest','input_binding_sha256','cell','core_commit','framework_commit','binary_sha256']);history.setdefault(key,[]).append(dict(cohort=c,elapsed_seconds=done['elapsed_seconds'],DONE_path=str(dp),DONE_sha256=sha(dp),RESULT_path=str(rp),RESULT_sha256=sha(rp),profile=s.get('profile',s.get('downstream_profile')),cycles=result['cycles']))
rows=[]
for c,s in specs.items():
 ip=R/'control/qualification_ledger'/(c+'.INTENT.json')
 if c in q['consumed']or c in claims or ip.exists():continue
 key=tuple(s.get(k)for k in['input_digest','input_binding_sha256','cell','core_commit','framework_commit','binary_sha256']);h=history.get(key,[]);f=res.forecast(s,hist,dict(res.DEFAULT_POLICY,**policy));db=R/'control/dispatch_bindings'/(c+'.json');binding=read(db)if db.exists()else None;forecast=max(s['estimated_peak_model_RAM_bytes'],f['predicted_peak_RAM_bytes']);rows.append(dict(cohort=c,program=s['program'],cell=s['cell'],profile=s.get('profile',s.get('downstream_profile')),input_digest=s['input_digest'],canonical_spec_sha256=q['admitted_specs'][c],canonical_forecast_bytes=s['estimated_peak_model_RAM_bytes'],forecast_full_max_bytes=forecast,forecast_full_max_GiB=forecast/1024**3,predicted_actual_wall_seconds_median=statistics.median([x['elapsed_seconds']for x in h])if h else None,predicted_actual_wall_seconds_min=min([x['elapsed_seconds']for x in h])if h else None,predicted_actual_wall_seconds_max=max([x['elapsed_seconds']for x in h])if h else None,matched_strict_natural_archive_count=len(h),same_design_history=h,dispatch_binding=binding,dispatch_binding_sha256=sha(db)if binding else None,existing_binding_cpu_legal_now=binding['host_cpu']in legal if binding else None,canary_legality_at_snapshot=dict(admitted=True,unconsumed=True,unclaimed=True,no_INTENT=True)))
rows.sort(key=lambda x:(x['predicted_actual_wall_seconds_median']is None,x['predicted_actual_wall_seconds_median']or 1e99,x['forecast_full_max_bytes'],x['cohort']))
out=dict(schema='READONLY_UNSTARTED_CANARY_RANKING_V1',UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),remaining=len(rows),q_remaining=q['remaining'],unstarted_with_matched_history=sum(x['matched_strict_natural_archive_count']>0 for x in rows),legal_cpu_count=len(legal),rows=rows,selection_basis='same input+binding+CH/DH design+Core/FW/binary strict natural archived elapsed median; all targets remain registered; scheduling-only no workload scientific selection',production_mutations=0,model_starts=0)
(B/'CANARY_RANKING.json').write_text(json.dumps(out,sort_keys=True,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items()if k!='rows'}));print(json.dumps(rows[:5]))

