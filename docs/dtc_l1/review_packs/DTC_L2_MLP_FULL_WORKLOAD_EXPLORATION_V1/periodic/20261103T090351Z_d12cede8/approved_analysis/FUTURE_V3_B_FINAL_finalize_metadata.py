"""Own package metadata and exact restore delta, no production operation."""
import pathlib,json,hashlib,difflib,ast
P=pathlib.Path;D=P(__file__).parent
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def put(p,v):P(p).write_text(json.dumps(v,sort_keys=True,indent=2)+'\n')
source=(D/'strace_entry.py').read_bytes();text=source.decode();r=text.index('def restore_owner_dispatch(');a=text.index("  engine=v['frame'].f_locals['engine'];q=engine.registered()[2];root=P(engine.R)\n",r);z=text.index("  assert v['frame'].f_globals['worker']is v['wrapper'];",a);old=text[:a]+text[z:]
assert hashlib.sha256(old.encode()).hexdigest()=='aca9b704364cc370b4135c75836ed931bc9dcbe2fa5488c38129a3a99d791a9c'
delta=D/'RESTORE_DELTA';delta.mkdir(exist_ok=True);(delta/'PRODUCER_PREIMAGE_ACA9.py').write_bytes(old.encode());(delta/'PRODUCER_EXACT_DIFF.patch').write_text(''.join(difflib.unified_diff(old.splitlines(True),text.splitlines(True),fromfile='qualified_ACA9_preimage',tofile='candidate_06e52')))
def other_functions(t):return ast.dump(ast.Module(body=[n for n in ast.parse(t).body if not(isinstance(n,ast.FunctionDef)and n.name=='restore_owner_dispatch')],type_ignores=[]),include_attributes=False)
assert other_functions(old)==other_functions(text)
put(delta/'DELTA.json',dict(schema='V3_PRODUCER_RESTORE_ONLY_DELTA_V1',old_sha256=hashlib.sha256(old.encode()).hexdigest(),new_sha256=sha(D/'strace_entry.py'),all_AST_outside_restore_identical=True,preimage_sha256=sha(delta/'PRODUCER_PREIMAGE_ACA9.py'),patch_sha256=sha(delta/'PRODUCER_EXACT_DIFF.patch'),old_joint6_preserved_not_claimed_as_new_source_qualification=True,required_delta_check='Admitted unused V3 routeclaim prevents worker/consumer restore and retains exact wrappers; no claim cancel, model or production action'))
print(json.dumps(dict(delta=str(delta/'DELTA.json'),delta_sha256=sha(delta/'DELTA.json'),producer_sha256=sha(D/'strace_entry.py'))))

# Run this metadata completion on174 only. All output remains in this own dir.
if str(D).startswith('/root/share/'):
 E=D.parents[1]/'E/strace_bpf_future_strict_consumer_v3';N=P('/root/data/dtc_l2_mlp_exploration_20261027_v1/control/operational_amendments/strace_bpf_future_entry_v3')
 roles=dict(entry=D/'native-entry/bin/experiment',frontend=D/'bpf_frontend.py',producer=D/'strace_entry.py',extra_strict=E/'bpf_extra_strict.py',consumer=E/'consumer_bridge.py');qualified={k:sha(p)for k,p in roles.items()};qa=N/'SOURCE_CPU_QUALIFICATION.json';back=N/'SOURCE_BYTE_READBACK.json'
 q=json.loads(qa.read_bytes());b=json.loads(back.read_bytes());assert q['qualified_sources']==b['qualified_sources']==qualified and q['production_release_eligible']is False and q['actual4_qualified']is False
 assert all(sha(p)==h for p,h in q['expected_pins'].items())
 refs=[E/'CPU_PREFIX_CONSUMER_QUALIFICATION.json',E/'CPU_GATE_ROUTING_QUALIFICATION.json',E/'MANIFEST.json',qa,back]
 delivery=dict(schema='B_V3_COMPLETE_INACTIVE_DELIVERY_V1',status='FROZEN_CPU_MECHANICS_QUALIFIED_NOT_INSTALLED_REAL4_MISSING',qualified_sources=qualified,source_paths={k:str(p)for k,p in roles.items()},metadata_helper_sha256=sha(D/'cfg_metadata.py'),interface_sha256=sha(D/'INTERFACE.json'),restore_delta_sha256=sha(delta/'DELTA.json'),qualification_references=[dict(path=str(p),sha256=sha(p))for p in refs],historical_initial_prefix_smoke_not_final_source_qualification=dict(path=str(D/'CPU_PREFIX_SMOKE.json'),sha256=sha(D/'CPU_PREFIX_SMOKE.json')),real4_prerequisite_path=None,real4_prerequisite_sha256=None,ACTIVE_or_overlay_created=False,actual_model_starts=0,production_changes=0,registry_changes=0,production_release_eligible=False)
 put(D/'DELIVERY.json',delivery)
 names=['strace_entry.py','bpf_frontend.py','native-entry/bin/experiment','cpu_prefix_fixture.py','qualify_prefix_smoke.py','cfg_metadata.py','finalize_metadata.py','INTERFACE.json','PRODUCTION_CONFIG_PENDING.json','README.md','DELIVERY.json','CPU_PREFIX_SMOKE.json','RESTORE_DELTA/PRODUCER_PREIMAGE_ACA9.py','RESTORE_DELTA/PRODUCER_EXACT_DIFF.patch','RESTORE_DELTA/DELTA.json']
 put(D/'MANIFEST.json',dict(schema='B_STRACE_BPF_FUTURE_ENTRY_V3_MANIFEST',status='FROZEN_INACTIVE_SOURCE_CANDIDATE',members=[dict(path=str(D/n),relative_path=n,sha256=sha(D/n),bytes=(D/n).stat().st_size)for n in names],qualified_sources=qualified,referenced_qualification_artifacts=delivery['qualification_references'],production_release_eligible=False))
 print(json.dumps(dict(manifest_sha256=sha(D/'MANIFEST.json'),delivery_sha256=sha(D/'DELIVERY.json'),members=len(names),metadata_helper_sha256=sha(D/'cfg_metadata.py'),interface_sha256=sha(D/'INTERFACE.json'))))
