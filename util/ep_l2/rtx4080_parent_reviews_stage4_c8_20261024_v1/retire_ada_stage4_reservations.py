"""Close three terminal engineering write reservations without refunding attempts."""
from pathlib import Path
import sys,json,copy,hashlib,os
R=Path('/root/data/shared_sm70_trace_library_20261024_v1')
sys.path.insert(0,'/root/data/ep_l2_main_vector_r5_20261023_v1');import vector_runtime as base
proof=R/'control/ADA_STAGE4_RESERVATION_RETIREMENT.json'
if proof.exists():print(proof.read_text());raise SystemExit(0)
stage=json.loads((R/'control/ADA_STAGE4_PARENT_ARCHIVE_FULL_READBACK.json').read_text());assert stage['status']=='PASS_PARENT_STAGE4_FULL_TAR_MEMBERS_NATIVE_RESTORE_AND_ACTUAL_MAPPING_BLOBS' and len(stage['cases'])==3
own=R/'reservation_retirement';(own/'control').mkdir(parents=True,exist_ok=True)
auth=(R/'control/USER_BULK_4080_AND_IO_AUTHORIZATION_20261024.json').read_bytes();auth_path=own/'control/USER_AUTHORIZATION.json'
if auth_path.exists():assert auth_path.read_bytes()==auth
else:auth_path.write_bytes(auth)
held=base.lock();base.identity();reg=base.read(base.REG);epoch=base.read(base.EPOCH)
assert base.sha(base.REG)==epoch['native_registry_sha256'] and epoch['epoch']==2 and epoch['holder']==os.uname().nodename
before=copy.deepcopy(reg);rows=[]
for request in ['EP_ADA_TRACE_COMPAT_JIT65_MAPS_R3_V8_20261024_V1','EP_ADA_TRACE_COMPAT_WARPSYNC65_MAPS_R3_V8_20261024_V1','EP_ADA_TRACE_COMPAT_LEGACY65_R2_V8_20261024_V1']:
    row=reg['registered_future_requests'][request]
    assert row['owner']=='EP-MAIN' and row['budget']==row['consumed']==1 and row['state']=='COMPAT_PARTIAL_COMPLETE'
    assert row['reserved_write_bytes']==128*2**20 and len(row['case_consumption'])==1
    case=next(iter(row['case_consumption'].values()));exit_path=Path(case['exit_receipt']);result=json.loads(exit_path.read_text())
    assert result['exit_code']==0 and result['stop_reason'] is None and result['application_attempt_consumed']==1
    assert result['native_observed'] and result['request']==request
    assert (exit_path.parent/'PARENT_INDEPENDENT_TERMINAL_JOIN.json').exists()
    row['reserved_write_bytes']=0
    row['write_reservation_retirement']={'reason':'Terminal sole exact attempt (including retained semantic failure); full evidence sealed164 and independently reopened by parent','proof_reference':str(R/'control/ADA_STAGE4_PARENT_ARCHIVE_FULL_READBACK.json'),'proof_sha256':base.sha(R/'control/ADA_STAGE4_PARENT_ARCHIVE_FULL_READBACK.json'),'budget_refunded':False,'native_hot_output_deleted':False}
    rows.append({'request':request,'previous_reserved_write_bytes':128*2**20,'reserved_write_bytes':0,'consumed':1,'budget':1})
check=copy.deepcopy(reg)
for row in rows:
    original=before['registered_future_requests'][row['request']];changed=check['registered_future_requests'][row['request']]
    changed['reserved_write_bytes']=original['reserved_write_bytes'];changed.pop('write_reservation_retirement')
assert check==before
base.B=own;base.C='EP_ADA_STAGE4_RESERVATION_CLOSEOUT_20261024_V1'
base.registry_change(reg,epoch,'RETIRE_TERMINAL_WRITE_RESERVATIONS')
assert base.read(base.REG)==reg and base.read(base.EPOCH)['native_registry_sha256']==base.sha(base.REG)
result={'status':'PASS_EXACT_TERMINAL_RESERVATIONS_RETIRED','rows':rows,'reservation_bytes_released':384*2**20,'scientific_budget_refunded':0,'global_remaining_before':before['new_scientific_budget_remaining'],'global_remaining_after':reg['new_scientific_budget_remaining'],'foreign_records_unchanged':True,'original_scientific_lineages_unchanged':True,'native_hot_output_deleted':False}
proof.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
