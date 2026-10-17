"""Run-specific first-trial control binding around the unchanged reverse stager."""
import pathlib,hashlib,sys,json
SELECTION='496995a9032d88f4f0506ade56325b6df51aa45ca07c64da1ef830121db6dbf3'
USER_SCOPE='b622c06271f46aa15596428a1b44e145bfc0c01f942bc2d0240e1bee262f0565'
NATIVE='/workspace/repos/gpu-l2-cache-verilog-v3r1-clean/build.restore.r1_197'
def bind_acceptance(ack):
    def require(ok):
        if not ok: raise ValueError('FIRST_TRIAL_EXACT_CONTROL_BINDING_MISMATCH')
    require(ack.get('target_fresh_selection_sha256')==SELECTION and ack.get('first_trial_user_scope_receipt_sha256')==USER_SCOPE)
    require(ack.get('maximum_authorized_trial_batch_id')=='R1_197_NATIVE_RESTORE_B001' and ack.get('maximum_authorized_plan_index')==0)
    require(ack.get('first_batch_files')==13 and ack.get('first_batch_logical_bytes')==470083881)
    require(ack.get('source_first_batch_temporary_resource_acceptance') is True and ack.get('target_first_batch_bridge_stage_authorized_after_github_pinned_ack') is True and ack.get('target_second_or_later_reverse_batch_stage_authorized') is False)
    roots=[ack[k] for k in ['native_staging_root','native_staging_path'] if k in ack];require(bool(roots) and all(r==NATIVE for r in roots))
    return dict(ack,native_staging_root=NATIVE)
def bind_ready(value):
    if value.get('schema')=='STORAGE_OPS_V7_TARGET_REVERSE_RESTORE_READY':
        assert value['batch_id']=='R1_197_NATIVE_RESTORE_B001' and value['plan_index']==0 and value['file_count']==13 and value['total_size_bytes']==470083881
        value=dict(value,target_fresh_selection_sha256=SELECTION,first_trial_user_scope_receipt_sha256=USER_SCOPE)
    return value
def main():
    root=pathlib.Path('/root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/infrastructure/tools')
    old=root/'r10_197_49997e8631fe';bundle=root/'v7_4f70a66da8fd'
    assert hashlib.sha256((old/'r1_197_reverse_restore_stage.py').read_bytes()).hexdigest()=='49997e8631fe513841bff27abd350f3f0ed03625544c84351a75444268503bc4'
    assert hashlib.sha256((bundle/'archive_receiver.py').read_bytes()).hexdigest()=='2ed1c3b14d26154f677bde26157688638d53416d7169a43d1b7fdb906a1bd35c'
    sys.path[:0]=[str(old),str(bundle)]
    import r1_197_reverse_restore_stage as stager
    import archive_receiver as receiver
    bridge=receiver.BRIDGE
    assert hashlib.sha256((bridge/'TARGET_NEXT_SOLE_WINDOW_SELECTION_R10_V4.json').read_bytes()).hexdigest()==SELECTION
    assert hashlib.sha256((bridge/'R1_197_FIRST_REVERSE_TRIAL_USER_SCOPE_R10_V1.json').read_bytes()).hexdigest()==USER_SCOPE
    validate=stager.validate_acceptance
    stager.validate_acceptance=lambda ack,decision:validate(bind_acceptance(ack),decision)
    atomic=receiver.atomic_json
    receiver.atomic_json=lambda path,value:atomic(path,bind_ready(value))
    assert '--index' in sys.argv and sys.argv[sys.argv.index('--index')+1]=='0'
    stager.main()
if __name__=='__main__':main()
