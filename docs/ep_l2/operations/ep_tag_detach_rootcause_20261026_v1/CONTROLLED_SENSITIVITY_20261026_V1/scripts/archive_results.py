#!/usr/bin/env python3
"""COPY_ONLY frozen primitives, private EP lease, genuine164 and portable restore proof."""
import sys
sys.dont_write_bytecode=True
import inspect,json,pathlib,fcntl,hashlib,subprocess
import experiment_runtime as v
P=pathlib.Path;BASE=v.BASE
NAS=P('/root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261026_ep_memory_path_sensitivity_v1')
def adapter(case):
 v.bind(case);B=v.B;m=v.load(BASE/'vector_result.py','ep_memory_frozen_result_primitives')
 m.ROOT=B;m.NAS=NAS;m.COHORTS={case:'.'}
 def gate(reservation=0,other_reservation=None):
  fs=json.loads(subprocess.check_output(['findmnt','-J','-T',str(NAS.parent)],text=True))['filesystems'][0]
  v.need(fs['fstype']=='fuse.sshfs' and fs['source']=='admin-wcx@10.208.130.164:/home/shared','genuine164 mapping changed')
  r=v.resources();v.need(r['consistent_snapshot'] and r['disk_pass'] and r['RAM_pass'],'COPY_ONLY resource HOLD')
  v.need(reservation<=128*v.MIB,'restore cap128MiB');return r
 m.gate=gate;source=inspect.getsource(m.archive)
 old="else:science_lock=(ROOT/'control/qualification_ledger/NATIVE_QUALIFICATION.lock').open('rb')"
 v.need(source.count(old)==1,'archive lease splice contract changed')
 source=source.replace(old,"else:science_lock=(ROOT/'control/ARCHIVE_JOB.lock').open('a+b')")
 exec(compile(source,'EP_PRIVATE_LEASE_FROZEN_COPY_ONLY_ARCHIVE','exec'),m.__dict__)
 return m
def identical_or_put(path,value):
 if path.exists():v.need(v.read(path)==value,'receipt collision '+str(path))
 else:v.put(path,value)
def archive(case):
 v.bind(case);B=v.B
 whole=(B/'control/ARCHIVE_WHOLE_OPERATION.lock').open('a+b');fcntl.flock(whole,fcntl.LOCK_EX|fcntl.LOCK_NB)
 done=v.read(v.LED/(case+'.DONE.json'));out=P(done['output']);point=v.read(out/'CURRENT_ACCEPTED_DIAGNOSTIC_POINT.json')
 v.need(point['status']=='EP_MEMORY_PATH_SENSITIVITY_CASE_ACCEPTED' and point['raw_sha256']==v.sha(out/'raw.log'),'science acceptance absent')
 m=adapter(case);local=B/'control'/(case+'_ARCHIVE_RECEIPT.json')
 result={'receipt':v.read(local),'verified_reused_transaction':True} if local.exists() else m.archive(case)
 receipt=result['receipt'];bundle=P(receipt['target_mount_path']);f,tx=m.libraries(bundle);manifest=m.read(bundle/'SOURCE_MANIFEST.json')
 v.need(m.manifest_for(case)==manifest,'accepted source changed since archive')
 before=m.gate();f.verify_archive(bundle,manifest)
 # Supplemental recovery tools are bound by a separate immutable SHA manifest.
 receiver=P('/root/share/host174_storage_recovery_bridge/20261016_storageops_02/.TARGET_RECEIVER.lock').open('rb');fcntl.flock(receiver,fcntl.LOCK_EX|fcntl.LOCK_NB)
 tool=bundle/'RESTORE_EP_MEMORY.py';code=(v.ROOT/'tools/portable_restore.py').read_bytes()
 if tool.exists():v.need(tool.read_bytes()==code,'portable tool collision')
 else:
  with tool.open('xb') as stream:stream.write(code);stream.flush()
 names=['RESTORE_EP_MEMORY.py','full_result_bundle.py','v9_transaction.py','RESULT_ENGINE_PIN.json']
 binding={'schema':'EP_PORTABLE_RESTORE_TOOL_BINDING_V1','cohort':case,'txid':manifest['txid'],'tool_sha256':{n:v.sha(bundle/n) for n in names},'legacy_native_result_py':'reference only; legacy default routes must not be used for this case','scope':'supplemental recovery tools; source payload remains protected by original COMMIT'}
 identical_or_put(bundle/'RESTORE_TOOL_MANIFEST.json',binding)
 receiver.close()
 target=B/'run/recovery'/('INDEPENDENT_'+receipt['txid'])
 args=['/usr/bin/python3','-B',str(tool),'--destination',str(target),'--minimum-free-bytes',str(before['required_bytes'])]
 cp=subprocess.run(args,env={'PATH':'/usr/bin:/bin','LANG':'C','LC_ALL':'C','PYTHONDONTWRITEBYTECODE':'1'},capture_output=True,text=True,timeout=180)
 v.need(cp.returncode==0,'independent restore failed '+cp.stderr[-2000:])
 independent=json.loads(cp.stdout);v.need(independent['status']=='INDEPENDENT_BUNDLE_TO_NATIVE_TARGET_RESTORE_PASS' and independent['runtime_or_controller_imported'] is False,'independent restore proof mismatch')
 identical_or_put(B/'control/INDEPENDENT_NATIVE_TARGET_RESTORE.json',independent)
 identical_or_put(B/'control/PORTABLE_RESTORE_TOOL_BINDING.json',binding)
 with v.writer() as lock:
  reg=v.read(v.REG);epoch=v.read(v.EPOCH);row=reg['registered_future_requests'][case]
  v.need(row['consumed']==1 and row['uuid']==done['uuid'],'closed request identity')
  row.update(state='CLOSED',reserved_write_bytes=0,scientific_status=point['status'],archive_receipt_sha256=v.sha(local),independent_restore_sha256=v.sha(B/'control/INDEPENDENT_NATIVE_TARGET_RESTORE.json'))
  v.mutate(reg,epoch,'ARCHIVE_RESTORE_CLOSE')
 return {'archive':result,'independent_restore':independent}
