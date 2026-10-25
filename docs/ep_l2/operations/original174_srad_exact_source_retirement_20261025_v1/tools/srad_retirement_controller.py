"""New174 controller for one finite exact SRAD source retirement."""
import fcntl,gzip,hashlib,json,os,pathlib,shlex,stat,subprocess,sys,time,traceback
P=pathlib.Path;T=P('/root/data/research_asset_verified_offload_20261024_v1');OUT=T/'control/srad_exact_retirement_v1';sys.path.insert(0,str(T/'tools'))
import retire_174new_build_duplicates as audit
N=P('/root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261024_verified_offload_reclaim_v1/control/srad_exact_source_retirement_v1')
BUNDLE=P('/root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261024_verified_offload_reclaim_v1/assets/TRACE_300274ed6041b087');BRIDGE=P('/root/share/host174_storage_recovery_bridge/20261016_storageops_02')
PROTECTED=['TRACE_90174dcf58988a5d','TRACE_2f6210166d43b19e'];MANIFEST_SHA='b8007329860a36de022edb70c2a29ea6570502c5f307d47a1d515f73796432b3';COMMIT_SHA='7937f45865f94b07a1634f48fe551ca312f6296d42386e3722f809f6fb4377ce'

def need(v,m):
    if not v:raise RuntimeError(m)
def blob(x):return (json.dumps(x,sort_keys=True,indent=2)+'\n').encode()
def pair(name,x):
    b=blob(x);audit.put(OUT/name,b);audit.put(N/name,b)
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def ssh_json(code,timeout=180):
    ssh=['ssh','-i','/root/.ssh/id_ed25519_old174','-o','IdentitiesOnly=yes','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile=/root/data/result_offload_pilot_20261023_v1/controls/OLD174_VERIFIED_KNOWN_HOSTS','-p','2233','root@10.208.130.174','nice -n 19 ionice -c 3 python3 -B -']
    r=subprocess.run(ssh,input=code.encode(),stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=timeout);need(r.returncode==0,r.stderr.decode(errors='replace')[-3000:]);return json.loads(r.stdout)
def protected_snapshot():
    code="""import pathlib,json,stat,hashlib\nP=pathlib.Path;T=P('/root/data/research_asset_verified_offload_20261024_v1');out={}\nfor aid in %r:\n m=json.loads((T/'manifests'/(aid+'.json')).read_bytes());root=P(m['source_root']);rows=[]\n for x in m['members']:\n  p=root/x['relative_path'];s=p.lstat();rows.append({'relative_path':x['relative_path'],'dev':s.st_dev,'inode':s.st_ino,'size':s.st_size,'mtime_ns':s.st_mtime_ns,'ctime_ns':s.st_ctime_ns,'uid':s.st_uid,'gid':s.st_gid,'mode':stat.S_IMODE(s.st_mode),'nlink':s.st_nlink})\n out[aid]={'source_root':str(root),'members':rows,'manifest_sha256':hashlib.sha256((T/'manifests'/(aid+'.json')).read_bytes()).hexdigest()}\nprint(json.dumps(out))\n"""%PROTECTED
    return ssh_json(code)
def main():
    audit.q.mount_check();need(not (OUT/'INTENT.json').exists() and not (N/'INTENT.json').exists(),'existing retirement transaction; inspect, do not replay')
    lock=(BRIDGE/'.TARGET_RECEIVER.lock').open('rb');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    pre=json.loads((OUT/'PRE_DELETE_AUDIT.json').read_bytes());need(pre['status']=='PASS' and not pre['current_readers'] and not pre['registered_or_scheduled_readers'],'pre-delete reader audit not PASS')
    source=json.loads((OUT/'SOURCE_FULL_SHA_REVERIFY.json').read_bytes());target=json.loads((OUT/'TARGET_FULL_SHA_REVERIFY.json').read_bytes());need(source['all_manifest_SHA_identity_match'] and target['all_manifest_SHA_identity_match'],'full SHA reverify missing')
    need(source['members']==target['members']==506 and source['traceg']==target['traceg']==502 and source['bytes']==target['bytes']==21565199284,'qualification scope changed')
    srows={x['relative_path']:x for x in source['rows']};trows={x['relative_path']:x for x in target['rows']};need(set(srows)==set(trows),'Source/true164 member sets differ')
    mraw=(BUNDLE/'SOURCE_MANIFEST.json').read_bytes();need(hashlib.sha256(mraw).hexdigest()==MANIFEST_SHA and sha(BUNDLE/'COMMIT.json')==COMMIT_SHA,'archive controls changed');m=json.loads(mraw)
    def source_identity(raw):
        return dict(dev=raw['dev'],inode=raw['ino'],size=raw['size'],allocated=raw['blocks']*512,mtime_ns=raw['mtime_ns'],ctime_ns=raw['ctime_ns'],uid=raw['uid'],gid=raw['gid'],mode=stat.S_IMODE(raw['mode']),nlink=raw['nlink'],type='file')
    files=[];controls=[]
    for row in m['members']:
        need(row['sha256']==srows[row['relative_path']]['sha256']==trows[row['relative_path']]['sha256'],'qualified SHA mismatch');dest=dict(row,identity=source_identity(srows[row['relative_path']]['identity']),archive_identity_raw=trows[row['relative_path']]['identity'])
        (files if row['relative_path'].endswith('.traceg') else controls).append(dest)
    need(len(files)==502 and {x['relative_path'] for x in controls}=={'commandlist','kernelslist','kernelslist.g','stats.csv'},'whitelist changed')
    for row in files+controls:
        p=BUNDLE/'tree'/row['relative_path'];need(p.is_file() and not p.is_symlink() and audit.q.identity(p)==row['archive_identity_raw'],'true164 identity changed '+str(p))
    restore=T/'tools/srad_restore_to_old174.py';worker=T/'tools/srad_source_unlink.py';need(restore.is_file() and worker.is_file(),'retirement or restore tool missing')
    before_protected=protected_snapshot();protected_bundle={aid:{'commit_sha256':sha(P('/root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261024_verified_offload_reclaim_v1/assets')/aid/'COMMIT.json'),'restore':str(P('/home/shared/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261024_verified_offload_reclaim_v1/assets')/aid/'RESTORE.sh')} for aid in PROTECTED}
    qualified=dict(schema='ORIGINAL174_SRAD_EXACT_QUALIFIED_WHITELIST_V1',asset_id='TRACE_300274ed6041b087',files=files,controls=controls,logical_traceg_bytes=sum(x['size'] for x in files),allocated_traceg_bytes=sum(x['identity']['allocated'] for x in files),source_SHA_receipt_sha256=sha(OUT/'SOURCE_FULL_SHA_REVERIFY.json'),target_SHA_receipt_sha256=sha(OUT/'TARGET_FULL_SHA_REVERIFY.json'),restore_tool_sha256=sha(restore),source_worker_sha256=sha(worker),lavaMD_and_HybridSort_before=before_protected,protected_bundles=protected_bundle)
    pair('QUALIFIED_WHITELIST.json',qualified);audit.put(N/'SRAD_RESTORE_TO_OLD174.py',restore.read_bytes())
    for evidence in ('PRE_DELETE_AUDIT.json','SOURCE_FULL_SHA_REVERIFY.json','TARGET_FULL_SHA_REVERIFY.json','SCRIPT_QUALIFICATION.json'):
        audit.put(N/evidence,(OUT/evidence).read_bytes())
    intent=dict(schema='ORIGINAL174_SRAD_EXACT_RETIREMENT_INTENT_V1',unix=time.time(),asset_id='TRACE_300274ed6041b087',source_root=m['source_root'],files=502,logical_bytes=qualified['logical_traceg_bytes'],allocated_bytes=qualified['allocated_traceg_bytes'],whitelist_sha256=sha(OUT/'QUALIFIED_WHITELIST.json'),archive_manifest_sha256=MANIFEST_SHA,archive_commit_sha256=COMMIT_SHA,controls=[{'relative_path':x['relative_path'],'sha256':x['sha256'],'identity':x['identity']} for x in controls],restore_entry=str(N/'SRAD_RESTORE_TO_OLD174.py'),full_native_restore_21GB_performed=False,lavaMD_and_HybridSort_deletion_authorized=False,recursive_delete_authorized=False,science_or_controller_changes=0,user_authorization='ORIGINAL174_SRAD_EXACT_SOURCE_RETIREMENT_V1')
    pair('INTENT.json',intent)
    smallest=min(files,key=lambda x:(x['size'],x['relative_path']));test=(BUNDLE/'tree'/smallest['relative_path']).read_bytes();need(len(test)==smallest['size'] and hashlib.sha256(test).hexdigest()==smallest['sha256'],'test recovery payload mismatch')
    ssh=['ssh','-i','/root/.ssh/id_ed25519_old174','-o','IdentitiesOnly=yes','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile=/root/data/result_offload_pilot_20261023_v1/controls/OLD174_VERIFIED_KNOWN_HOSTS','-p','2233','root@10.208.130.174','nice -n 19 ionice -c 3 python3 -B '+shlex.quote(str(worker))]
    run=subprocess.run(ssh,input=test,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=7200);log=dict(returncode=run.returncode,stdout=run.stdout.decode(errors='replace'),stderr=run.stderr.decode(errors='replace'),unix=time.time());pair('SOURCE_WORKER_LOG.json',log)
    if run.returncode:
        status='HOLD_TEST_SOURCE_RESTORED' if (OUT/'TEST_RECLAIM_FAILED_AND_SOURCE_RESTORED.json').exists() else 'HOLD_PARTIAL_TRANSACTION_REVIEW_REQUIRED';hold=dict(schema='ORIGINAL174_SRAD_EXACT_RETIREMENT_HOLD_V1',status=status,unix=time.time(),worker_returncode=run.returncode,worker_stderr=log['stderr'][-3000:]);pair('HOLD.json',hold);raise RuntimeError(status)
    done=json.loads((OUT/'DONE.json').read_bytes());need(done['status']=='DONE' and done['files']==502,'Source DONE changed')
    after_protected=protected_snapshot();need(before_protected==after_protected,'lavaMD or HybridSort Source identity changed')
    for aid,row in protected_bundle.items():need(sha(P(row['restore'].replace('/home/shared','/root/share/mnt164',1)).parent/'COMMIT.json')==row['commit_sha256'],'protected archive changed')
    records=[]
    for i in range(502):records.append({'INTENT':json.loads((OUT/'per_file'/('%06d.INTENT.json'%i)).read_bytes()),'DONE':json.loads((OUT/'per_file'/('%06d.DONE.json'%i)).read_bytes())})
    journal=b''.join((json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode() for x in records);compressed=gzip.compress(journal,compresslevel=9,mtime=0);audit.put(N/'PER_FILE_INTENT_DONE.jsonl.gz',compressed)
    final=dict(done,qualified_whitelist_sha256=sha(OUT/'QUALIFIED_WHITELIST.json'),per_file_journal_uncompressed_sha256=hashlib.sha256(journal).hexdigest(),per_file_journal_gzip_sha256=hashlib.sha256(compressed).hexdigest(),per_file_transactions=502,true164_archive_unchanged=True,lavaMD_and_HybridSort_before=before_protected,lavaMD_and_HybridSort_after=after_protected,lavaMD_and_HybridSort_completely_unchanged=True,restore_entry=str(N/'SRAD_RESTORE_TO_OLD174.py'))
    pair('DONE_CONTROLLER.json',final);print(json.dumps(final),flush=True)
if __name__=='__main__':
    try:main()
    except BaseException as e:
        p=N/('CONTROLLER_FAILURE_%d.json'%time.time_ns());audit.put(p,audit.blob({'error':repr(e),'traceback':traceback.format_exc(),'unix':time.time(),'no_blind_retry':True}));raise
