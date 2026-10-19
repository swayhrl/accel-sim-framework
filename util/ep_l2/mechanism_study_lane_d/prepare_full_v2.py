"""D's finite V2 preparation: small metadata only, never launch or qualify.

Prior four registrations and opportunity table are immutable inputs. All final
runtime/binary identities and performance values remain unassigned until E.
"""
import csv
import datetime as dt
import fcntl
import hashlib
import json
from pathlib import Path
import subprocess

REPO = Path(__file__).resolve().parents[3]
OLD = REPO/'docs/ep_l2/mechanism_study_2026_10_19_v1/lane_d'
OUT = OLD/'full_system_v2'
SHARED = Path('/workspace/ep_l2_ft20261016_shared')
AUTH = 'b2e5328aca825d6e9ebfe09e46fa208957834636'
CAMPAIGN = 'EPL2_MECHANISM_STUDY_20261019_V1'
WORKLOADS = ['sad', 'vectorAdd_4M', 'cfd_097k', 'convolutionSeparable', 'FWT_7_21', 'btree', 'dwt2d']
REPS = ['convolutionSeparable', 'FWT_7_21']
UNKNOWN = 'UNKNOWN'

def sha(data): return hashlib.sha256(data).hexdigest()
def dump(name, obj):
    path=OUT/name; path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def table(name, rows):
    with (OUT/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(dict.fromkeys(k for r in rows for k in r)),lineterminator='\n')
        w.writeheader();w.writerows(rows)
def git(ref, path): return subprocess.check_output(['git','show',ref+':'+path],cwd=REPO)

def matrix():
    profiles={
      'S': (0,0,0,0,'NONE',16,'传统静态写回'),
      'F': (1,1,1,1,'NONE',0,'统一写回＋动态淘汰保留＋只读T/M'),
      'F_MINUS_W': (0,1,1,1,'NONE',16,'关统一写回，保留动态淘汰与只读'),
      'F_MINUS_V': (1,0,1,1,'NONE',0,'关可选淘汰保留'),
      'F_MINUS_R': (1,1,0,0,'NONE',0,'关只读T/M'),
      'W_ONLY': (1,0,0,0,'NONE',0,'仅统一写回'),
      'WV_T': (1,1,1,0,'NONE',0,'统一写回与动态淘汰＋仅标签脱离'),
      'WV_M': (1,1,0,1,'NONE',0,'统一写回与动态淘汰＋仅line-MSHR绕过'),
      'F_FIXED_V64': (1,'FIXED64',1,1,'NONE',0,'同预算固定64项淘汰区＋统一写回与只读'),
      'S_COPY_FREE': (0,0,0,0,'COPY_FREE',16,'传统结构免复制服务诊断'),
      'S_L2_DATA_FREE': (0,0,0,0,'L2_DATA_FREE',16,'传统结构免L2数据bank争用诊断'),
      'F_L2_DATA_FREE': (1,1,1,1,'L2_DATA_FREE',0,'完整方案免L2数据bank争用诊断'),
      'S_WB64': (0,0,0,0,'NONE',64,'同预算静态64项写回容量对照')}
    rows=[]
    def add(w,p,g,priority,anchor=None):
        W,V,T,M,diagnostic,wb,cn=profiles[p]
        dependency='FINAL_A_SOURCE_BINARY_PROFILE_AND_E_NATIVE_QUALIFICATION'
        if p=='F_MINUS_W':dependency+=';DEPENDENT_CONTROL_UNSUPPORTED_UNTIL_A_PROVES_V_R_RETAINED'
        if p=='F_FIXED_V64':dependency+=';FIXED64_1104_FULL_DIRTY_RO_COMBINATION_REQUIRED_CURRENT_CLEAN_ONLY_NOT_SUFFICIENT'
        if p=='S_WB64':dependency+=';A_MUST_FREEZE_WHICH_OTHER_ROLES_PAY_48_ADDITIONAL_WB_SLOTS'
        rows.append(dict(condition_id=f'V2_{w}_{p}',workload=w,profile=p,group=g,priority=priority,
          W=W,V=V,T=T,M=M,diagnostic=diagnostic,static_wb_slots=wb,chinese=cn,
          anchor_condition_id=f'V2_{w}_{anchor}' if anchor else '',
          final_binary='UNASSIGNED_A_E',runtime_config_sha256=UNKNOWN,status='PLANNED_NOT_RUN_NOT_QUALIFIED',
          dependency=dependency,total_payload_slots=1168,resident_tags=1024,shared_directory_entries=128,
          descriptors=512,line_mshr=128,banks=4,ops_per_bank_physical_cycle=1))
    for w in WORKLOADS:
        for p in ['S','F']:add(w,p,'MAIN',1 if w in REPS else 2,'S' if p=='F' else None)
    for w in REPS:
        for p in ['F_MINUS_W','F_MINUS_V','F_MINUS_R']:add(w,p,'REMOVE_ONE',3,'F')
    for w in REPS:add(w,'W_ONLY','W_ONLY',3,'S')
    for p in ['WV_T','WV_M']:add(REPS[0],p,'RO_FACTORIAL',3,'F_MINUS_R')
    add(REPS[0],'F_FIXED_V64','FIXED_VICTIM',3,'F')
    for w in REPS:
        for p in ['S_COPY_FREE','S_L2_DATA_FREE','F_L2_DATA_FREE']:
            add(w,p,'LOCAL_DIAGNOSTIC',4,'F' if p.startswith('F_') else 'S')
    add(REPS[0],'S_WB64','STATIC_CAPACITY',4,'S')
    assert len(rows)==32 and len({r['condition_id'] for r in rows})==32
    return rows

def inputs():
    scope=json.loads(Path('/workspace/ep_l2_mechanism_lane3_v1/derived_r2/INPUT_SCOPE.json').read_text())
    byname={r['workload']:r for r in scope}
    selection=json.loads((OLD/'INPUT_SELECTION.json').read_text())
    candidate={r['workload']:r for r in selection['candidates']}
    rows=[]
    immutable={}
    for w in WORKLOADS:
        prior=OLD/'input_registrations'/f'{w}.json'
        if prior.exists():
            reg=json.loads(prior.read_text());f=reg['full_input_identity'];src=f['runtime_independent_input_source']
            entry=Path(src['entry_trace_path']);commands=src['command_list'];trace=f['trace_content_sha256']
            expected=f['expected_full_instructions'];prov=src['capture_provenance']
            immutable[w]={'path':str(prior.relative_to(REPO)),'sha256':sha(prior.read_bytes()),'selection_id':reg['selection_id']}
        else:
            old=byname[w];entry=Path(old['entry']);commands=old['commandlist_literal'];trace=old['trace']
            expected=old['runtime_instruction_count'];prov=old['literal_capture_script']
            src={'entry_trace_name':entry.name,'entry_trace_path':str(entry),'command_list':commands,
                 'capture_provenance':prov,'source_revision':UNKNOWN,'epoch_range':{'epochs':'all','scope':'full_application'},
                 'trace_files':[{'name':n,'path':str(entry.parent/n)} for n in [entry.name]+[x.strip() for x in commands.splitlines() if x.strip().startswith('kernel')]]}
            reg={'schema':'EPL2_MECHANISM_D_INPUT_PREREGISTRATION_V1','campaign_id':CAMPAIGN,
              'authority_commit':AUTH,'selected_by':'D','selection_id':'D_V2_'+w,
              'selection_utc':selection['selected_at_utc'],'selection_time_note':'V2 mandated original five; time above refers to prior original-five selection, V2 adoption recorded separately',
              'full_input_identity':{'workload':w,'trace_content_sha256':trace,
                'trace_hash_evidence':'existing accepted complete input; E freshly rebinds current bytes',
                'runtime_independent_input_source':src,'expected_full_instructions':expected,
                'comparison_groups':['V2_MAIN_'+w]},'not_a_launch_authorization':True,
              'readonly_certificate':'UNKNOWN_NOT_GRANTED','producer_binary':'UNASSIGNED_A_OWNER','preserve_budget':40,
              'rationale':'V2 common original-five roster; no candidate speedup selection',
              'expected_exit':'full command list; expected instructions; normal exit and actual complete drain'}
            dump('input_registrations/'+w+'.json',reg)
        present=entry.exists() and entry.read_text()==commands
        bodies=[entry.parent/n.strip() for n in commands.splitlines() if n.strip().startswith('kernel')]
        sizes=[{'path':str(p),'bytes':p.stat().st_size if p.exists() else None,'exists':p.exists()} for p in bodies]
        if not all(r['exists'] for r in sizes):present=False
        cert= w=='convolutionSeparable'
        row=dict(workload=w,display={'sad':'SAD','vectorAdd_4M':'向量加法','cfd_097k':'CFD','convolutionSeparable':'可分离卷积','FWT_7_21':'快速Walsh变换','btree':'B树','dwt2d':'二维小波'}[w],
          input_scale={'sad':'reference.bin/frame.bin frozen3-kernel commandlist','vectorAdd_4M':'4000000 elements','cfd_097k':'fvcorr.domn.097K','convolutionSeparable':'3072x3072','FWT_7_21':'logK7 logD21','btree':'mil.txt + command.txt','dwt2d':'rgb.bmp 1024x1024 f=-5 l=3'}[w],
          commandlist_path=str(entry),commandlist_literal=commands,commandlist_sha256=sha(commands.encode()),
          full_trace_content_sha256=trace,kernel_count=len(bodies),body_files=sizes,
          total_body_bytes=sum(r['bytes'] or 0 for r in sizes),expected_full_instructions=expected,
          capture_provenance=prov,application_source_revision=UNKNOWN,
          input_availability='COMMANDLIST_AND_ALL_BODIES_PRESENT_NOT_FRESH_E_QUALIFICATION' if present else 'INPUT_IDENTITY_OR_AVAILABILITY_HOLD',
          non_atomic_scope=byname[w]['atomic_scope'] if w in byname else {'scope':'UNKNOWN_REQUIRES_E_COMPLETE_INPUT_CHECK'},
          readonly_evidence='CONV_MODEL_SCOPE_REVIEW_ACCEPTED_NATIVE_NOT_QUALIFIED' if cert else 'UNCERTIFIED_FULL_EPOCH_UNKNOWN',
          model_certified_lines=294912 if cert else UNKNOWN,
          model_certified_read_lane_references=11698176 if cert else UNKNOWN,
          model_line_coverage=1/3 if cert else UNKNOWN,
          model_read_reference_coverage=11698176/(11698176+11747328) if cert else UNKNOWN,
          model_coverage_denominator='all distinct global lines including write-only; read references count lane-line touches',
          active_runtime_certified_lines=0,active_runtime_coverage=0,
          active_runtime_coverage_note='No qualified final runtime/oracle binding yet; operational enabled coverage0 is NOT proof of zero read-only opportunity',
          fallback='Every uncertified line normal native path; no other-input certificate reuse; fail closed on certified-line writer/host-overlap; all scopes require E runtime acceptance',
          host_updates_after_kernel=any(n.startswith('MemcpyHtoD,') for n in commands.split('kernel',1)[-1].splitlines()),
          final_qualification='PENDING_A_COMBINED_RELEASE_E_NATIVE_AND_INPUT_ACCEPTANCE',
          original_registration=immutable.get(w),new_registration=None if prior.exists() else 'input_registrations/'+w+'.json')
        rows.append(row)
    dump('SEVEN_INPUTS.json',{'authority':AUTH,'campaign_id':CAMPAIGN,'workloads':rows,'immutable_prior_registrations':immutable})
    table('INPUT_READONLY_COVERAGE.csv',[{k:(json.dumps(v,ensure_ascii=False) if isinstance(v,(list,dict)) else v) for k,v in r.items() if k not in ['commandlist_literal','capture_provenance','body_files']} for r in rows])
    return rows

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    for name in ['MASTER_FULL_SYSTEM_V2.md','MATRIX_AND_ACCEPTANCE_V2.md','RESOURCE_AND_STORAGE_V2.md','CAMPAIGN_FULL_V2.json','LANE_CONTINUATIONS_V2.md']:
        data=git(AUTH,'docs/ep_l2/chatgpt_handoff/full_system_2026_10_19_v2/'+name)
        # Authority bytes need no full duplicate in the working tree.
        dump('authority/'+name+'.identity.json',{'commit':AUTH,'path':'docs/ep_l2/chatgpt_handoff/full_system_2026_10_19_v2/'+name,'sha256':sha(data),'fully_read':True})
    rows=matrix();table('MATRIX_32.csv',rows)
    dump('MATRIX_32.json',{'schema':'D_FULL_SYSTEM_V2_PLAN_NOT_LAUNCH_AUTHORIZATION','authority':AUTH,'campaign_id':CAMPAIGN,
      'conditions':rows,'representatives':REPS,'RO_fixed_capacity_representative':REPS[0],
      'selection_reason':'Conv measured baseline line-MSHR+WB pressure and actual model-only RO subset; FWT baseline WB/copy contrast; no new F speedup observed',
      'fixed_victim_policy':'preexisting B fixed64/1104, bank quotas16/276; does not grant clean-only final dirty+RO qualification',
      'old_14_preparation':'PREPARED_SUPERSEDED_ORDER_PRESERVED_NOT_AUTOMATICALLY_RUN','planned':32,'reserve':8,'cumulative_max':40,
      'final_release_binding':'UNASSIGNED_A_E','policy':'same final binary, same nonresearch config and fixed policy; different per-input independently accepted certificates only; UNKNOWN never zero'})
    inp=inputs()
    with (SHARED/'REGISTRY.lock').open() as lock:
        fcntl.flock(lock,fcntl.LOCK_SH)
        raw=(SHARED/'RUN_REGISTRY.json').read_bytes();allreg=json.loads(raw);r=allreg['mechanism_study_20261019_v1']
    snapshot={k:r.get(k) for k in ['campaign_id','authority_commit','owner','status','actual_starts','maximum_actual_starts','controller']}
    snapshot.update(accepted_pairs=len(r.get('accepted_pairs',{})),accepted_results=len(r.get('accepted_results',{})),
      qualifications=len(r.get('qualifications',{})),registry_sha256_at_read=sha(raw),at_utc=dt.datetime.now(dt.timezone.utc).isoformat(),
      V2_authorized_max=40,V2_adoption_owner='E_ONLY_NO_D_LEDGER_MUTATION',counter_reset=False,
      remaining_authorized_starts=40-int(r['actual_starts']),plan_new_starts=32,
      budget_feasibility='PENDING_E_ADOPTION_AND_DEDUP_WITH_EXISTING_ATTEMPTS',no_background_waiter=True)
    dump('E_STATE_AT_PREPARATION.json',snapshot)
    print(json.dumps({'conditions':len(rows),'inputs':len(inp),'actual_starts':r['actual_starts'],'old_four_unchanged':4,'accepted_pairs':snapshot['accepted_pairs']}))

if __name__=='__main__':main()
