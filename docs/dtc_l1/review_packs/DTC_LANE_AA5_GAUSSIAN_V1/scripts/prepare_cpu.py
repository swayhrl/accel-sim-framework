"""AA5 immutable prior evidence and legal drafts; new X2 identities deliberately unavailable."""
from common import *
AA4='2b69f5ec8fae85c0ee1bbfe95ac93eb524bb172e';BASE='docs/dtc_l1/review_packs/DTC_LANE_AA4_GAUSSIAN_V1'
FIXED={'AA4':AA4,'AA3':'dab43027467d577291aabd6a5d2812d601219188','X':'49fb5d1b62b6f2387abc2d568bc8ae7543dc0df4','V':V_SHA,'Y2':'d085f98c10010d641ba4cfffa1f58fb8db3b56ee','Z2':'2b633a616dc59efb99973e94bdfa421e28c33fab','U':'16e56912cfd02f2311a1603a29415dee829fd495','OLD_Core':CANDIDATE_CORE}

def main():
    records=[]
    for lane,commit in FIXED.items():
        repo=CORE_REPO if lane=='OLD_Core' else FW_REPO
        assert git(repo,'rev-parse','refs/aa5-bindings/'+lane)==commit
        records.append(dict(lane=lane,commit=commit,tree=git(repo,'rev-parse',commit+'^{tree}'),fetch_back_ref='refs/aa5-bindings/'+lane,role='PRIOR_REFERENCE_NOT_X2_CORE' if lane in ['OLD_Core','X'] else 'FROZEN_INPUT_CONTRACT'))
    write(PACK/'FROZEN_SOURCE_BINDINGS.json',dict(records=records,new_Core_commit=None,new_Framework_producer_commit=None,new_executable_sha256=None,new_libcudart_sha256=None,X2_identity_status='UNAVAILABLE_NOT_PUBLISHED_OR_IDENTIFIED',no_old_Core_fallback=True))
    zpath='docs/dtc_l1/review_packs/DTC_LANE_Z2_U_EVIDENCE_V1/K1_INTERPRETATION_V2.md'
    z=blob(FW_REPO,FIXED['Z2'],zpath);assert z==blob(FW_REPO,'35ff4bc3660dc7653be5d9a3d5a166b610effcf9',zpath)
    write(PACK/'Z2_V2_BINDING.json',dict(final_commit=FIXED['Z2'],original_binding_commit='35ff4bc3660dc7653be5d9a3d5a166b610effcf9',identical=True,blob=git(FW_REPO,'rev-parse',FIXED['Z2']+':'+zpath),sha256=hashlib.sha256(z).hexdigest()))
    inp=json.loads((PACK/'inputs/AA4/INPUT_STAT_IDENTITY.json').read_text());assert len(inp['members'])==510
    for m in inp['members']:
        st=Path(m['path']).stat();assert (st.st_dev,st.st_ino,st.st_size,st.st_mtime_ns,st.st_ctime_ns)==(m['device'],m['inode'],m['bytes'],m['mtime_ns'],m['ctime_ns'])
    ordered=json.loads((PACK/'ORDERED_KERNELS.json').read_text());assert len(ordered)==510 and sum(x['complete_ctas'] for x in ordered)==65790 and sum(x['active_instructions'] for x in ordered)==283685120
    spec0=git_json(FW_REPO,AA4,BASE+'/specs/K0_32x4.json');assert sha(spec0['trace_list'])=='6dc7caba6733657293e8c517467bac28890ae4eb97c732ffd245d7fd1c479fb9'
    assert len(Path(spec0['trace_list']).read_text().splitlines())==513
    write(PACK/'INPUT_IDENTITY_RECHECK.json',dict(status='PASS_PRIOR_MEMBER_SHA_WITH_UNCHANGED_510_STAT_IDENTITIES',source_AA4=AA4,member_stat_receipt_sha256=sha(PACK/'inputs/AA4/INPUT_STAT_IDENTITY.json'),original_T_commit=T_SHA,Gaussian_members=510,commands=513,HtoD_commands=3,ordered_kernel_sha256=sha(PACK/'ORDERED_KERNELS.json'),member_manifest_sha256=sha(PACK/'GAUSSIAN_MEMBERS_SHA256.tsv'),list_sha256=sha(spec0['trace_list']),CTAs=65790,active_thread_instructions=283685120,ROI='FULL_ORIGINAL_LIST_510_KERNELS',body_rehash_or_rescan=False,member_bytes_not_modified=True))
    # Full metadata-only scan; do not use UUIDs to create actual attempt directories.
    roots=sorted(p for p in Path('/workspace').iterdir() if p.is_dir() and p.name.startswith(('dtc-','fast64-')));examined=[];conflicts=[]
    for root in roots:
        for folder,dirs,files in os.walk(root):
            dirs[:]=[n for n in dirs if not n.startswith(('.git','build','source','CMakeFiles')) and n not in ['__pycache__','binaries','lib','include','immutable-runtime']]
            for name in files:
                if name not in ['RUN_START.json','RUN_START.tsv','RUN_TERMINAL.json','RUN_TERMINAL.tsv','PID.json','RUN_MANIFEST.tsv']:continue
                p=Path(folder)/name
                if not p.is_file() or p.stat().st_size>1024**2:continue
                data=p.read_bytes();r=dict(path=str(p),sha256=hashlib.sha256(data).hexdigest(),bytes=len(data));examined.append(r)
                if any(uid in str(p) or uid.encode() in data for _,uid,*_ in POINTS):conflicts.append(r)
    assert not conflicts,conflicts
    write(PACK/'ATTEMPT_BUDGET_AND_UUID_AUDIT.json',dict(utc=now(),aggregate_AA_AA2_AA3_AA4_AA5_actual_starts=0,total_actual_start_limit=4,new_UUIDs_generated=False,reserved_UUIDs={p:u for p,u,*_ in POINTS},roots=list(map(str,roots)),scope='all visible original174 DTC/FAST64 receipt metadata; no disconnected host assertion',examined=examined,conflicts=conflicts))
    reg=[];profiles=[]
    for point,uid,k,sets,ways,cal in POINTS:
        s=git_json(FW_REPO,AA4,BASE+'/specs/'+point+'.json');profile=s['expected_full_default_and_config_echo'];assert len(profile)==267;profiles.append(profile)
        for cfg in s['configs']:
            cfg['path']=str(PACK/'config'/Path(cfg['path']).name);assert sha(cfg['path'])==cfg['sha256']
        s.update(status='DRAFT_NOT_EXECUTABLE_X2_IDENTITY_AND_NORMAL_EXPORT_GATE_PENDING',lane='AA5',candidate_core=None,accepted_core=None,source_Core_commit=None,runtime_path=None,runtime_sha256=None,runtime_library_path=None,runtime_library_sha256=None,build_Framework=None,runtime_environment=None,max_AA_AA2_AA3_AA4_AA5_actual_starts=4,production_runner_sha256=None,strict_collector_sha256=None,execution_guard_sha256=sha(PACK/'scripts/execution_guard.py'),new_Core_effective_echo_status='UNAVAILABLE_X2_NOT_PUBLISHED; inherited267_profile_is_only_frozen_draft',normal_terminal_export_gate='NOT_RUN_NO_X2_IDENTITY',normal_export_fixture_source_sha256=sha(PACK/'scripts/normal_export_fixture.cc'),event_decoder_source_sha256=sha(PACK/'scripts/event_snapshots.py'),Y2_applicability='BOUNDED_OLD_OO_SCOPE; requires independent X2 printing-only diff review',launch_admitted=False)
        # Remove old per-lane control bindings rather than imply they describe a new runtime.
        for key in ['max_AA_AA2_AA3_AA4_actual_starts','strict_guard_sha256','member_stat_identity_sha256','observer_supplement_sha256']:s.pop(key,None)
        s['member_stat_identity_sha256']=sha(PACK/'inputs/AA4/INPUT_STAT_IDENTITY.json');s['observer_supplement_sha256']=sha(PACK/'inputs/AA3/OBSERVER_SUPPLEMENT_V1.md')
        write(PACK/'specs'/f'{point}.json',s)
        reg.append(dict(order=s['priority']+1,point=point,uuid=uid,K=k,sets=sets,ways=ways,timeout_seconds=7200,max_actual_starts=1,historical_calibration_cycles=cal,historical_role='REFERENCE_ONLY_NOT_NEW_K0',new_Core='UNAVAILABLE_X2_NOT_IDENTIFIED',executable_sha256='UNAVAILABLE',libcudart_sha256='UNAVAILABLE',spec_sha256=sha(PACK/'specs'/f'{point}.json'),status='DRAFT_NOT_EXECUTABLE'))
    table(PACK/'PRE_REGISTRATION.tsv',reg)
    deltas=[]
    for key in profiles[0]:
        if len({json.dumps(p[key]) for p in profiles})>1:
            assert key in [K_OPTION,'-gpgpu_dtc_l1_logical_sets','-gpgpu_dtc_l1_logical_ways'];deltas.append(dict(option=key,**{name:json.dumps(profile[key]) for (name,*_),profile in zip(POINTS,profiles)}))
    assert len(deltas)==3;table(PACK/'CONTROLLED_DELTA.tsv',deltas)
    print('PASS fixed prior refs, original510 unchanged identity, inherited267 draft profiles and zero UUID starts. X2 identity/artifacts remain UNAVAILABLE, no executable release.')

if __name__=='__main__':main()
