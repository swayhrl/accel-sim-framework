import pathlib,json,subprocess,textwrap,datetime,hashlib
META=pathlib.Path(__file__).resolve().parent
PATHS=json.loads((META/'paths.json').read_bytes())
REPO=pathlib.Path(PATHS['repo']);BASE=pathlib.Path(PATHS['base'])
BRANCH='hrl/tls-v10-174new-target-exec-v1'
BRIDGE='/root/share/host174_storage_recovery_bridge/20261016_storageops_02'
STORAGE='/root/share/mnt164/huangrulin/host174_storage_recovery'
V9ROOT=STORAGE+'/174new_archive/20261016_storageops_02/increments/20261018_v9'
CUTOFF=datetime.datetime.fromisoformat('2026-10-18T11:30:14.500719+00:00')
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def save(name,value):
 p=BASE/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((json.dumps(value,indent=2)+'\n').encode())
def get(name):return json.loads((BASE/name).read_bytes())
def git(*args):return subprocess.check_output(['git',*args],cwd=REPO)
def remote(code,label,timeout=60,save_receipt=True):
 code=textwrap.dedent(code);started=now()
 p=subprocess.run(['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','ConnectTimeout=15','hrl-174-new',
                   'timeout -k 5s '+str(timeout)+'s python3 -'],input=code,text=True,encoding='utf-8',capture_output=True,timeout=timeout+20)
 record=dict(label=label,host='hrl-174-new',started_at=started,finished_at=now(),exit_code=p.returncode,python_source=code,stdout=p.stdout,stderr=p.stderr)
 with (META/'TLS_V10_RUNTIME_LOG.jsonl').open('ab') as f:f.write((json.dumps(record)+'\n').encode())
 (META/(label+'.json')).write_bytes((json.dumps(record,indent=2)+'\n').encode())
 if p.returncode:raise RuntimeError(label+': '+p.stderr[:2000])
 data=json.loads(p.stdout)
 if save_receipt:save(label+'.json',data)
 print(label+': '+json.dumps(data)[:3500],flush=True);return data


def validate_tls_restore_location(adoption, approval, source_notice):
    canonical='9f1a21a909e437f1e34233b22595d0f7359f3dd3'
    assert adoption['canonical_approval_commit']==source_notice['canonical_approval_commit']==canonical
    assert adoption['status']=='S_AND_T_SAME_CANONICAL_USER_APPROVAL_COMMIT_ADOPTED'
    assert adoption['target_independent_fetch_and_raw_SHA_readback'] is True
    assert source_notice['source_adopts_exact_commit'] is True and source_notice['source_verified_remote_ref_and_raw_blobs'] is True
    assert approval['decision']=='USER_APPROVED_EXPLICIT_AMENDMENT'
    assert approval['base_coordination_commit']=='3a7ea422d3f4301688bd3cb7bcf4431b97f08e90'
    assert approval['original_txid']=='574747b05622a2a0f3ef1a58c11044ee724e5e585d0edd5f0fc32937eda12e6b'
    assert approval['P9_selector_sha256']=='315c008ee1757637b4f68172f93e58c4916cda061936dc4d0125762e6aa9ba0a'
    assert approval['tmpfs_is_persistent_archive'] is False
    assert approval['P9_full_original_file_count']==141 and approval['P9_directory_metadata_count']==4
    assert approval['fresh_restore_destination_must_be_ABSENT'] is True
    assert approval['other24_source_originals']=='SOURCE_KEEP'
    assert approval['C16_scope_and_IO_and_source_retention']=='UNCHANGED_NO_NEW_AUTHORITY'
    return True

def require_tls_restore_location(wid):
    if int(wid.rsplit('B',1)[1])<10:return
    adoption=get('TLS_V10_TARGET_SAME_COMMIT_LOCATION_ADOPTION_V1.json')
    canonical=adoption['canonical_approval_commit']
    prefix='docs/ep_l2/operations/storage_one_shot_20261019/'
    for name,pin in adoption['canonical_raw_files'].items():
        raw=git('show',canonical+':'+prefix+name)
        assert hashlib.sha256(raw).hexdigest()==pin
        assert raw==(BASE/('CANONICAL_9f1a21a9_'+name)).read_bytes()
    approval=get('CANONICAL_9f1a21a9_TLS_NATIVE_RESTORE_LOCATION_USER_AMENDMENT_20261019.json')
    source_commit=adoption['source_same_commit_adoption_git_commit']
    name='TLS_V10_USER_NATIVE_RESTORE_AMENDMENT_20261019_SOURCE_NOTICE.json'
    bare='D:/repo/storage-ops-174new-164-exec-v1/.git/source-evidence.git'
    source=['git','--git-dir='+bare]
    subprocess.run(source+['merge-base','--is-ancestor',source_commit,'origin/hrl/ops-174-tls-v10-source-exec-v1'],check=True,capture_output=True)
    raw=subprocess.check_output(source+['show',source_commit+':docs/ep_l2/operations/tls_v10_174_to_164_source/'+name])
    assert hashlib.sha256(raw).hexdigest()==adoption['source_same_commit_notice_sha256']
    assert raw==(BASE/adoption['source_same_commit_notice_name']).read_bytes()
    validate_tls_restore_location(adoption,approval,json.loads(raw))
