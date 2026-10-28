"""Assemble candidate-only config/QA/templates. Never writes production paths.
Qualification phase requires current library, owner and native/strict evidence.
"""
import pathlib,json,hashlib,copy,argparse,datetime
P=pathlib.Path;D=P(__file__).parent;R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1');E=D.parents[1]/'E/cpu_spare_execution_v1';M=R/'control/operational_amendments/future_memory_admission_v1'
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def put(p,v):P(p).write_text(json.dumps(v,sort_keys=True,indent=2)+'\n')
def has(v,target):
 if isinstance(v,dict):return any(has(x,target)for x in v.values())
 if isinstance(v,list):return any(has(x,target)for x in v)
 return v==target
p=argparse.ArgumentParser();p.add_argument('--phase',choices=['draft','qualify'],default='draft');p.add_argument('--owner-source',default=str(E/'cpu_owner.py'));p.add_argument('--extra-source',default=str(E/'cpu_extra_strict.py'));p.add_argument('--owner-qa',default=str(E/'OWNER_CPU_QUALIFICATION.json'));p.add_argument('--strict-qa');p.add_argument('--review');p.add_argument('--output',default=str(D/'candidate'));p.add_argument('--deployment-root',default=str(R/'control/operational_amendments/cpu_spare_memory_v1'));a=p.parse_args();out=P(a.output);need=out.resolve().is_relative_to(D.resolve());assert need,'Only independent candidate directory writes authorized';out.mkdir(parents=True,exist_ok=True)
libqa=read(D/'CPU_LIBRARY_QUALIFICATION.json');old=read(M/'ACTIVE_MEMORY.json');assert old['overlay_id']=='FUTURE_ONLY_MEMORY_ADMISSION_095_FLOOR10_V1','Freeze original old95 fallback before switching ACTIVE';identity=read(D.parents[2]/'coordinator/CPU_SPARE_PROVISIONAL_CANARY_IDENTITY_V1.json');C=identity['preferred'];deploy=P(a.deployment_root)
sources=dict(library=sha(D/'cpu_memory.py'),frontend=sha(old['frontend_path']),owner=sha(a.owner_source),extra_strict=sha(a.extra_source),joint_padding=old['joint_padding_sha256'],joint_io=old['joint_io_sha256']);issues=[]
if libqa['status']!='PASS'or libqa['source_sha256']!=sources['library']:issues.append('LIBRARY_PROOF_NOT_CURRENT')
owner=read(a.owner_qa)if P(a.owner_qa).exists()else None
if not owner or owner['status']!='PASS'or not all(has(owner,v)for v in [sources['library'],sources['owner'],sources['extra_strict']]):issues.append('OWNER_REAL_CROSS_PROOF_NOT_CURRENT')
strict=read(a.strict_qa)if a.strict_qa and P(a.strict_qa).exists()else None
required_strict_cases=['actual A native producer plus real oldIO helper/front and new extra replay passes','original performance remains mandatory','OWNER_FRAME proof cannot stand in for NATIVE proof','missing canonical candidate rejected even after total math recomputation','new generation cannot also claim old memory binding','source snapshot tamper fails closed']
strict_stage=bool(strict and strict.get('status')=='PASS'and all(has(strict,v)for v in [sources['library'],sources['extra_strict'],sources['owner']])and(strict.get('native_prefix_qualified')and strict.get('extra_strict_qualified')or all(x in strict.get('checks',[])for x in required_strict_cases)))
if not strict_stage:issues.append('NATIVE_PREFIX_AND_EXTRA_STRICT_PROOF_REQUIRED')
review=read(a.review)if a.review and P(a.review).exists()else None
if a.review and(not review or review['status']!='PASS'or not has(review,sources['library'])):issues.append('INDEPENDENT_REVIEW_NOT_CURRENT')
if a.phase=='qualify':assert not issues,issues
proofs=dict(library=dict(path=str(D/'CPU_LIBRARY_QUALIFICATION.json'),sha256=sha(D/'CPU_LIBRARY_QUALIFICATION.json')),owner=dict(path=a.owner_qa,sha256=sha(a.owner_qa))if owner else None,strict=dict(path=a.strict_qa,sha256=sha(a.strict_qa))if strict else None,independent_review=dict(path=a.review,sha256=sha(a.review))if review else None)
qa=dict(schema='CPU_SPARE_MEMORY_OWNER_NATIVE_JOINT_QUALIFICATION_V1',status='PASS'if not issues else'PENDING',cpu_spare_library_qualified=not('LIBRARY_PROOF_NOT_CURRENT'in issues),native_binding_qualified=strict_stage,native_prefix_qualified=strict_stage,extra_strict_qualified=strict_stage,joint_strict_qualified=strict_stage,native_prefix_qualification_scope='CPU fixture A native binding producer plus unchanged real IO helper/front; exclusive and original-performance leaf are stand-ins, no real model/lease/physics acceptance',qualified_sources=sources,expected_pins=old['expected_pins'],evidence=proofs,remaining_requirements=issues,production_installed=False,models_started=0,grants_added=0)
put(out/'CPU_JOINT_QUALIFICATION.json',qa)
cfg=copy.deepcopy(old);cfg.update(status='CANDIDATE_NOT_INSTALLED',overlay_id='CPU_SPARE_FUTURE_MEMORY_ADMISSION_095_V1',fallback_v2_config=old,cpu_exception_scope=dict(mode='SINGLETON',allowed_cohorts=[C]),cpu_spare_policy=dict(min_sample_seconds=.5,max_evidence_age_seconds=2.,max_sample_seconds=10.,quota_fraction=.75,prospective_cpu_threads=1,min_spare_physical_cores=4,max_sibling_busy_fraction=.10,only_ignored_reason='cpu_pressure_full',visible_ancestors_only=True,hidden_ancestor_limits_excluded=False),library_path=str(deploy/'cpu_memory.py'),owner_path=str(deploy/'cpu_owner.py'),extra_strict_path=str(deploy/'cpu_extra_strict.py'),QA_path=str(deploy/'CPU_JOINT_QUALIFICATION.json'),QA_sha256=sha(out/'CPU_JOINT_QUALIFICATION.json'),readback_path=str(deploy/'PUBLICATION_READBACK.json'),readback_sha256='MAIN_VERIFIED_READBACK_SHA_REQUIRED')
for r,h in sources.items():cfg[r+'_sha256']=h
if C not in cfg['allowed_cohorts']:cfg['allowed_cohorts'].append(C)
put(out/'INSTALL.template.json',cfg)
record_keys=['request','overlay_id','scope_mode','memory_utilization_fraction','host_floor_bytes','cgroup_floor_bytes','expected_pins','io_active_sha256','allowed_cohorts',*[r+'_sha256'for r in sources],'QA_sha256','readback_sha256','cpu_exception_scope','cpu_spare_policy'];rec={k:cfg[k]for k in record_keys};rec.update(status='CANDIDATE_NOT_REGISTERED',fallback_v2_config_sha256=hashlib.sha256((json.dumps(old,sort_keys=True,indent=2)+'\n').encode()).hexdigest());put(out/'REGISTRY_RECORD.template.json',rec)
put(out/'PUBLICATION_READBACK.template.json',dict(verified=False,commit=None,qualified_sources=sources,expected_pins=cfg['expected_pins'],QA_sha256=cfg['QA_sha256'],note='Main all-byte readback required; source and QA only; template cannot activate'))
source_files=[dict(role='library',source=str(D/'cpu_memory.py'),deploy=cfg['library_path'],sha256=sources['library']),dict(role='owner',source=a.owner_source,deploy=cfg['owner_path'],sha256=sources['owner']),dict(role='extra_strict',source=a.extra_source,deploy=cfg['extra_strict_path'],sha256=sources['extra_strict'])]
put(out/'PREPARATION_RECEIPT.json',dict(status='QUALIFIED_CANDIDATE_NOT_INSTALLED'if not issues else'DRAFT_INCOMPLETE_NOT_INSTALLABLE',UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),phase=a.phase,source_files_to_copy_after_publication=source_files,remaining_requirements=issues,exception_cohort=C,fallback_count=len(old['allowed_cohorts']),original_MEM6_files_modified=False,native46_modified=False,old_record_must_remain_exact=True,science_grants_added=0))
print(json.dumps(dict(output=str(out),status=qa['status'],remaining_requirements=issues,library_source_sha256=sources['library'],cfg_template_sha256=sha(out/'INSTALL.template.json'))))
