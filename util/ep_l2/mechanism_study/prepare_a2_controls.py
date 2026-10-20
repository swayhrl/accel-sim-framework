"""Prepare bounded main61 profile candidates; no controller, native execution or build."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import re
import shlex
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
CORE = Path('/workspace/worktrees/gpgpu-sim-ep-l2-ms20261020-a-r39-own-pending-v1')
BASE = ROOT/'docs/ep_l2/review_packs'
REGISTRY = Path('/workspace/ep_l2_ft20261016_shared/RUN_REGISTRY.json')
E_HEAD = '13718839b515542f332eca6a845701a8dbb9a922'
IDENTITY = json.loads((BASE/'MS20261020_A2_FORMAL_WAD_PRODUCER_RELEASE_r1/RELEASE.json').read_text())['source_identity']
MODES = dict(W_ONLY=(1,0,0,0), F_MINUS_R=(1,1,0,0), F_MINUS_V=(1,0,1,1),
    WV_M_ONLY=(1,1,0,1), WV_T_ONLY=(1,1,1,0), S_COPY_FREE=(0,0,0,0),
    S_L2_DATA_FREE=(0,0,0,0), F_L2_DATA_FREE=(1,1,1,1))
ALIASES = dict(WV_M_ONLY='WV_M', WV_T_ONLY='WV_T')
APPS = ('convolutionSeparable','cfd_097k','dwt2d')


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda: f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()


def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()


def ref(path):
    return dict(path=str(Path(path)),sha256=sha(path),bytes=Path(path).stat().st_size)


def read(path): return json.loads(Path(path).read_text())
def save(path,value): path.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--batch',choices=('1','2'),required=True)
    args=parser.parse_args();profiles=('W_ONLY','F_MINUS_R') if args.batch=='1' else tuple(k for k in MODES if k not in ('W_ONLY','F_MINUS_R'))
    out=BASE/('MS20261020_A2_MAIN61_CONTROL_BATCH'+args.batch+'_r1')
    assert not out.exists(),'Preserve previously published batch'
    original=REGISTRY.read_bytes();state=json.loads(original)['mechanism_study_20261019_v1']
    assert state['actual_starts']<=40
    sys.path.insert(0,'/workspace/worktrees/accel-sim-ep-l2-ft20261016-lane5-v1/util/ep_l2/ft_lane5')
    from headroom_config import options  # Pure existing parser; no Registry/Coordinator constructed.
    main_binary=Path('/workspace/build/ep-l2-ms20261020-a-wad-pending-r41/accel-sim.out')
    assert sha(main_binary)==IDENTITY['binary_sha256']
    assert subprocess.check_output(['git','-C',str(CORE),'rev-parse','HEAD']).decode().strip()==IDENTITY['core_source_commit']
    assert not subprocess.check_output(['git','-C',str(CORE),'status','--porcelain=v1']).strip()
    registered=set(re.findall(r'"(-gpgpu_ep_l2_[a-zA-Z0-9_]+)"',(CORE/'src/gpgpu-sim/gpu-sim.cc').read_text()))
    out.mkdir();rows=[];inputs={}
    for app in APPS:
        pair=state['accepted_pairs']['V2_MAIN_'+app+'_S_F_MAIN61'];assert pair['status']=='CURRENT_ACCEPTED'
        templates={};qualifications={}
        for side in ('left','right'):
            endpoint=pair['endpoints'][side];attempt=next(a for a in state['attempts'] if a['attempt_id']==endpoint['attempt_id'])
            receipt=read(endpoint['path']);assert sha(endpoint['path'])==endpoint['sha256']
            assert receipt['status']=='COMPLETE_VALID'
            template=read(Path(attempt['result_directory'])/'input_spec.json')
            q=state['qualifications'][endpoint['qualification_id']];assert sha(q['path'])==q['sha256']
            assert q['qualification']['source_identity']==IDENTITY
            assert options([x['path'] for x in template['configs']])==q['qualification']['supported_profiles'][attempt['profile']]['effective_options']
            templates[attempt['profile']]=template;qualifications[attempt['profile']]=q
        inputs[app]=dict(accepted_pair=pair,existing_qualifications={k:dict(artifact=ref(q['path']),profiles=list(q['qualification']['supported_profiles'])) for k,q in qualifications.items()},
            trace_content_sha256=templates['F']['identity']['trace_content_sha256'],
            expected_full_instructions=qualifications['F']['qualification'].get('input_scope_admission'),
            input_proof=qualifications['F']['qualification']['input_scope_admission'],
            trace_body_rehashed_by_A2=False,trace_note='Use exact E accepted full-input content manifest; E refreshes mandatory full trace rehash before admission. No trace rescanning or simulation here.')
        for profile in profiles:
            bits=dict(zip(('W','V','T','M'),MODES[profile]));is_static=profile.startswith('S_');template=copy.deepcopy(templates['S' if is_static else 'F']);parent=qualifications['S' if is_static else 'F']
            oldopts=options([x['path'] for x in template['configs']]);cfg=options([template['configs'][-1]['path']])
            cfg.update({'-gpgpu_ep_l2_ft_mode':str(2 if bits['W'] else 1),
                '-gpgpu_ep_l2_tvd_clean':str(bits['V']),'-gpgpu_ep_l2_tvd_dirty':str(bits['V']),
                '-gpgpu_ep_l2_tvd_fixed_entries':'0','-gpgpu_ep_l2_ro_tag_detach':str(bits['T']),
                '-gpgpu_ep_l2_ro_line_mshr_bypass':str(bits['M']),
                '-gpgpu_ep_l2_diag_copy_free':str(int(profile=='S_COPY_FREE')),
                '-gpgpu_ep_l2_diag_l2_data_free':str(int(profile.endswith('L2_DATA_FREE')))})
            if not (bits['T'] or bits['M']):
                cfg={k:v for k,v in cfg.items() if not k.startswith(('-gpgpu_ep_l2_ro_ranges','-gpgpu_ep_l2_ro_manifest')) and k!='-gpgpu_ep_l2_ro_scope'}
            assert set(cfg)<=registered
            directory=out/app/profile;directory.mkdir(parents=True)
            overlay=directory/'profile.config';overlay.write_text('# A2 main61 source-supported candidate; NOT E-qualified or launch-authorized.\n'+''.join(k+' '+v+'\n' for k,v in cfg.items()))
            template['configs'][-1]['path']=str(overlay)
            effective=options([x['path'] for x in template['configs']])
            assert all(oldopts[k]==v for k,v in effective.items() if not k.startswith('-gpgpu_ep_l2_'))
            for k,v in {'payload_mode':'2','wbuf_entries':'16','descriptor_pool_size':'512','descriptor_per_line_cap':'32','wad_entries':'128','bank_ops':'1','static_s64':'0','wb_local_cap':'0','mq2':'0','rg1':'0','ideal_meta':'0','ideal_read_hit':'0','ideal_wb':'0','i_mem_all_data':'0','ms_observer':'1','payload_policy':'0'}.items(): assert effective['-gpgpu_ep_l2_'+k]==v,(app,profile,k)
            assert effective['-gpgpu_cache:dl2']=='S:64:128:16,L:B:m:L:P,A:128:1,128:0,32'
            assert effective['-gpgpu_cache:dl2_texture_only']=='0'
            assert not (cfg['-gpgpu_ep_l2_diag_copy_free']=='1' and (bits['W'] or bits['V'] or bits['T'] or bits['M']))
            cert={}
            if bits['T'] or bits['M']:
                for kind in ('ranges','manifest'):
                    key='-gpgpu_ep_l2_ro_'+kind;assert sha(cfg[key])==cfg[key+'_sha256'];cert[kind]=ref(cfg[key])
                manifest=read(cfg['-gpgpu_ep_l2_ro_manifest']);assert manifest['epoch']=='whole_commandlist' and manifest['scope']==cfg['-gpgpu_ep_l2_ro_scope']=='TRACE_MODEL_CLOSED_WORLD'
            semantics=copy.deepcopy(template['profile_semantics']);semantics['effective_options']=effective;semantics['research_switches']=bits
            semantics['feature_vector'].update(unified_wb=bool(bits['W']),tvd=bool(bits['V']),ro_tag_detach=bool(bits['T']),ro_line_mshr_bypass=bool(bits['M']))
            semantics['ideal_vector'].update(copy_free=profile=='S_COPY_FREE',l2_data_free=profile.endswith('L2_DATA_FREE'))
            semantics['labels'].update(diagnostic=profile in ('S_COPY_FREE','S_L2_DATA_FREE','F_L2_DATA_FREE'),oracle=bool(bits['T'] or bits['M']),readonly_scope='TRACE_MODEL_CLOSED_WORLD' if bits['T'] or bits['M'] else 'OFF',victim_scope='CLEAN_DIRTY_PENDING_INFLIGHT' if bits['V'] else 'OFF')
            if not (bits['T'] or bits['M']): semantics.pop('readonly_input_review',None)
            template.update(profile=ALIASES.get(profile,profile),profile_semantics=semantics,labels=semantics['labels'],qualification_id='PENDING_E_INDEPENDENT_PROFILE_QUALIFICATION',parser=parent['qualification']['terminal_parser'])
            template['identity']['feature_vector']=semantics['feature_vector'];template['identity']['ideal_vector']=semantics['ideal_vector']
            ordered=[dict(name=x['name'],sha256=sha(x['path']),bytes=Path(x['path']).stat().st_size) for x in template['configs']]
            assets=sorted([dict(name=x['name'],sha256=sha(x['path']),bytes=Path(x['path']).stat().st_size) for x in template['auxiliary_assets']],key=lambda x:x['name'])
            template['identity']['runtime_config_sha256']=hashlib.sha256(canonical(dict(ordered_configs=ordered,auxiliary_assets=assets,environment=template['environment']))).hexdigest()
            invariant=dict(source=IDENTITY,trace=template['identity']['trace_content_sha256'],epoch=template['identity']['epoch_range'],termination=template['identity']['termination_contract'],environment=template['environment'],auxiliary_assets=assets,nonresearch_options={k:v for k,v in effective.items() if k not in semantics['comparison_variable_options']},comparison_variable_options=sorted(semantics['comparison_variable_options']))
            template['comparison_invariants_sha256']=hashlib.sha256(canonical(invariant)).hexdigest()
            template['A2_preparation_status']='DRAFT_NOT_E_QUALIFIED_NOT_QUEUED';template['application_start_authorization']=False
            save(directory/'SPEC_CANDIDATE.json',template)
            planned=any(c['workload']==app and c['profile']==ALIASES.get(profile,profile) for c in state['full_system_matrix']['matrix']['conditions'])
            row=dict(workload=app,A_profile=profile,E_profile=template['profile'],source_supported=True,engineering_config_control='PASS_STATIC_OPTIONS_GEOMETRY_NONRESEARCH_AND_ASSET_HASH_CHECKS_ONLY',E_exact_profile_qualification_present=False,
                source_identity=IDENTITY,overlay=ref(overlay),spec_candidate=ref(directory/'SPEC_CANDIDATE.json'),effective_options=effective,changed_options={k:dict(before=oldopts.get(k),after=effective.get(k)) for k in set(oldopts)|set(effective) if oldopts.get(k)!=effective.get(k)},
                reusable_E_SF_qualification=ref(parent['path']),certificate_binding=cert,
                original32_condition_exists=planned,matrix_gap=None if planned else 'Input/profile replacement in existing32 requires explicit E/D review; no automatic extra allocation.',
                minimum_gap=['E source/profile-specific evidence disposition and fresh qualification artifact (existing qualification covers S/F only).','E terminal parser/profile binding and mandatory config/input checks; no new full-simulator build required.'],application_start_authorization=False)
            rows.append(row)
    save(out/'BATCH.json',dict(schema='A2_MAIN61_CONTROL_CANDIDATES_V1',batch=int(args.batch),status='SOURCE_AND_STATIC_ENGINEERING_CONFIG_READY_FOR_E_PROFILE_REVIEW',E_HEAD_reviewed=E_HEAD,source_identity=IDENTITY,rows=rows,inputs=inputs,
        pure_config_parser=ref('/workspace/worktrees/accel-sim-ep-l2-ft20261016-lane5-v1/util/ep_l2/ft_lane5/headroom_config.py'),
        qualification_count=0,new_application_starts=0,new_native_tests=0,builds=0,actual_starts_observed=state['actual_starts'],maximum_actual_starts=40,central_registry_sha256_before=hashlib.sha256(original).hexdigest()))
    assert REGISTRY.read_bytes()==original,'Concurrent E activity: preserve candidates and re-read current ledger before handoff'
    assert sha(main_binary)==IDENTITY['binary_sha256']
    print(json.dumps(dict(batch=args.batch,pack=str(out),candidates=len(rows),static_checks='PASS',E_new_qualifications=0,starts=0,builds=0)))


if __name__=='__main__':main()
