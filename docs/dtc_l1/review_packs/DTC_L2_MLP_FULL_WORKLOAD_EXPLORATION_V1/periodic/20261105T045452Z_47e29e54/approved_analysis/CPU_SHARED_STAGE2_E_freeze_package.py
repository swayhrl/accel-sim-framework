"""Freeze explicit Stage2 E members; no production mutation."""
import pathlib,json,hashlib,datetime,difflib
P=pathlib.Path;D=P(__file__).parent
A=D.parents[2]
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def read(p):return json.loads(P(p).read_bytes())
def put(p,v):P(p).write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
runtime=['resource_extra_strict.py','bpf_extra_strict.py','consumer_bridge.py']
expected=['a6c79668e8520fefc92720476fb146af85c051a19b1792ec80aa919e8e3417ea','4d511441316523a833009d1e354e750d5cb60432fea4a39f8cec9771eeef1c1e','2e548a181f28535043bdd5ed885ab2d554ca6462a2e8e690f6e400a36d8fc1c7']
assert [sha(D/n)for n in runtime]==expected
B=A/'agents/B/cpu_shared_timeslice_stage2_v1'
assert sha(B/'MANIFEST.json')=='48da536b0037f61745d981ad9503560b69d837908759c397b74d9c4ec3cec6c1'
qualification=read(D/'CPU_STAGE2_CONSUMER_QUALIFICATION.json');assert qualification['status']=='PASS'and qualification['count']==9
gate=read(D/'ACTUAL_MIXED_GENERATION_GATE_READONLY.json');assert gate['accepted_real_count']==1 and gate['four_point_qualified']is False
patch=''
for n in runtime:
 patch+=''.join(difflib.unified_diff((D.parent/'cpu_shared_timeslice_strict_v1'/n).read_text().splitlines(True),(D/n).read_text().splitlines(True),fromfile='stage1/'+n,tofile='stage2/'+n))
(D/'STAGE1_TO_STAGE2_EXACT_DIFF.patch').write_text(patch)
interface=dict(schema='E_SHARED_STAGE2_CONSUMER_INTERFACE_V1',status='FROZEN_CPU_QUALIFIED_FINITE_ENGINEERING_CANDIDATE',sources=dict(zip(runtime,expected)),resource_library_sha256='bad182abf637e38d1cc41822315d957c708a754fd11da7a36de1511ba5574bcc',approval_sha256='30bd502f7fe6653907b3e835c2b7aee78c780c65ecde758df473942158d1b895',max_shared_running=1,scope='original engineering four, already accepted C0 readonly only',models_started=0,new_grants=0,production_changes=0,actual_new_three_qualified=False,actual_four_gate_qualified=False,primary_rollout_eligible=False,IR_rollout_eligible=False,validated_union_authorized=False,API={'consumer':'install_on_frame / consumer_check / restore_in_owner unchanged signatures; same private module safe_finish route','resource':'terminal(c, base_proof, root=None, authority=None, readonly=False)','observation':'normalize_contract(document, root, source_sha256, qualification_only=False, cfg=None); terminal; verify_archive','gate':'replay_closed_generation / replay_mixed_four_gate / capture_mixed_four_gate'},dependencies=[dict(path=str(B/'MANIFEST.json'),sha256=sha(B/'MANIFEST.json')),dict(path=str(B/'CPU_STAGE2_PREFIX_QUALIFICATION.json'),sha256=sha(B/'CPU_STAGE2_PREFIX_QUALIFICATION.json')),dict(path=str(B/'CPU_STAGE2_OWNER_QUALIFICATION.json'),sha256=sha(B/'CPU_STAGE2_OWNER_QUALIFICATION.json'))])
put(D/'INTERFACE.json',interface)
members=runtime+['build_stage2.py','mixed_generation_gate.py','build_consumer.py','qualify_stage2_consumer.py','CPU_STAGE2_CONSUMER_QUALIFICATION.json','ACTUAL_MIXED_GENERATION_GATE_READONLY.json','README.md','INTERFACE.json','STAGE1_TO_STAGE2_EXACT_DIFF.patch','freeze_package.py']
manifest=dict(schema='E_SHARED_STAGE2_FROZEN_MEMBER_MANIFEST_V1',created_UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),status=interface['status'],members=[dict(path=n,sha256=sha(D/n),bytes=(D/n).stat().st_size)for n in members],models_started=0,new_grants=0,production_changes=0,actual_models_qualified=False,actual_four_gate_qualified=False)
assert not (D/'MANIFEST.json').exists(),'No frozen manifest overwrite'
put(D/'MANIFEST.json',manifest)
print(json.dumps(dict(manifest_path=str(D/'MANIFEST.json'),manifest_sha256=sha(D/'MANIFEST.json'),QA_sha256=sha(D/'CPU_STAGE2_CONSUMER_QUALIFICATION.json'),actual_gate_sha256=sha(D/'ACTUAL_MIXED_GENERATION_GATE_READONLY.json'),source_sha256=dict(zip(runtime,expected)),members=len(members))))
