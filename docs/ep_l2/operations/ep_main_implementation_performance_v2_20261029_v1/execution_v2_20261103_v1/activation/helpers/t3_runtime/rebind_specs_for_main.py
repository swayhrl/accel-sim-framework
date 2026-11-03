"""Main-owned invocation only: bind draft immutable artifacts, no authority/native/model actions.
INPUT json: host_qualification_ref/resource_module_ref/resource_policy_ref [real Main refs].
Writes candidate staged_specs in helper dir, never registered cases. Main installs final specs.
"""
import pathlib,json,hashlib,importlib.util,sys,copy
P=pathlib.Path;E=P(__file__).resolve().parents[2];R=E/'runtime_t';H=P(__file__).resolve().parent
D=P('/root/data/ep_l2_full_workload_performance_20261027_v1/research/implementation_performance_v2_20261029_v1/agent_c_formal_closure/main_review_bound_drafts')
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def ref(p):return dict(path=str(p),sha256=sha(p))
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,sort_keys=True,indent=2)+'\n');return ref(p)
def main(bindings_path):
    bindings=json.loads(P(bindings_path).read_text());out=H/'staged_specs';out.mkdir(exist_ok=True)
    for name in ['host_qualification_ref','resource_module_ref','resource_policy_ref']:
        v=bindings[name];assert sha(v['path'])==v['sha256'],name+' drift'
    copies={}
    for p in D.glob('*MATRIX.json'):copies[str(p)]=write(out/p.name,json.loads(p.read_text()))
    results=[]
    for p in sorted(D.glob('EP_PERF_*.json')):
        s=json.loads(p.read_text());s['authorization_status']='USER_AUTHORIZED_20261103_EXACT_FRESH_SCOPE_NOT_YET_REGISTERED'
        for key in ['host_engine_ref','host_common_ref','mode_contract_ref','validation_module_ref']:
            s[key]=ref(R/P(s[key]['path']).name)
        for name in ['archive_module_ref']:s[name]=ref(R/P(s[name]['path']).name)
        for name in ['host_qualification_ref','resource_module_ref','resource_policy_ref']:s[name]=bindings[name]
        s['three_arm_matrix_ref']=copies[s['three_arm_matrix_ref']['path']]
        # Relocate complete parser/dependency inventory without changing its bytes.
        old='/agent_c_formal_closure/host_candidate/'
        pins={}
        for path,digest in s['pinned_files'].items():
            if old in path:
                target=R/path.split(old,1)[1];pins[str(target)]=sha(target)
            else:pins[path]=digest
        for path in R.rglob('*'):
            if path.is_file():pins[str(path)]=sha(path)
        pins[bindings['resource_module_ref']['path']]=bindings['resource_module_ref']['sha256']
        s['pinned_files']=pins
        results.append(dict(cohort=s['cohort'],spec_ref=write(out/p.name,s)))
    write(H/'REBIND_RESULT.json',dict(status='STAGED_FOR_MAIN_NOT_REGISTERED',specs=results,scientific_starts=0,registry_writes=0))
    return results
if __name__=='__main__':print(json.dumps(main(sys.argv[1])))
