"""Directed admission and preserved-budget checks; never launches data work."""
import pathlib,sys,json,hashlib,importlib.util,tempfile,copy,ast,time
P=pathlib.Path
T=P('/root/data/research_asset_verified_offload_20261024_v1')
STAGE=T/'qualification/active_science_io_policy_v1'
sys.path.insert(0,str(T/'tools'))

def module(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def main():
    rr=module('qualified_resource_policy',STAGE/'server_resources.py')
    sup=module('qualified_supervisor_policy',STAGE/'continuation_supervisor.py');sup.c.rr=rr
    checks={}
    def rejects(name,fn,reason):
        try:fn()
        except RuntimeError as e:assert reason in str(e);checks[name]='PASS'
        else:raise AssertionError('must reject '+name)
    high={'some':{'avg10':7.7},'full':{'avg10':7.7}};active=[{'pid':1}]
    real=rr.IO_AUTHORIZATION
    with tempfile.TemporaryDirectory(prefix='policy_checks_',dir=STAGE) as d:
        rr.IO_AUTHORIZATION=P(d)/'missing.json'
        rejects('no_authorization_still_blocks_high_IO',lambda:rr.active_science_io_admission(high,active),'RESOURCE_HOLD_ACTUAL_ACTIVE_AEFAIR_IO')
        assert rr.active_science_io_admission({'some':{'avg10':1},'full':{'avg10':0.5}},active)['original_avg10_thresholds_pass'];checks['old_threshold_pass_without_authorization']='PASS'
        rr.IO_AUTHORIZATION.write_bytes(b'{}')
        rejects('changed_authorization_fails_closed',lambda:rr.active_science_io_admission(high,active),'ACTIVE_SCIENCE_IO_AUTHORIZATION_IDENTITY_HOLD')
    rr.IO_AUTHORIZATION=real
    x=rr.active_science_io_admission(high,active)
    assert x['mode']=='USER_AUTHORIZED_MONITOR_ONLY' and not x['original_avg10_thresholds_pass'];checks['valid_user_authorization_allows_observed_high_IO']='PASS'
    before=(STAGE/'BEFORE_server_resources.py').read_text().splitlines();after=(STAGE/'server_resources.py').read_text().splitlines()
    def admission_lines(lines):
        start=next(i for i,l in enumerate(lines) if l.startswith('def admission('));end=next(i for i in range(start+1,len(lines)) if lines[i].startswith('def '));return lines[start:end]
    a=admission_lines(before);b=admission_lines(after)
    a=[l for l in a if not l.startswith(' if active:need(')]
    b=[l.replace('active_science_IO_gate=active_io,','') for l in b if l!=' active_io=active_science_io_admission(io,active)']
    assert a==b,'an unrelated admission rule changed';checks['all_other_admission_lines_exactly_unchanged']='PASS'
    old=json.loads((T/'control/CONTINUATION_SUPERVISOR.json').read_bytes())
    h={'schema':'LANE_T2_IO_POLICY_SUPERVISOR_HANDOFF_V1','io_authorization_sha256':rr.IO_AUTHORIZATION_SHA256,'previous_supervisor_state':old}
    z=sup.preserved_start(h,now=old['deadline_unix']-1)
    assert z['deadline']==old['deadline_unix'] and z['rechecks']==old['resource_rechecks'] and z['restarts']==old['driver_restarts'] and z['current']==old['driver'];checks['original_deadline_counters_and_driver_identity_preserved']='PASS'
    rejects('expired_original_deadline_not_reset',lambda:sup.preserved_start(h,now=old['deadline_unix']+1),'ORIGINAL_SUPERVISION_DEADLINE_EXPIRED')
    bad=copy.deepcopy(h);bad['previous_supervisor_state']['resource_rechecks']=289
    rejects('exhausted_resource_counter_not_reset',lambda:sup.preserved_start(bad),'HANDOFF_RECHECK_COUNTER_INVALID')
    bad=copy.deepcopy(h);bad['previous_supervisor_state']['driver_restarts']=96
    rejects('exhausted_restart_counter_not_reset',lambda:sup.preserved_start(bad),'HANDOFF_RESTART_COUNTER_INVALID')
    for name in ['server_resources.py','continuation_supervisor.py']:ast.parse((STAGE/name).read_bytes())
    actual=rr.admission('TARGET',include_activity=False)
    result={'schema':'ACTIVE_SCIENCE_IO_POLICY_DIRECTED_QUALIFICATION_V1','unix':time.time(),'checks':checks,'actual_target_admission':actual,'supervisor_boundaries_observed':old,'data_executors_launched':0,'science_or_registry_changes':0,'authorization_sha256':rr.IO_AUTHORIZATION_SHA256}
    p=STAGE/'QUALIFICATION.json'
    with p.open('x') as f:json.dump(result,f,sort_keys=True,indent=2);f.flush();__import__('os').fsync(f.fileno())
    print(json.dumps({'checks':checks,'actual_target_admission':'PASS','active_science_IO_mode':actual['active_science_IO_gate']['mode'],'SSD_available_bytes':actual['SSD_available_bytes'],'SSD_required_bytes':actual['SSD_required_bytes'],'data_executors_launched':0}))

if __name__=='__main__':main()
