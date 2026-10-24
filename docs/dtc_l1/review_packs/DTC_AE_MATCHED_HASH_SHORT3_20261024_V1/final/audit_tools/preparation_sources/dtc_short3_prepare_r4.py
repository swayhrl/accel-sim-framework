import pathlib,json,subprocess,shutil,ast,hashlib
P=pathlib.Path;T=P('/root/data/dtc_main_short3_20261024_v1');N=P('/root/data/ep_l2_dtc_l1_native_v2');F=T/'docs-worktree';D=F/'docs/dtc_l1/review_packs/DTC_AE_MATCHED_HASH_SHORT3_20261024_V1'
read=lambda p:json.loads(P(p).read_bytes())
q=read(N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json')['registered_future_requests']['DTC_AEFAIR_SHORT3_EPOCH2_20261024_V1'];assert q['state']=='STOP_UNACCEPTED' and len(q['consumed'])==11 and q['sealed_unused']==1 and q['remaining']==0
assert '[Errno 11]' in q['failure'] and read(T/'control/E2-AEF3-MRIQ-CM_ARCHIVE_RECEIPT.json')['status']=='ARCHIVE_VERIFIED_AND_RESTORE_VERIFIED_NATIVE_TARGET'
checkpoint={'schema':'DTC_SHORT3_COPYONLY_OUTBOX_CONTENTION_CHECKPOINT_R3','state':read(T/'control/CONTROLLER_STATE.json'),'request_preimage':q,'archive_HOLD':read(T/'control/E2-AEF3-MRIQ-CM.R3.ARCHIVE_CLI.json'),'current_completed_CM_archive_receipt':read(T/'control/E2-AEF3-MRIQ-CM_ARCHIVE_RECEIPT.json'),'scientific_starts':11,'remaining_never_started':['E2-AEF3-MRIQ-CH'],'model_retries':0,'scope':'All11 consumed models naturally completed and strict accepted. Archive was refused by a nonblocking shared lock; existing CM output was then COPY_ONLY archived/restored. Exact original lock owner not attributed from genericEAGAIN. Continue only original unusedCH.'}
with (T/'control/OUTBOX_CONTENTION_CHECKPOINT_R3.json').open('x') as f:json.dump(checkpoint,f,indent=2);f.write('\n')
src=(T/'tools/short3_controller_r3.py').read_text().replace('CONTROLLER_START_R3.json','CONTROLLER_START_R4.json').replace('short3_native.py','short3_native_floor5_v3.py').replace('.R3.CLI_EXECUTION.json','.R4.CLI_EXECUTION.json').replace('.R3.PREPARE.json','.R4.PREPARE.json')
src=src.replace("assert cell=='E2-AEF3-NN-DM','only the one closed original point may be consumed before this continuation'","assert cell in "+repr(sorted(q['consumed']))+",'only the11 exact archived consumed cells may be skipped'")
old="""  r=subprocess.run([str(N/'bin/result'),'archive',cell],capture_output=True,text=True,timeout=300)
  (T/'control'/(cell+'.R3.ARCHIVE_CLI.json')).write_text(r.stdout+r.stderr);r.check_returncode()
  archive=json.loads(r.stdout);assert archive['receipt']['status']=='ARCHIVE_VERIFIED_AND_RESTORE_VERIFIED_NATIVE_TARGET'"""
new="""  copyonly=module('bounded_copyonly_lock_wait','short3_archive_wait.py')
  archive=copyonly.archive_wait(cell,tag='R4_COPYONLY_LOCK_WAIT')
  assert archive['receipt']['status']=='ARCHIVE_VERIFIED_AND_RESTORE_VERIFIED_NATIVE_TARGET'"""
assert old in src;src=src.replace(old,new);ast.parse(src)
with (T/'tools/short3_controller_r4.py').open('x') as f:f.write(src)
for name in ['short3_controller_r4.py','short3_archive_wait.py']:shutil.copyfile(T/'tools'/name,D/'tools'/name)
for name in ['OUTBOX_CONTENTION_CHECKPOINT_R3.json','STORAGE_FLOOR5_ACTIVATED_V3.json']:shutil.copyfile(T/'control'/name,D/'control'/name)
with (D/'README.md').open('a') as f:f.write('''
## Shared COPY_ONLY lock contention after11 accepted models

MRI-Q-CM naturally completed with362244cycles and passed whole-input strict. Its first archive request returned nonblockingEAGAIN from a shared science/receiver lock, before a local archive receipt existed. The exact old lock owner is not attributed from the generic error. R3 preserved the11 spent models and sealed the one never-startedCH. COPY_ONLY continuation then archived/restored the sameCM output successfully, without any model rerun. R4 is a separately identified finite metadata continuation that skips exactly those11 accepted/archived UUIDs and may start only the original unusedMRI-Q-CH, keeping total budget12. Its outbox waits on transientEAGAIN for at most21600s; only metadata COPY_ONLY operations are retried, never an INTENT/model. Other errors remain fail-closed. All prior controller/CLI/authority preimages remain preserved.
''')
subprocess.run(['git','-C',str(F),'add',str(D.relative_to(F))],check=True)
subprocess.run(['git','-C',str(F),'diff','--cached','--check'],check=True)
subprocess.run(['git','-C',str(F),'commit','-m','Continue final unused point after shared outbox lock contention'],check=True)
subprocess.run(['git','-C',str(F),'bundle','create',str(T/'control/short3_outbox_continuation.bundle'),'hrl/dtc-aefair-short3-174new-20261024-v1','^2da94f48c7e818f32a5f3d96fc3ae9cd4ab1eb18'],check=True)
print('COMMIT',subprocess.check_output(['git','-C',str(F),'rev-parse','HEAD'],text=True).strip())
