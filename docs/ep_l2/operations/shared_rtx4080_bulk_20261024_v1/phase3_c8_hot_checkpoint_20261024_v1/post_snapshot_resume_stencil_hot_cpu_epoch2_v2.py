"""Parent-approved closed GPU capture adoption. No CUDA process or new GPU capture."""
import argparse, pathlib, json, hashlib, os, time, fcntl, subprocess, shutil, signal, traceback, collections, re
C=pathlib.Path('/root/data/shared_rtx4080_trace_library_20261024_v1/control')
B=pathlib.Path('/root/share/mnt164/huangrulin/traces/rtx4080_sm89/bulk_20261024_v1')
OLD='ORD_LATE_stencil_c3e987b033b4_A001';NEW='ORD_LATE_stencil_c3e987b033b4_A002_CPU_ADOPT_V2'
SOURCE=B/'inflight'/OLD;ROOT=B/'inflight'/NEW;DEPS=C/'stencil_adoption_dependencies_109_v1'
VALID=C/'validate_app_hot_resume_v4r3.py';POST=C/'post_app_parallel_v2.py'
VHASH='85ff5d68408632a4f15634bfa6a6d7a504429821ed8067f1ab8f39ce1b9a6909'
PHASH='0ec04d6a49fa757d90f436b63de8e4904110605ddcd3977d909238310df5db10'
P55='55c6f4829e8c92e11e0ab54496bf8f507f6cfa3a10cd01a857c6de147ee68b73'
def sha(p,rate=15):
    h=hashlib.sha256()
    with p.open('rb')as f:
        for b in iter(lambda:f.read(2**20),b''):
            start=time.monotonic();h.update(b)
            if rate:time.sleep(max(0,len(b)/(rate*2**20)-(time.monotonic()-start)))
    return h.hexdigest()
def save(p,o):
    with p.open('x')as f:json.dump(o,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
def replace(p,o):
    t=p.with_suffix('.tmp');t.write_text(json.dumps(o,indent=2)+'\n');os.replace(t,p)
def copy(s,d):
    d.parent.mkdir(parents=True,exist_ok=True)
    with s.open('rb')as inp,d.open('xb')as out:
        for b in iter(lambda:inp.read(2**20),b''):
            start=time.monotonic();out.write(b);time.sleep(max(0,len(b)/(15*2**20)-(time.monotonic()-start)))
        out.flush();os.fsync(out.fileno())
    assert sha(s)==sha(d)
def ticks(pid):return pathlib.Path('/proc',str(pid),'stat').read_text().split(') ',1)[1].split()[19]
def phase(name,**kw):replace(C/(NEW+'_HOT_EPOCH2_STATE.json'),dict(status=name,pid=os.getpid(),start_ticks=ticks(os.getpid()),unix=time.time(),**kw))
class Lease:
    def __enter__(self):
        self.f=[];deadline=time.time()+7200
        for name in ['RTX4080_SOURCE.lock','RTX4080_TARGET.lock']:
            f=open(C/name,'a');self.f.append(f)
            while True:
                try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);break
                except BlockingIOError:assert time.time()<deadline;time.sleep(2)
        return self
    def __exit__(self,*a):
        for f in reversed(self.f):fcntl.flock(f,fcntl.LOCK_UN);f.close()
def run(cmd,log,timeout):
    with log.open('x')as f:p=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,timeout=timeout)
    assert p.returncode==0,(cmd,p.returncode)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--approval',required=True);a=ap.parse_args();approval=pathlib.Path(a.approval);grant=json.loads(approval.read_text())
    assert grant['status']=='APPROVED_STENCIL_CPU_HOT_RESUME_NO_GPU'and grant['controller_sha256']==sha(pathlib.Path(__file__))
    assert sha(VALID)==VHASH and sha(POST)==PHASH
    frozen=C/'STENCIL_CLOSED_RAW_ADOPTION_SOURCE_V1.json';assert sha(frozen)==grant['raw_source_manifest_sha256'];source=json.loads(frozen.read_text())
    cache=C/'STENCIL_TERMINAL_CACHE_FOR_HOT_V4_V1.json';assert sha(cache)==grant['terminal_cache_sha256'];terminal=json.loads(cache.read_text());assert len(terminal['kernels'])==34 and terminal['old_exit_not_separately_recorded']
    policy=C/'STENCIL_HOT_RESOURCE_POLICY_V1.json';assert sha(policy)==grant['resource_policy_sha256'];resource_policy=json.loads(policy.read_text());assert resource_policy['effective_free_floor_bytes']==9*2**30
    assert shutil.disk_usage(C).free>resource_policy['effective_free_floor_bytes']+4*2**30
    state=json.loads((C/(NEW+'_STATE.json')).read_text());assert state['status']=='VALIDATE_ALL_RECORDS_READ_ONLY_NO_RTX_WRITER_LEASE'
    snapshot=C/'STENCIL_VALIDATOR_HOT_RESUME_PROCESS_V1.json';assert sha(snapshot)==grant['old_process_snapshot_sha256'];processes=json.loads(snapshot.read_text())['rows']
    wrapper=next(x for x in processes if 'validate_app_parallel_v2.py' in x['cmdline']);oldadopter=next(x for x in processes if 'adopt_stencil_cpu_v3.py' in x['cmdline'])
    assert wrapper['pid']==1004445 and wrapper['start_ticks']=='960079787'and ticks(wrapper['pid'])==wrapper['start_ticks']and ticks(oldadopter['pid'])==oldadopter['start_ticks']
    assert 'ORD_LATE_stencil_c3e987b033b4_A002_CPU_ADOPT_V2_validation_work'in wrapper['cmdline']
    import importlib.util
    spec=importlib.util.spec_from_file_location('hot',VALID);hot=importlib.util.module_from_spec(spec);spec.loader.exec_module(hot)
    for old in [wrapper,oldadopter]:
        d=pathlib.Path('/proc',str(old['pid']));parts=(d/'stat').read_text().split(') ',1)[1].split()
        assert parts[19]==old['start_ticks']and int(parts[1])==old['ppid']and int(parts[2])==old['pgid']
        assert(d/'cmdline').read_bytes().replace(b'\0',b' ').decode()==old['cmdline'],'old CPU identity changed'
    authority=C/'read_native_foreign_reserve_v1.py';assert sha(authority)=='441fec1917c436781cc0aa6e7e0b35f7a9aa0dc019b2fe96540fca27c78a29ba'
    spec=importlib.util.spec_from_file_location('authority',authority);auth=importlib.util.module_from_spec(spec);spec.loader.exec_module(auth);foreign=auth.snapshot()
    assert foreign['registry_sha256']==grant['foreign_registry_sha256']and foreign['epoch_sha256']==grant['foreign_epoch_sha256']and foreign['epoch']==grant['foreign_epoch']==2
    assert foreign['sum_all_records_reserved_write_bytes']==grant['foreign_reserved_sum_bytes']<=2281701376
    save(C/(NEW+'_HOT_EPOCH2_FOREIGN_PRELAUNCH.json'),foreign)
    phase('STOP_ONLY_OLD_CPU_WRAPPER_AND_REGISTERED_HELPERS')
    try:
        os.kill(wrapper['pid'],signal.SIGSTOP)
        stop_deadline=time.monotonic()+10;observed_tids=None
        while True:
            d=pathlib.Path('/proc',str(wrapper['pid']))
            if not d.exists():raise RuntimeError('old wrapper exited before stopped barrier; do not adopt concurrently with later old phases')
            observed_tids={int(t.name):(t/'stat').read_text().split(') ',1)[1].split()[0]for t in(d/'task').iterdir()}
            if observed_tids and all(v in('T','t')for v in observed_tids.values()):break
            assert time.monotonic()<stop_deadline,'old wrapper allTID stop barrier timed out'
            time.sleep(.05)
        save(C/(NEW+'_HOT_EPOCH2_STOP_ALL_TID_BARRIER.json'),{'wrapper_pid':wrapper['pid'],'start_ticks':wrapper['start_ticks'],'states':observed_tids,'all_stopped':True})
        stopped=hot.descendants(wrapper['pid']);save(C/(NEW+'_HOT_EPOCH2_STOP_SNAPSHOT.json'),{'wrapper':wrapper,'descendants_after_submission_stop':stopped,'GPU_signals':0})
        own=[]
        for p in stopped:
            if p['pid']==wrapper['pid']:continue
            cmd=pathlib.Path('/proc',str(p['pid']),'cmdline').read_bytes().replace(b'\0',b' ').decode()
            assert str(C.parent/(NEW+'_validation_work'))in cmd and 'delegated_validator_portable.py'in cmd
            assert p['pgid']!=wrapper['pgid'];own.append(p)
        for sig in [signal.SIGTERM,signal.SIGKILL]:
            for p in own:
                try:
                    now=hot.proc(p['pid'])
                    if now['ticks']==p['ticks']and now['pgid']==p['pgid']:os.killpg(p['pgid'],sig)
                except (ProcessLookupError,FileNotFoundError):pass
            time.sleep(3)
        # Queue TERM before CONT: the stopped wrapper cannot submit a later helper between them.
        os.kill(wrapper['pid'],signal.SIGTERM);os.kill(wrapper['pid'],signal.SIGCONT)
    finally:
        try:
            if ticks(wrapper['pid'])==wrapper['start_ticks']:os.kill(wrapper['pid'],signal.SIGCONT)
        except (FileNotFoundError,ProcessLookupError):pass
    deadline=time.time()+60
    while pathlib.Path('/proc',str(oldadopter['pid'])).exists()and ticks(oldadopter['pid'])==oldadopter['start_ticks']and pathlib.Path('/proc',str(oldadopter['pid']),'stat').read_text().split(') ',1)[1].split()[0]!='Z':
        assert time.time()<deadline;time.sleep(.5)
    assert (C/(NEW+'_FAILURE.json')).exists(),'old controller must close naturally with retained failed epoch'
    with(C/'RTX4080_QUEUE.lock').open('a')as f:
        fcntl.flock(f,fcntl.LOCK_EX);queue=json.loads((C/'QUEUE.json').read_text());q=next(x for x in queue if x['id']==NEW);assert q['status']=='FAILED_RETAINED';q.update(status='RUNNING_CPU_HOT_RESUME',old_CPU_epoch_failure_retained=str(C/(NEW+'_FAILURE.json')),controller_pid=os.getpid(),controller_start_ticks=ticks(os.getpid()),CPU_epoch=2);replace(C/'QUEUE.json',queue)
    receiver=C/'dispatch_bulk_v3.py';assert sha(receiver)=='e7a090d2baed8d0177cdf4af5132490023dad4ed60d35f46271db8f3c6f52025';namespace={};exec(compile(receiver.read_text().split("\nsingle=open(",1)[0],str(receiver),'exec'),namespace)
    phase('VALIDATE_HOT_WINDOW_16_CPU_ONLY_NO_WRITER_LEASE')
    validation=C/(NEW+'_FULL_RECORD_VALIDATION_HOT_EPOCH2.json');work=C.parent/(NEW+'_validation_hot_epoch2')
    run(['python3','-B',str(VALID),str(ROOT),str(ROOT/'map/manifest.json'),'--helper',str(C/'stencil_original_f9_validator.py'),'--parser',str(ROOT/'contract/validate_v7.py'),'--work',str(work),'--output',str(validation),'--raw-manifest',str(frozen),'--raw-manifest-sha256',sha(frozen),'--reuse-manifest',str(cache),'--reuse-manifest-sha256',sha(cache),'--max-workers','16','--free-floor',str(9*2**30),'--hot-limit',str(4*2**30),'--deadline','21600'],C/(NEW+'_HOT_EPOCH2_VALIDATION.log'),21700)
    completion=work/'CONTROLLER_COMPLETE.json';assert not(work/'FAILURE.json').exists()and json.loads(completion.read_text())['output_sha256']==sha(validation)
    val=json.loads(validation.read_text());assert val['kernels']==100 and val['counts']['sass_records']==source['reported_SASS_records_not_yet_validated']and val['reused_terminal_results_old_exit_not_separately_recorded']==34
    phase('WAIT_WRITER_LEASE_POST_PARALLEL2_UNCHANGED')
    with Lease():
        copy(validation,ROOT/'FULL_RECORD_VALIDATION.json')
        for p in [VALID,pathlib.Path(__file__),cache,policy,approval,completion,C/(NEW+'_FAILURE.json')]:copy(p,ROOT/'CPU_epoch2'/p.name)
        flags=json.loads((ROOT/'TRACER_CONTROLS_FROM_ORIGINAL_GPU_STDOUT.json').read_text())['actual_printed_control_variables']
    names=[k['name']for k in val['per_kernel']];all_grouped=[]
    for batch in range(0,len(names),2):
        selected=names[batch:batch+2];view=C.parent/(NEW+'_grouping_views')/('%03d'%batch);(view/'traces').mkdir(parents=True)
        members=[k for k in val['per_kernel']if k['name']in selected];batchcounts=collections.Counter()
        for k in members:batchcounts.update(k['counts'])
        sub=dict(val);sub.update(kernels=len(selected),ctas=sum(k['ctas']for k in members),warps=sum(k['warps']for k in members),counts=dict(batchcounts),per_kernel=members,source_files={p:h for p,h in val['source_files'].items()if pathlib.Path(p).name in selected},scope='INTERNAL_GROUPING_SCHEDULING_VIEW_NOT_AN_INDEPENDENT_APPLICATION_OR_CAPTURE',upstream_whole_application_validation_sha256=sha(validation))
        save(view/'FULL_RECORD_VALIDATION.json',sub)
        for n in selected:(view/'traces'/n).symlink_to(ROOT/'traces'/n)
        dest=ROOT/'post_batches'/('%03d'%batch);postout=C/(NEW+'_POST_BATCH_%03d.json'%batch)
        phase('PARALLEL2_POST_BATCH',completed_kernels=batch,total_kernels=100)
        with Lease():
            run(['python3','-B',str(POST),str(view),'--post',str(C/'postprocess_nas_sharded_v4.py'),'--dest-root',str(dest),'--output',str(postout)],C/(NEW+'_POST_BATCH_%03d.log'%batch),86400)
            q=json.loads(postout.read_text());assert q['kernels']==len(selected)
            for r in q['per_kernel']:
                p=pathlib.Path(r['grouped']);assert sha(p)==r['grouped_sha256'];p.rename(ROOT/'traces'/p.name)
                all_grouped.append(dict(r,original_closed_grouped_path=r['grouped'],grouped='traces/'+p.name,grouped_path_scope='ARCHIVE_RELATIVE_AFTER_CLOSED_MOVE'))
            copy(postout,ROOT/'post_batch_receipts'/postout.name)
            copy(view/'FULL_RECORD_VALIDATION.json',ROOT/'post_batch_receipts'/('%03d_INTERNAL_GROUPING_VIEW.json'%batch))
        # All subprocesses and XZ frames are closed before this safe transport-lease boundary.
    with Lease():
        expected={n.replace('.trace.xz','.traceg.xz')for n in names};assert {p.name for p in(ROOT/'traces').glob('*.traceg.xz')}==expected
        assert sum(r['records']for r in all_grouped)==val['counts']['sass_records']and len(all_grouped)==100
        for r in all_grouped:assert sha(ROOT/'traces'/pathlib.Path(r['grouped']).name)==r['grouped_sha256']
        save(ROOT/'POSTPROCESS_PARALLEL.json',{'status':'ALL_100_APP_KERNELS_CLOSED_GROUPED_SHA_PASS','upstream_whole_application_validation_sha256':sha(validation),'per_kernel':all_grouped,'writer_lease_release_between_complete_batches':True,'scheduling_views_are_not_independent_application_assets':True,'source_KEEP':True})
        lines=[l.replace('.trace.xz','.traceg.xz')if l.startswith('kernel-')else l for l in next((ROOT/'traces').glob('kernelslist_ctx_*')).read_text().splitlines()];(ROOT/'traces/kernelslist.g').write_text('\n'.join(lines)+'\n')
        task=json.loads((ROOT/'TASK.json').read_text());asset={'schema':'RTX4080_FULL_TRACE_ASSET_V1','kind':'FULL_APPLICATION_TRACE','asset_id':NEW,'suite':task['suite'],'source_version':task['version'],'program':task['program'],'variant':task['variant'],'argv':task['argv'],'input_identity':task.get('input_identity',task.get('input_files')),'binary_member':'bin/application','binary_sha256':source['GPU_execution']['binary_sha256'],'capture_gpu_uuid':source['GPU_execution']['actual_gpu_uuid'],'actual_cubin_arch':89,'producer_sha256':P55,'contract_sha256':sha(ROOT/'contract/CONTRACT.json'),'validator_sha256':VHASH,'delegated_validator_sha256':'f9f8a05ca7e0f8afe60e7d9a34f4884a9d1cb920b2212e41ed9a4faf19975af1','postprocessor_sha256':sha(C/'postprocess_nas_sharded_v4.py'),'parallel_post_scheduler_sha256':PHASH,'CPU_adoption_pipeline_sha256':sha(pathlib.Path(__file__)),'original_GPU_capture_job':OLD,'original_GPU_EXECUTION_sha256':next(x['sha256']for x in source['control_members']if x['path']=='EXECUTION.json'),'GPU_replayed':False,'full_application':{'kernel_launches':100,'ctas':val['ctas'],'warps':val['warps'],'records':val['counts']['sass_records'],'all_warps_terminate':True,'sampling':'NONE','commandlist':'traces/kernelslist.g'},'numerical_status':'ORIGINAL_CAPTURE_REFERENCE_CHECKER_REPORTED_PASS','numerical_reference_policy':'Preserved original same-capture checker/stdout; CPU adoption grants no stronger oracle','producer_semantic_qualification':'ADA7_ORDINARY_FULL_RECORD_PASS','consumer_qualification':'NOT_GRANTED','hardware_timing_calibration':'NOT_GRANTED','source_keep':True,'release_bytes':0}
        asset['tracer_control_flags']=flags
        asset['CPU_processing_epochs']={'old7657':{'failure_receipt_member':'CPU_epoch2/'+NEW+'_FAILURE.json','source_GPU_replayed':False},'epoch2_hot16':{'validator_sha256':VHASH,'closed_terminal_results_adopted':34,'old_per_kernel_exit_not_separately_recorded':True,'all_new_workers_and_final_observed_exit0_COMPLETE':True,'controller_COMPLETE_member':'CPU_epoch2/CONTROLLER_COMPLETE.json','aggregate_NAS_large_read_MiBps':15,'hot_window_bytes':4*2**30}}
        save(ROOT/'ASSET.json',asset);files=[{'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(ROOT.rglob('*'))if p.is_file()];save(ROOT/'SENDER_MANIFEST.json',{'asset':asset,'files':files})
        sender={'status':'SENDER_COMPLETE','asset_id':NEW,'inflight':str(ROOT.relative_to(B)),'sender_manifest_sha256':sha(ROOT/'SENDER_MANIFEST.json')};commit=namespace['publish'](sender);save(C/(NEW+'_COMMIT_READBACK.json'),commit)
        q=next(x for x in json.loads((C/'QUEUE.json').read_text())if x['id']==NEW);q.update(status='COMMITTED_VERIFIED',commit=commit,end_unix=time.time());namespace['update_job'](q)
    phase('COMMITTED_VERIFIED_NO_GPU_REPLAY',commit=commit)
if __name__=='__main__':
    try:main()
    except BaseException as e:
        fail={'status':'FAILED_RETAINED_CPU_EPOCH2','error':repr(e),'traceback':traceback.format_exc(),'source_KEEP':True,'GPU_replayed':False,'unix':time.time()};save(C/(NEW+'_HOT_EPOCH2_FAILURE.json'),fail);raise
