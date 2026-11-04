"""Readonly actual COMMITTED resource journal/postimages and old science check."""
import pathlib,json,hashlib,importlib.util,datetime,sys
sys.dont_write_bytecode=True
P=pathlib.Path;D=P(__file__).parent;A=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1');R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1');M=R/'control/operational_amendments/pending_resource_forecast_refresh_v1'
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def put(p,v):
 with p.open('x')as f:json.dump(v,f,indent=2,sort_keys=True);f.write('\n')
ap=M/'actual_install_v2/ACK.json';assert sha(ap)=='7b579e7df815fd92b6686a05190c0293e03fa5d86e602bf714cd9124ad6f2dda';ack=read(ap);assert ack['status']=='COMMITTED_UNUSED_SYRK_RESOURCE_ONLY_SAME_OWNER'and ack['new_grants']==ack['model_starts_by_callback']==0 and ack['previous_chooser_restored']is True
pp=P(ack['proposal_path']);assert sha(pp)==ack['proposal_sha256']=='0e693a07d4801edbe75f7db1d4a2e2dc5840037482daeff25531c205f5bbe16a';proposal=read(pp);helper=load('committed_resource_ro',M/'resource_refresh.py');assert sha(helper.__file__)==ack['helper_sha256']=='c4103056c90807ee72ac550ba2886e95ff4fa15996857e713f9a9ad3d6105369';helper.validate_proposal(proposal,R)
folder=M/helper.digest(helper.js(proposal));prepared=folder/'PREPARED.json';committed=folder/'COMMITTED.json';assert sha(prepared)==sha(pp)and read(prepared)==proposal and read(committed)==ack['transaction_result']==helper.receipt_for(proposal)
engine=load('committed_resource_native_ro',R/'tools/l2_native.py');q=engine.registered()[2];rows=[]
for i in proposal['items']:
 old=json.loads(i['files'][0]['old_utf8']);new=json.loads(i['files'][0]['new_utf8']);assert helper.science(old)==helper.science(new)
 assert q['admitted_specs'][i['cohort']]==i['new_spec_sha256']
 files=[]
 for f in i['files']:
  assert P(f['path']).read_bytes()==f['new_utf8'].encode()and sha(f['path'])==f['new_sha256']
  pre=folder/'preimages'/(f['old_sha256']+'.json');assert pre.read_bytes()==f['old_utf8'].encode()and sha(pre)==f['old_sha256']
  files.append(dict(path=f['path'],post_sha256=sha(f['path']),preimage_sha256=sha(pre)))
 cpu=None
 if i['DB_present']:
  oldb=json.loads(i['files'][2]['old_utf8']);newb=read(i['files'][2]['path']);assert oldb['host_cpu']==newb['host_cpu']==26;cpu=newb['host_cpu']
 rows.append(dict(cohort=i['cohort'],new_RAM=new['estimated_peak_model_RAM_bytes'],new_RSS_cap=new['limits']['max_process_tree_rss_bytes'],new_AS_cap=new['limits']['max_process_tree_vms_bytes'],same_science_and_full_IR_lineage=True,DB_CPU=cpu,files=files))
assert len(rows)==10 and sum(r['DB_CPU']is not None for r in rows)==1
preMain3=R/'control/operational_amendments/broad_shared_cpu_v1/actual_install_v2/PREIMAGE.json';oldUUIDs=read(preMain3)['old_UUIDs'];assert all(q['consumed'][c]['uuid']==u for c,u in oldUUIDs.items())
for c,u in [('E2-DTCL2MLP-ddb6806316876a85-CH-P0-V1','98d83595-84a4-43de-8e4b-472df204e8b5'),('E2-DTCL2MLP-09f94fcc7494a03b-DH-E384-IR1-V1','34bb91df-f5db-41a2-8727-a9e3eeff5ac7')]:assert q['consumed'][c]['uuid']==u
scope=read(proposal['scope_path']);negative=[]
for r in scope['rows']:
 if r['role']!='INCIDENT_RECOVERY_PERFORMANCE_TRIAL':continue
 s=read(R/'control/specs'/(r['cohort']+'.json'));lineage=s['incident_recovery_trial_lineage'];path=R/'analysis'/(lineage['original_cohort']+'.RESULT.json');assert sha(path)==lineage['original_negative_RESULT_sha256'];v=read(path);assert v.get('cycles')is None and v.get('proof',{}).get('performance_accepted')is not True and q['consumed'][lineage['original_cohort']]['uuid']==lineage['original_uuid'];negative.append(dict(cohort=lineage['original_cohort'],uuid=lineage['original_uuid'],negative_RESULT_sha256=sha(path)))
assert len(negative)==11 and q['budget']==360
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ');out=D/stamp;out.mkdir()
report=dict(schema='E_ACTUAL_SYRK_RESOURCE_COMMIT_POSTCHECK_V1',status='PASS_COMMITTED_POSTIMAGES_AND_OLD_SCIENCE_PRESERVED',UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),ACK_sha256=sha(ap),proposal_sha256=sha(pp),PREPARED_sha256=sha(prepared),COMMITTED_sha256=sha(committed),journal_directory=str(folder),rows=rows,old_UUID_baseline_count=len(oldUUIDs),old_UUID_baseline_sha256=sha(preMain3),all_old_UUIDs_preserved=True,old_incident_negatives=negative,all_11_original_negative_SHA_UUID_preserved=True,current_budget=q['budget'],current_remaining=q['remaining'],current_consumed=len(q['consumed']),observer_models_started=0,observer_new_grants=0,observer_production_changes=0,actual_new_physics_qualified=False)
put(out/'REPORT.json',report);put(out/'MANIFEST.json',dict(schema='E_RESOURCE_POSTCHECK_READONLY_MANIFEST_V1',source_sha256=sha(__file__),members=[dict(path=p.name,sha256=sha(p),bytes=p.stat().st_size)for p in sorted(out.iterdir())],production_changes=0))
print(json.dumps(dict(status=report['status'],directory=str(out),REPORT_sha256=sha(out/'REPORT.json'),MANIFEST_sha256=sha(out/'MANIFEST.json'),old_UUID_count=len(oldUUIDs),postimages=sum(len(r['files'])for r in rows),oldnegative_count=len(negative),remaining=q['remaining'])))
