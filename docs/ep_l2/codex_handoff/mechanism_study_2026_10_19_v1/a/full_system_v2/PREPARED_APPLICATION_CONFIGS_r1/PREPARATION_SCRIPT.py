"""Prepare exact32-cell V2 draft; no compiler, trace-body scan or launch."""
from pathlib import Path
import json, hashlib, datetime, re

BOOK = Path('/workspace/ep_l2_ms20261019_a_common_v1')
OUT = BOOK/'PREPARED_FULL_V2_APPLICATION_OVERLAYS_r1'
OUT.mkdir(exist_ok=False)
A = Path('/workspace/worktrees/accel-sim-ep-l2-ms20261019-a-core-v1/docs/ep_l2/codex_handoff/mechanism_study_2026_10_19_v1/a')
E = Path('/workspace/worktrees/accel-sim-ep-l2-ms20261019-e-eval-v1/docs/ep_l2/review_packs/MS20261020_E_REMAINING_SIX_ORACLE_REVIEW_r1')
CORE = Path('/workspace/worktrees/gpgpu-sim-ep-l2-ms20261019-a-r3-victim-full-v1')
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
index = json.loads((E/'RUN_LEDGER_INPUT_REVIEW_INDEX.json').read_text())
inputs = {}
for name, binding in index.items():
    review_path = Path(binding['path'])
    assert sha(review_path) == binding['sha256']
    review = json.loads(review_path.read_text())
    assert not binding['runtime_qualification']
    assert review['status'].startswith('INPUT_ORACLE_ARTIFACT_AND_SCOPE_REVIEW_PASS')
    manifest_path = Path(review['manifest_path'])
    assert sha(manifest_path) == review['manifest_sha256']
    manifest = json.loads(manifest_path.read_text())
    ranges = manifest_path.parent/'certified_ranges.csv'
    assert sha(ranges) == review['artifacts']['certified_ranges.csv']['sha256']
    commandlist = Path(manifest['commandlist'])
    assert sha(commandlist) == manifest['commandlist_sha256']
    inputs[name] = dict(input_review_path=str(review_path), input_review_sha256=binding['sha256'],
        manifest_path=str(manifest_path), manifest_sha256=review['manifest_sha256'],
        ranges_path=str(ranges), ranges_sha256=sha(ranges), commandlist=str(commandlist),
        commandlist_sha256=manifest['commandlist_sha256'], trace_content_sha256=review['trace_content_sha256'],
        certified_model_lines=review['counts'].get('CERTIFIED_RO',{}).get('lines',0),
        runtime_qualified=False, fresh_full_trace_rehash_by_E_required=True)
assert len(inputs)==7
conv='D_V1_convolutionSeparable';fwt='D_V1_FWT_7_21';representatives=[conv,fwt]
assert inputs[fwt]['certified_model_lines']==0
common = {}
for line in (A/'profiles/S_observer0.config').read_text().splitlines():
    if not line.startswith('-'):continue
    key,value=line.split(None,1);assert key not in common;common[key]=value
common.update({'-gpgpu_ep_l2_ms_observer':'1','-gpgpu_ep_l2_b0_stats':'1',
 '-gpgpu_ep_l2_m0a_stats':'1','-gpgpu_ep_l2_i_mem_all_data':'0',
 '-gpgpu_ep_l2_tvd_clean':'0','-gpgpu_ep_l2_tvd_dirty':'0','-gpgpu_ep_l2_tvd_fixed_entries':'0',
 '-gpgpu_ep_l2_ro_tag_detach':'0','-gpgpu_ep_l2_ro_line_mshr_bypass':'0'})
registered=set(re.findall(r'"(-gpgpu_ep_l2_[a-zA-Z0-9_]+)"',(CORE/'src/gpgpu-sim/gpu-sim.cc').read_text()))
assert set(common)<=registered
modes={
 'S':dict(W=0,V=0,T=0,M=0),
 'F':dict(W=1,V=1,T=1,M=1),
 'F_MINUS_V':dict(W=1,V=0,T=1,M=1),
 'F_MINUS_R':dict(W=1,V=1,T=0,M=0),
 'W_ONLY':dict(W=1,V=0,T=0,M=0),
 'WV_T_ONLY':dict(W=1,V=1,T=1,M=0),
 'WV_M_ONLY':dict(W=1,V=1,T=0,M=1),
 'S_COPY_FREE':dict(W=0,V=0,T=0,M=0,COPY_FREE=1),
 'S_L2_DATA_FREE':dict(W=0,V=0,T=0,M=0,DATA_FREE=1),
 'F_L2_DATA_FREE':dict(W=1,V=1,T=1,M=1,DATA_FREE=1),
 'STATIC_WB64':dict(W=0,V=0,T=0,M=0,STATIC64=1),
}
conditions=[]
def add(group,app,mode):
    ordinal=len(conditions)+1
    row=dict(ordinal=ordinal,group=group,selection_id=app,profile=mode,
             runtime_qualified=False,scientific_condition_not_start_authorization=True,
             input_identity=inputs[app],binary_sha256=None)
    if mode in ('F_MINUS_W','F_FIXED64_DIRTY_RO'):
        row.update(status='DEPENDENT_CONTROL_UNSUPPORTED' if mode=='F_MINUS_W' else 'FULL_DIRTY_RO_QUOTA_UNIMPLEMENTED',
                   overlay=None,not_substituted_by='S or clean64')
    else:
        bits=modes[mode];cfg=dict(common)
        cfg['-gpgpu_ep_l2_ft_mode']=str(2 if bits['W'] else 1)
        cfg['-gpgpu_ep_l2_tvd_clean']=cfg['-gpgpu_ep_l2_tvd_dirty']=str(bits['V'])
        cfg['-gpgpu_ep_l2_ro_tag_detach']=str(bits['T']);cfg['-gpgpu_ep_l2_ro_line_mshr_bypass']=str(bits['M'])
        cfg['-gpgpu_ep_l2_diag_copy_free']=str(bits.get('COPY_FREE',0))
        cfg['-gpgpu_ep_l2_diag_l2_data_free']=str(bits.get('DATA_FREE',0))
        cfg['-gpgpu_ep_l2_static_s64']=str(bits.get('STATIC64',0))
        if bits['T'] or bits['M']:
            inp=inputs[app]
            cfg.update({'-gpgpu_ep_l2_ro_ranges':inp['ranges_path'],
                '-gpgpu_ep_l2_ro_ranges_sha256':inp['ranges_sha256'],
                '-gpgpu_ep_l2_ro_manifest':inp['manifest_path'],
                '-gpgpu_ep_l2_ro_manifest_sha256':inp['manifest_sha256'],
                '-gpgpu_ep_l2_ro_scope':'TRACE_MODEL_CLOSED_WORLD'})
        assert set(cfg)<=registered and all(k.startswith('-gpgpu_ep_l2_') for k in cfg)
        # No synthetic fixture geometry/clock/DRAM/queue/ROP overrides.
        assert cfg['-gpgpu_ep_l2_wbuf_entries']=='16' and cfg['-gpgpu_ep_l2_bank_ops']=='1'
        assert cfg['-gpgpu_ep_l2_descriptor_pool_size']=='512' and cfg['-gpgpu_ep_l2_wad_entries']=='128'
        assert cfg['-gpgpu_ep_l2_tvd_fixed_entries']=='0'
        if mode=='STATIC_WB64':assert cfg['-gpgpu_ep_l2_static_s64']=='1' and cfg['-gpgpu_ep_l2_ft_mode']=='1'
        filename=f'{ordinal:02}_{app}_{mode}.config'
        text='# DRAFT ONLY: not native-qualified and not application launch authority.\n'
        text+='# Append after the SAME accepted H0 base/trace/target/nonresearch overlays.\n'
        text+='# Same future binary and uncapped whole commandlist; E revalidates full trace bytes.\n'
        text+=''.join(f'{k} {v}\n' for k,v in cfg.items())
        p=OUT/filename;p.write_text(text)
        row.update(status='SOURCE_CONFIG_PREPARED_PENDING_NATIVE_AND_E',overlay=filename,
            overlay_sha256=sha(p),mechanism=bits,effective_overlay_options=cfg,
            model_certified_lines_applied=inputs[app]['certified_model_lines'] if bits['T'] or bits['M'] else 0,
            physical_budget=dict(Tags=1024,payload=1168,WAD_TVD=128,D=512,per_address=32,banks=4,P=1),
            static_partition='1024resident/80landing/64WB; legacy wbuf_entries16 anchor' if bits.get('STATIC64') else None)
    conditions.append(row)
# Main first representatives then other five: exactly14, no app-start duplication.
for app in representatives+[x for x in inputs if x not in representatives]:
    for mode in ['S','F']:add('seven_workload_common_S_F',app,mode)
for app in representatives:
    for mode in ['F_MINUS_W','F_MINUS_V','F_MINUS_R']:add('two_workload_remove_W_V_R',app,mode)
for app in representatives:add('two_workload_W_only',app,'W_ONLY')
for mode in ['WV_T_ONLY','WV_M_ONLY']:add('one_workload_T_only_M_only_on_WV',conv,mode)
add('one_workload_fixed_victim_on_WR',conv,'F_FIXED64_DIRTY_RO')
for app in representatives:
    for mode in ['S_COPY_FREE','S_L2_DATA_FREE','F_L2_DATA_FREE']:add('two_workload_local_diagnostics',app,mode)
add('one_workload_static_WB64',conv,'STATIC_WB64')
assert len(conditions)==32
assert sum(c['overlay'] is not None for c in conditions)==29
assert sum(c['profile']=='F_MINUS_W' for c in conditions)==2
# F uses the identical mechanism policy on all7, including empty-certifiedFWT.
frows=[c for c in conditions if c['profile']=='F'];assert len(frows)==7
assert all(c['mechanism']==dict(W=1,V=1,T=1,M=1) for c in frows)
result=dict(schema='A_PREPARED_FULL_V2_APPLICATION_OVERLAYS_R1',UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
 status='DRAFT_SOURCE_PREPARATION_NOT_RELEASE_OR_LAUNCH_AUTHORIZATION',authority='b2e5328aca825d6e9ebfe09e46fa208957834636',
 campaign_id='EPL2_MECHANISM_STUDY_20261019_V1',source_core='e4ac03c730cd42009a3d94cc45ee16ee3ef6cd9a',
 runtime_framework='9dd1ee57a83d83b56b7874bc7c716185ab52c8f7',build_control_frozen='41d109496ede0158cb544fe2ce69ca45a89661b2',
 native_qualified=False,binary_sha256=None,full_starts=0,cumulative_limit=40,planned_conditions=32,reserve_starts=8,
 available_source_overlays=29,unsupported_conditions=3,conditions=conditions,
 notes=['No C++/native/trace-body/SQLite scan/app start/registry write/source worktree change.',
 'Metadata/candidate/ranges/commandlist bytes bound to E accepted input-scope reviews only; no runtime correctness or live trace-byte qualification.',
 'Seven fixedF policies, no Conv certificate reuse; FWT0 applied model coverage with T/M bothON.',
 'Conv/FWT remain representatives. Single-representative control assignment defaultsConv before any fullF results; E/D must preserve preregistered identity/order and scientific choice.',
 'All observer1 overlays require actual producer equivalence and E acceptance. No nonresearch geometry/ROP/DRAM/clock/queue changes.',
 'S64 is fixed1168 with 80landing/64WB, not wbuf_entries64 which would enlarge physical data.',
 'A will publish these drafts on execution branch after the current build handoff, without invalidating pending/live bound driverHEAD.'])
(OUT/'MATRIX.json').write_text(json.dumps(result,indent=2)+'\n')
(OUT/'README.md').write_text('# Prepared full-system V2 application overlays\n\nDRAFT only:32 planned cells,29 source overlays,3 unsupported placeholders. No runtime qualification, binary, complete app start or launch permission. E remains sole scheduler and counter. Current frozen common build driver source is unchanged.\n\nEvery overlay contains research-only options; sameH0 geometry, ROP, queues, DRAM and whole-input termination must be supplied by E. FixedF has W/V/T/M ON for all seven inputs, each with its own accepted model certificate; FWT uses its genuine empty ranges. Observer1 requires real equivalence. F-minus-W and full fixeddirtyRO are explicit unsupported entries without runnable config.\n\nStaticWB64 uses static_s64=1 with legacy16 anchor to keep1168 slots, trading48 landing slots for48WB slots. It does not set wbuf_entries64. The full32 matrix and reserve8 do not alter actual cumulative40. A/E native validation and independent E acceptance are mandatory before final same-binary publication.\n')
print(json.dumps({'draft':str(OUT),'conditions':len(conditions),'overlays':29,'unsupported':3,'main14_ready_for_future_qualification':True,'fixed_FWT_T_M':[1,1],'actual_compile':0,'native':0,'apps':0,'matrix_sha256':sha(OUT/'MATRIX.json')},indent=2))
