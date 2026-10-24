import pathlib,json,hashlib,os,importlib.util,subprocess,shutil
P=pathlib.Path;T=P('/root/data/dtc_main_short3_20261024_v1');N=P('/root/data/ep_l2_dtc_l1_native_v2');F=T/'docs-worktree';D=F/'docs/dtc_l1/review_packs/DTC_AE_MATCHED_HASH_SHORT3_20261024_V1'
read=lambda p:json.loads(P(p).read_bytes())
assert not list((T/'control/qualification_ledger').glob('*.INTENT.json'))
assert not list((T/'DTC/run/results').iterdir())
reg=read(N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json');q=reg['registered_future_requests']['DTC_AEFAIR_SHORT3_EPOCH2_20261024_V1'];assert q['consumed']=={} and q['sealed_unused']==12
proof={'schema':'DTC_SHORT3_PRE_FORK_ENGINEERING_STOP_V1','scope':'Missing central registry path mapping in new isolated workspace; no INTENT, no UUID result root and no model fork','model_starts':0,'refunds':0,'original_budget':12,'unused_budget':12,'stopped_request':q,'stopped_controller_state':read(T/'control/CONTROLLER_STATE.json'),'original_launch':read(T/'control/CONTROLLER_LAUNCH.json'),'original_CLI_HOLD':read(T/'control/E2-AEF3-NN-DM.CLI_EXECUTION.json'),'repair':'Add an exact symlink from new control/science_authority to the existing sole central science_authority; preserve original native/controller source and all stopped metadata. Use one separately identified R2 finite metadata controller to consume the original never-started cells only.'}
with (T/'control/PRELAUNCH_ENGINEERING_STOP_R1.json').open('x') as f:json.dump(proof,f,indent=2);f.write('\n')
(T/'control/science_authority').symlink_to(N/'control/science_authority',target_is_directory=True)
assert (T/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json').resolve()==(N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json').resolve()
controller=(T/'tools/short3_controller.py').read_text().replace('CONTROLLER_START.json','CONTROLLER_START_R2.json').replace("cell+'.CLI_EXECUTION.json'","cell+'.R2.CLI_EXECUTION.json'").replace("cell+'.PREPARE.json'","cell+'.R2.PREPARE.json'").replace("cell+'.ARCHIVE_CLI.json'","cell+'.R2.ARCHIVE_CLI.json'")
with (T/'tools/short3_controller_r2.py').open('x') as f:f.write(controller)
shutil.copyfile(T/'tools/short3_controller_r2.py',D/'tools/short3_controller_r2.py');shutil.copyfile(T/'control/PRELAUNCH_ENGINEERING_STOP_R1.json',D/'control/PRELAUNCH_ENGINEERING_STOP_R1.json')
with (D/'README.md').open('a') as f:f.write('\n## Prelaunch engineering correction\n\nThe first metadata controller stopped before INTENT/UUID/model fork because the new workspace lacked its central-registry path mapping. Zero scientific starts were consumed. An exact symlink now resolves to the same central authority. The stopped controller, CLI and sealed-unused state are retained. R2 is a separately identified finite metadata worker for the original12 never-started cells; this is no scientific retry/refund or added budget. No simulator/config/strict/resource policy byte changed.\n')
subprocess.run(['git','-C',str(F),'add',str(D.relative_to(F))],check=True)
subprocess.run(['git','-C',str(F),'diff','--cached','--check'],check=True)
subprocess.run(['git','-C',str(F),'commit','-m','Bind new short-workload workspace to sole central native authority'],check=True)
subprocess.run(['git','-C',str(F),'bundle','create',str(T/'control/short3_prelaunch_fix.bundle'),'hrl/dtc-aefair-short3-174new-20261024-v1','^8f63a19369422a0dedb0fc6dbab9cf1e7e74a225'],check=True)
print('NEW_COMMIT',subprocess.check_output(['git','-C',str(F),'rev-parse','HEAD'],text=True).strip())
