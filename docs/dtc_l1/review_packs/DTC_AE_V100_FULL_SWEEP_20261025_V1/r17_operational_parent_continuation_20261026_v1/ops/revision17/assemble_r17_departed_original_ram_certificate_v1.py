"""Only copies immutable observed identities into a new operational evidence certificate."""
import pathlib,json,hashlib,datetime,importlib.util
P=pathlib.Path;F=P('/root/data/dtc_failure_repair_20261025_v1');T=P('/root/data/dtc_main_v100_sweep_20261025_v1');N=P('/root/data/ep_l2_dtc_l1_native_v2');O=F/'ops/revision17';rd=lambda p:json.loads(P(p).read_bytes());sha=lambda p:hashlib.sha256(P(p).read_bytes()).hexdigest();s=importlib.util.spec_from_file_location('r17_certificate_resources',O/'admission_resource_adapter_v1.py');a=importlib.util.module_from_spec(s);s.loader.exec_module(a)
pins=[{'path':str(F/'ops/OBSERVER_OLD_ATTEMPTS_FORENSIC_V1.json'),'sha256':'2532351d1c0e218b6d8fa424cec3e902e459920c98dcf6fab3290c625a63c043'},{'path':str(F/'analysis/ORIGINAL_OBSERVER_GAP_09F94_CM_20261026T000808Z.json'),'sha256':'359518f2dc5e0431bd379293e4ba33a102df25c20a8bf98ec169d628a61488ce'}]
for p in pins:assert sha(p['path'])==p['sha256']
old=rd(pins[0]['path']);new=rd(pins[1]['path']);forensic={r['cohort']:r['uuid']for r in old['cases']};forensic[new['cohort']]=new['uuid'];assert forensic==a.ALLOWED
targets=[]
for c,uid in sorted(a.ALLOWED.items()):
 ip=T/'control/qualification_ledger'/(c+'.INTENT.json');i=rd(ip);out=T/'DTC/run/results'/uid;pp=out/'NATIVE_SIMULATOR_PID_AND_MAPS.json';lp=out/'NATIVE_LAUNCH.json';p=rd(pp);l=rd(lp);assert i['uuid']==uid and i['cohort']==c and i['output']==str(out);assert not P('/proc',str(p['pid'])).exists() and not P('/proc',str(l['launcher_pid'])).exists()
 targets.append(dict(cohort=c,uuid=uid,intent_path=str(ip),intent_sha256=sha(ip),output=str(out),PID_receipt_sha256=sha(pp),launch_receipt_sha256=sha(lp),model_pid=p['pid'],model_start_ticks=p['start_ticks'],launcher_pid=l['launcher_pid'],forensic_disposition='UNACCEPTED_MISSING_RECEIPT; no DONE created, no retry/refund'))
cert=dict(schema='R17_THREE_DEPARTED_ORIGINAL_RAM_EVIDENCE_V1',request=a.ORIGINAL,observed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),forensic_pins=pins,targets=targets,maximum_future_RAM_exclusion_bytes=12*a.G,host_floor_bytes=64*a.G,cgroup_floor_bytes=48*a.G,all_other4GiB_initial_and_LAVA96GiB_estimates_unchanged=True,scientific_receipts_created=0,authority_mutations=0,models_started=0,signals=0)
reg=rd(N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json');valid,retained=a.verified_departed(reg,cert);assert valid==a.ALLOWED and not retained;dest=O/'THREE_DEPARTED_ORIGINAL_RAM_CERTIFICATE_V1.json'
with dest.open('x')as f:json.dump(cert,f,indent=2);f.write('\n')
print(json.dumps(dict(status='READ_ONLY_CERTIFICATE_READY',path=str(dest),sha256=sha(dest),targets=len(targets),maximum_future_RAM_exclusion_GiB=12,authority_mutations=0)))
