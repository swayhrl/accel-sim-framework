"""Freeze qualified broad E package and exact snapshot dependency joins."""
import pathlib,json,hashlib,datetime,difflib
P=pathlib.Path;D=P(__file__).parent;A=D.parents[2]
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def read(p):return json.loads(P(p).read_bytes())
def put(p,v):
 assert not p.exists(),'Immutable artifact exists'
 p.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
runtime=['resource_extra_strict.py','bpf_extra_strict.py','consumer_bridge.py']
expected=['62aa7ea6bb09f81b1b4f8ffc4d2e83d33a62811f7fd202711b1834f3ea6b2d4d','75919b437c72b07b7cabcc3e517a6348231eef8625b341e596e7ba5455a5dabc','33b56779a9451d7fc449f78851475021c989bb4a10b83c95cf0d685953e8c517']
assert [sha(D/n)for n in runtime]==expected
prefix=read(D/'CPU_PREFIX_CONSUMER_QUALIFICATION.json');release=read(D/'CPU_RELEASE_QUALIFICATION.json');route=read(D/'CPU_ROUTE_QUALIFICATION.json')
assert prefix['status']==release['status']==route['status']=='PASS'and(prefix['count'],release['count'],route['count'])==(20,5,4)
assert release['resource_library_sha256']=='c761f23333a0cb1d95a4926cc671b13f827dfecc10a434d0a3249c97cbba5d41'
cases=[]
for case in prefix['cases']:
 root=P(case['root']);c=case['cohort'];intent=read(root/'control/qualification_ledger'/(c+'.INTENT.json'));out=P(intent['output']);rs=read(out/'CPU_SHARED_TIMESLICE_SNAPSHOT.json');os=read(out/'STRACE_BPF_OBSERVATION_SNAPSHOT.json')
 for snapshot in [rs,os]:
  cfg=snapshot['config']
  for role,path in cfg['source_paths'].items():assert sha(path)==cfg['qualified_sources'][role]==snapshot['source_snapshots'][role]['sha256']
 assert rs['config']['qualified_sources']['library']==release['resource_library_sha256']
 assert rs['config']['qualified_sources']['extra_strict']==expected[0]and os['config']['qualified_sources']['extra_strict']==expected[1]and os['config']['qualified_sources']['consumer']==expected[2]
 cases.append(dict(kind=case['kind'],cohort=c,uuid=intent['uuid'],resource_sources=rs['config']['qualified_sources'],observation_sources=os['config']['qualified_sources'],resource_snapshot_sha256=sha(out/'CPU_SHARED_TIMESLICE_SNAPSHOT.json'),observation_snapshot_sha256=sha(out/'STRACE_BPF_OBSERVATION_SNAPSHOT.json'),actual_current_byte_join=True))
put(D/'FINAL_DEPENDENCY_JOIN.json',dict(schema='E_BROAD_SHARED_FINAL_SNAPSHOT_DEPENDENCY_JOIN_V1',status='PASS',cases=cases,qualifications={n:sha(D/n)for n in ['CPU_PREFIX_CONSUMER_QUALIFICATION.json','CPU_RELEASE_QUALIFICATION.json','CPU_ROUTE_QUALIFICATION.json']},models_started=0,new_grants=0,production_changes=0))
patch=''
for n in runtime:
 old=D.parent/('cpu_shared_timeslice_stage2_v1'if n=='resource_extra_strict.py'else'strace_bpf_future_strict_consumer_v3')/n
 patch+=''.join(difflib.unified_diff(old.read_text().splitlines(True),(D/n).read_text().splitlines(True),fromfile='frozen_preimage/'+n,tofile='broad/'+n))
(D/'EXACT_SOURCE_DIFF.patch').write_text(patch)
put(D/'INTERFACE.json',dict(schema='E_BROAD_SHARED_CONSUMER_INTERFACE_V1',status='FROZEN_CPU_QUALIFIED_CANDIDATE_NOT_INSTALLED',resource_ID='CPU_SHARED_DYNAMIC_FUTURE_MEMORY_095_V1',observation_ID='DTC_STRACE_BROAD_SHARED_CPU_V1',resource_strict_status='PASS_CPU_SHARED_DYNAMIC_IO_AND_ORIGINAL_PERFORMANCE',observation_strict_status='PASS_BROAD_SHARED_BPF_AND_ORIGINAL_IO',consumer_marker='DTC_STRACE_BROAD_SHARED_PRIVATE_CONSUMER_V1',dispatcher_marker='DTC_STRACE_BROAD_SHARED_DISPATCH_V1',resource_strict_key='additional_cpu_shared_timeslice_strict',observation_strict_key='additional_strace_bpf_observation_strict',route_claim_directory='control/broad_shared_cpu_route_claims',route_claim_schema='BROAD_SHARED_CPU_FUTURE_ROUTE_CLAIM_V1',resource_gate='actual Main2a542 plus separate Main5c512 and scope26',current_scope='15 primary+11 incident recovery; excluded engineering4/R2',IR_union_authorized=False,old_underlay_consumer_sha256='2e548a181f28535043bdd5ed885ab2d554ca6462a2e8e690f6e400a36d8fc1c7',source_sha256=dict(zip(runtime,expected)),API=dict(resource='terminal(c, base_proof, root=None, authority=None, readonly=False)',observation='normalize_contract / terminal / verify_archive; verify_release_prerequisite(cfg,q,resource_configuration_utf8=None,resource_snapshot=None)',consumer='install_on_frame / consumer_check / restore_in_owner; actual frame-private safe_finish only'),actual_primary_IR_models_qualified=False,models_started=0,new_grants=0,production_changes=0))
members=runtime+['build_candidate.py','release_prerequisite.py','qualify_consumer.py','qualify_route.py','qualify_release.py','CPU_PREFIX_CONSUMER_QUALIFICATION.json','CPU_ROUTE_QUALIFICATION.json','CPU_RELEASE_QUALIFICATION.json','qualify_release_SOURCE46274_PREIMAGE.py','CPU_RELEASE_QUALIFICATION_SOURCE46274_PREIMAGE.json','FINAL_DEPENDENCY_JOIN.json','EXACT_SOURCE_DIFF.patch','README.md','INTERFACE.json','freeze_package.py']
put(D/'MANIFEST.json',dict(schema='E_BROAD_SHARED_FROZEN_MEMBER_MANIFEST_V1',UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='FROZEN_CPU_QUALIFIED_CANDIDATE_NOT_INSTALLED',members=[dict(path=n,sha256=sha(D/n),bytes=(D/n).stat().st_size)for n in members],models_started=0,new_grants=0,production_changes=0,actual_primary_IR_models_qualified=False))
print(json.dumps(dict(manifest_path=str(D/'MANIFEST.json'),manifest_sha256=sha(D/'MANIFEST.json'),members=len(members),dependency_join_sha256=sha(D/'FINAL_DEPENDENCY_JOIN.json'),prefixQA_sha256=sha(D/'CPU_PREFIX_CONSUMER_QUALIFICATION.json'),routeQA_sha256=sha(D/'CPU_ROUTE_QUALIFICATION.json'),releaseQA_sha256=sha(D/'CPU_RELEASE_QUALIFICATION.json'))))
