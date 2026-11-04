from pathlib import Path as P
import json,hashlib
V=P('/root/data/ep_l2_full_workload_performance_20261027_v1/research/performance_first_v3_20261104_v1');ACT=V/'activation_20261104_v1';F=ACT/'agent_a_formal';R=ACT/'runtimes/midtag';C=ACT/'agent_c_resources';D=ACT/'agent_d_execution'
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def ref(p):return dict(path=str(p),sha256=sha(p),bytes=P(p).stat().st_size)
def put(p,d):P(p).write_text(json.dumps(d,indent=2,sort_keys=True)+'\n');return ref(p)
# Refresh fresh dry-proof reference only, without changing any runtime byte.
p=F/'review_drafts/MAIN_HOST_QUALIFICATION_DRAFT.json';h=json.loads(p.read_text());h['fresh_formal_Host_evidence_ref']={k:v for k,v in ref(F/'FORMAL_DRY_HOST_RECEIPT.json').items()if k!='bytes'};p.write_text(json.dumps(h,indent=2,sort_keys=True)+'\n')
(F/'MAIN_HANDOFF.md').write_text("""# Mid-Tag8 formal activation handoff

Producer preparation is PASS; Main review/signing, registration, scoped Native installation, real Native prepare and admission are Main-owned gates. Zero models or budget/registry/global Native writes by Agent A.

Canonical request EP_L2_MID_TAG_850MHZ_V1_20261104. Canonical data root /root/data/ep_l2_full_workload_performance_20261027_v1/execution_midtag_v3_20261104_v1/midtag. Runtime activation/runtimes/midtag. Exact eight FWT/GEMM S/WV, G32x16/G64x8, Source78/accepted ELF,850MHz/L100/FR128/observer111 and physical Payload1168 unchanged.

Original Agent A package remains immutable. All scientific282 values, input identity/member/ordered kernels, observer env, Source5 and original config prefix match it exactly. Only final overlay path is copied to the formal runtime; its bytes/SHA are unchanged. No Core or ELF rebuild.

Fresh formal adapter dry tests:143 PASS. These use explicitly owned in-memory authority and synthetic Main-review fixtures only. Producer review drafts are rejected by the real formal mode contract. Existing four mode/geometry production CPU MS011/111 pairs and eight full282 parser runs are reused, not rerun or upgraded to application NI.

## Main review and seal

Read review_drafts/MAIN_MODE_CPU_QUALIFICATION_DRAFT.json, MAIN_HOST_QUALIFICATION_DRAFT.json and MAIN_SOURCE_INPUT_REUSE_REVIEW_DRAFT.json with FORMAL_DRY_HOST_RECEIPT.json. Main must issue real final receipts with approved_by EP-MAIN, no fixture_only, and required final statuses. The Host receipt must include all listed immutable modules, including D routeguard/safe core and C resources_midtag/resources_v3/CAP10policy. Module bytes are frozen.

Then run seal_formal_specs.py with --mode-review, --host-review, --resource-module and --resource-policy. It produces bound_specs and BOUND_FINAL_SPEC_INDEX.json after static mode, exact282, Source/input/auth and matched pair checks. It does not mint authorization, register budgets, modify shared Native or start models.

Native entry template is agent_a_formal/native_midtag_v3. Install its exact bytes to execution_midtag_v3_20261104_v1/bin/native_midtag_v3. D confirmed the sealed invocation chooses the Python interpreter from its exact shebang. The engine pins D guard9df2bab... and requires NATIVE_ENTRY_ROUTE_V3.json with new owned runtime dependency graph and shared route contract; unreviewed mutation HOLDs. Source5/ELF/lib/input/spec checks remain in the existing engine.

Fresh scoped user authorization is already read-only bound to approved881a4f07, exact eight cohorts and Source5. Main is the only registry/native/model owner. Consumed points cannot retry/refund.

C cap10 wrapper/policy and37-test resource qualification are bound. Admission supplies host_cpu, cohort and request identity, so only the exact own CLAIMED CPU is excluded from collision checks. All other claims/models remain protected. Global admission/archive locks are unchanged. Cap2 alternative is qualified if Main deliberately selects it during sealing.

FWT four must be CLOSED_ACCEPTED with complete true164 archives/two independent restores before any GEMM consumption. In addition to direct registry/Source/spec/drain/archive checks, engine requires D's FWT4_ACCEPTED_STAGE_REVIEW.json matching those same four point/archive refs and controller manifest SHA.

New geometry application NI remains NOT_MEASURED. B0/M0a stay ON and their application NI is NOT_PROVEN. No added observer, Source/ELF change or NI model allowance. Full application scientific results are still pending Main execution/acceptance.

Actual forecast: FWT1GiB/10-20min, GEMM5GiB/45-90min, each16MiB expected incremental result growth. Hard RSS8GiB/AS24GiB/result256MiB remain stop bounds, not extra reserved growth. Trace input remains true164.
""")
owned=[]
for p in sorted(R.rglob('*')):
 if p.is_file()and'__pycache__'not in p.parts:owned.append(ref(p))
runtime_manifest=put(F/'FORMAL_RUNTIME_BYTE_MANIFEST.json',dict(status='FROZEN_PRODUCER_RUNTIME_BYTES_PENDING_MAIN_INSTALLATION',runtime_root=str(R),owned_runtime_pins=owned,external_guard_and_resources=[ref(D/n)for n in ['native_route_guard_v3.py','safe_native_core_v3.py']]+[ref(C/n)for n in ['resources_midtag.py','resources_v3.py','RESOURCE_POLICY_CAP10.json']],no_Source_ELF_change=True))
files=[]
for p in sorted(F.rglob('*')):
 if p.is_file()and'host_fixture_root'not in p.parts and'__pycache__'not in p.parts and'bound_specs'not in p.parts and p.name not in ['FORMAL_DELIVERY_MANIFEST.json','BOUND_FINAL_SPEC_INDEX.json']:
  files.append(ref(p))
delivery=dict(schema='EP_PFV3_MIDTAG_FORMAL_PRODUCER_DELIVERY_V1',status='PASS_FORMAL_PREPARATION_PENDING_MAIN_REVIEW_REGISTRATION_NATIVE_INSTALLATION',request_id='EP_L2_MID_TAG_850MHZ_V1_20261104',producer_root=str(F),runtime_root=str(R),runtime_byte_manifest_ref=runtime_manifest,files=files,engine_ref=ref(R/'ep_perf_native_wv_modes_draft.py'),mode_contract_ref=ref(R/'mode_contract.py'),parser_ref=ref(R/'mode_aware_terminal.py'),native_entry_template_ref=ref(F/'native_midtag_v3'),scoped_authorization_ref=ref(P('/root/data/ep_l2_full_workload_performance_20261027_v1/execution_midtag_v3_20261104_v1/midtag/control/USER_AUTHORIZATION.json')),formal_Host_proof_ref=ref(F/'FORMAL_DRY_HOST_RECEIPT.json'),formal_Host_checks=143,prior_CPU_application_fixtures_reexecuted=False,new_models=0,registry_written=False,global_Native_written=False,Source_ELF_unchanged=True,application_NI='NOT_MEASURED')
dr=put(F/'FORMAL_DELIVERY_MANIFEST.json',delivery);print(json.dumps(dict(delivery_ref=dr,engine_ref=delivery['engine_ref'],runtime_files=len(owned),host_draft_ref=ref(F/'review_drafts/MAIN_HOST_QUALIFICATION_DRAFT.json'))))

