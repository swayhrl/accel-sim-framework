from pathlib import Path as P
import hashlib,json,difflib
J=P('/root/data/ep_l2_full_workload_performance_20261027_v1');A=J/'research/performance_first_v3_20261104_v1/agent_a_mid_tag';R=A/'runtime_candidate';old=J/'research/performance_first_v2_20261103_v1/activation_20261104_v1/recovery_20261104_v1/agent_b_native/runtimes/system'
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def ref(p):return dict(path=str(p),sha256=sha(p),bytes=P(p).stat().st_size)
# Keep preparer declared namespace consistent; prospective, never registered.
p=A/'prepare_and_cpu.py';t=p.read_text().replace('EP_L2_MID_TAG_MATCHED_PERFORMANCE_FAMILY_V1_20261104','EP_L2_MID_TAG_850MHZ_V1_20261104');p.write_text(t)
patch=[]
for n in ['ep_perf_common_v2.py','ep_perf_native_wv_modes_draft.py','mode_contract.py','mode_aware_terminal.py','ep_perf_postprocess.py','ep_perf_archive.py','ep_perf_frontend.py']:
 before=(old/n).read_text()if(old/n).exists()else''
 patch.extend(difflib.unified_diff(before.splitlines(True),(R/n).read_text().splitlines(True),fromfile='V2/'+n,tofile='V3_candidate/'+n))
(A/'RUNTIME_PATCH_FROM_V2.diff').write_text(''.join(patch))
index=json.loads((A/'MID_TAG_FAMILY_SCOPE.json').read_text())
for r in index['points']:assert sha(r['spec_ref']['path'])==r['spec_ref']['sha256']
files=[];artifacts=[]
for p in sorted(A.rglob('*')):
 if not p.is_file()or p.name in['BUNDLE_MANIFEST.json','SHA256SUMS','GIT_INCLUDE_FILES.txt']:continue
 rel=p.relative_to(A)
 if '__pycache__'in rel.parts or'host_fixture_root'in rel.parts:continue
 if p.suffix in ['.cpu','.o']or p.name=='midtag.cpu':artifacts.append(ref(p));continue
 files.append(dict(member=str(rel),**ref(p)))
manifest=dict(schema='EP_PFV3_AGENT_A_MIDTAG_DELIVERY_BUNDLE_V1',status='PASS_ENGINEERING_AND_EXACT8_PREPARATION_NOT_ACTIVATED',root=str(A),intended_execution_root=str(J/'execution_midtag_v3_20261104_v1/midtag'),science_request_id='EP_L2_MID_TAG_850MHZ_V1_20261104',source_identity=index['source_identity'],candidate_spec_count=8,new_scientific_starts=0,registered_budget=0,Source_changed=False,shared_Native_changed=False,real_registry_changed=False,CPU_protocol_pairs=4,CPU_protocol_runs=8,actual282_points=8,Host_checks=126,application_NI='NOT_MEASURED',B0_M0a_application_NI='NOT_PROVEN_HELD_ON',files=files,engineering_build_artifacts_not_for_Git=artifacts,run_order='FWT_FOUR_CLOSED_ACCEPTED_ARCHIVED_TWO_RESTORES_BEFORE_GEMM_FOUR',required_Main_installation=['new explicit scope authorization','fresh budget8 registration','Main Host/modeCPU review','frozen exact8 Source5/input/282/specSHA','scoped entry/globalexact route binding','unified current resource/consume/admission/restore policy','full acceptance+true164 archive/two restores'],dry_reproduce_command='python3 '+str(A/'test_runtime_candidate.py'))
(A/'BUNDLE_MANIFEST.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
(A/'SHA256SUMS').write_text(''.join(f['sha256']+'  '+f['member']+'\n'for f in files))
(A/'GIT_INCLUDE_FILES.txt').write_text('\n'.join(f['member']for f in files)+'\nBUNDLE_MANIFEST.json\nSHA256SUMS\nGIT_INCLUDE_FILES.txt\n')
print(json.dumps(dict(bundle_ref=ref(A/'BUNDLE_MANIFEST.json'),text_files=len(files),text_bytes=sum(x['bytes']for x in files),build_bytes=sum(x['bytes']for x in artifacts))))

