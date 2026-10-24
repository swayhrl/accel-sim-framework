"""Bounded kernel scheduler around the immutable, qualified V4 grouping algorithm."""
import argparse, concurrent.futures, hashlib, json, os, pathlib, shutil
import signal, subprocess, threading, time
POST_SHA='5d3ffcd3cf000e1f72e2adf97b4185217a51e1fe0c147c5c39500130e418e66d'
def sha(p):
    h=hashlib.sha256()
    with p.open('rb')as f:
        for b in iter(lambda:f.read(2**20),b''):h.update(b)
    return h.hexdigest()
def save(p,o):
    with p.open('x')as f:json.dump(o,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
def final_groups(dest,names,results):
    expected={n.replace('.trace.xz','.traceg.xz')for n in names}
    assert {p.name for p in dest.glob('*.traceg.xz')}==expected,'final grouped exact set changed'
    for n in names:
        r=results[n];p=dest/n.replace('.trace.xz','.traceg.xz')
        assert sha(p)==r['grouped_sha256'],'early grouped content changed'
        assert json.loads((dest/(n+'.POST_CLOSED_RECEIPT.json')).read_text())==r,'closed receipt changed'
def tree_size_race_safe(root):
    total=0
    def onerror(error):
        if not isinstance(error,FileNotFoundError):raise error
    for parent,dirs,files in os.walk(root,followlinks=False,onerror=onerror):
        for name in files:
            p=pathlib.Path(parent)/name
            try:
                if p.is_file():total+=p.stat().st_size
            except FileNotFoundError:pass
    return total
def main():
    ap=argparse.ArgumentParser();ap.add_argument('root');ap.add_argument('--post',required=True);ap.add_argument('--dest-root',required=True);ap.add_argument('--output',required=True);ap.add_argument('--deadline-sec',type=int,default=86400);ap.add_argument('--max-workers',type=int,default=2);ap.add_argument('--minimum-free',type=int,default=20*2**30);ap.add_argument('--aggregate-spill-budget',type=int,default=128*2**30);ap.add_argument('--per-shard-scratch-budget',type=int,default=64*2**30);a=ap.parse_args();assert a.max_workers in (2,4,8)
    root=pathlib.Path(a.root).resolve();post=pathlib.Path(a.post).resolve();dest=pathlib.Path(a.dest_root).resolve();output=pathlib.Path(a.output)
    nice=pathlib.Path('/usr/bin/nice');prlimit=pathlib.Path('/usr/bin/prlimit')
    assert sha(post)==POST_SHA
    assert sha(nice)=='6e3fd69addd6cff40185a406577b80ca03072588d593387a6a6ef73e9bc36348'
    assert sha(prlimit)=='a63d6a3b741b085776716c55a23f763280b509095faf43e5d435af7191b5e3e7'
    assert not dest.exists()and not output.exists();dest.mkdir(parents=True)
    proof=root/'FULL_RECORD_VALIDATION.json';v=json.loads(proof.read_text());assert v['status']=='ADA7_ORDINARY_FULL_RECORD_PASS'and v['all_declared_warps_terminate']and v['kernel_commandlist_exact_set']and v['stats_record_counts_match']
    names=[r['name']for r in v['per_kernel']];assert len(names)==len(set(names))==v['kernels']and names
    raw={p.name:p for p in(root/'traces').glob('kernel*.trace.xz')};assert set(raw)==set(names)
    declared={pathlib.Path(p).name:digest for p,digest in v['source_files'].items()};assert set(declared)==set(names)
    for name in names:assert sha(raw[name])==declared[name]
    before={n:(p.stat().st_size,p.stat().st_mtime_ns,declared[n])for n,p in raw.items()};proofsha=sha(proof)
    children={};lock=threading.Lock();stop=threading.Event();deadline=time.time()+a.deadline_sec;peak_processes=0;peak_spill=0;peak_RSS=0
    def one(name):
        nonlocal peak_processes
        source=raw[name];out=dest/source.name.replace('.trace.xz','.traceg.xz');work=dest/(source.stem+'_work')
        with(dest/(name+'.stdout.log')).open('x')as stdout,(dest/(name+'.stderr.log')).open('x')as stderr:
            with lock:
                assert not stop.is_set(),'stopped before child spawn'
                p=subprocess.Popen([str(nice),'-n','15',str(prlimit),'--as='+str(1536*2**20),'--','python3','-B',str(post),str(source),str(out),str(work),'--scratch-budget',str(a.per_shard_scratch_budget)],stdout=stdout,stderr=stderr,start_new_session=True)
                children[p.pid]=p;peak_processes=max(peak_processes,len(children))
            rc=p.wait()
            with lock:children.pop(p.pid,None)
        assert rc==0,(name,rc,(dest/(name+'.stderr.log')).read_text()[-2000:])
        result=json.loads((dest/(name+'.stdout.log')).read_text());assert result['status']=='GROUPED_ALL_SHARDS_CRC_PASS'and result['source_sha256']==declared[name]
        original=next(r for r in v['per_kernel']if r['name']==name)
        assert result['records']==original['counts']['sass_records']and result['ctas']==original['ctas']and result['warps']==original['warps']
        assert result['grouped_sha256']==sha(out)
        st=source.stat();assert(st.st_size,st.st_mtime_ns,sha(source))==before[name]
        save(dest/(name+'.POST_CLOSED_RECEIPT.json'),result);shutil.rmtree(work)
        return name,result
    pool=concurrent.futures.ThreadPoolExecutor(max_workers=a.max_workers);futures=[]
    try:
        futures=[pool.submit(one,n)for n in names]
        while not all(f.done()for f in futures):
            for f in futures:
                if f.done()and f.exception():raise f.exception()
            used=tree_size_race_safe(dest);peak_spill=max(peak_spill,used)
            assert used<a.aggregate_spill_budget,'polled global output/scratch threshold'
            assert shutil.disk_usage(dest).free>a.minimum_free,'physical free reserve'
            assert time.time()<deadline,'whole scheduler finite deadline'
            time.sleep(1)
        results=dict(f.result()for f in futures)
    except BaseException as error:
        with lock:
            stop.set()
            for p in children.values():
                if p.poll()is None:
                    try:os.killpg(p.pid,signal.SIGTERM)
                    except ProcessLookupError:pass
        for f in futures:f.cancel()
        unresolved=[]
        for p in list(children.values()):
            try:p.wait(timeout=3)
            except subprocess.TimeoutExpired:
                try:os.killpg(p.pid,signal.SIGKILL)
                except ProcessLookupError:pass
                try:p.wait(timeout=3)
                except subprocess.TimeoutExpired:unresolved.append(p.pid)
        if unresolved:
            save(dest/'UNRESOLVED_CHILDREN_FAILURE.json',{'status':'OWN_CHILDREN_PENDING_KERNEL_EXIT_NO_COMPLETE_RESULT','pids':unresolved,'error':repr(error),'source_KEEP':True});os._exit(70)
        raise
    finally:pool.shutdown(wait=True,cancel_futures=True)
    assert sha(proof)==proofsha and {p.name for p in(root/'traces').glob('kernel*.trace.xz')}==set(names)
    for n,p in raw.items():
        st=p.stat();assert(st.st_size,st.st_mtime_ns,sha(p))==before[n]
    final_groups(dest,names,results)
    assert sha(post)==POST_SHA
    assert sha(nice)=='6e3fd69addd6cff40185a406577b80ca03072588d593387a6a6ef73e9bc36348'
    assert sha(prlimit)=='a63d6a3b741b085776716c55a23f763280b509095faf43e5d435af7191b5e3e7'
    result={'status':'WHOLE_APP_PARALLEL_BOUNDED_V4_GROUPING_CLOSED_PASS','source_validation_sha256':proofsha,'source_files':{n:declared[n]for n in names},'per_kernel':[results[n]for n in names],'kernels':len(names),'records':sum(r['records']for r in results.values()),'postprocessor_sha256':POST_SHA,'scheduler_sha256':sha(pathlib.Path(__file__)),'resource_scan_scope':'os.walk ignores onlyENOENT directory/file deletion races; allother errors raise','nice_sha256':sha(nice),'prlimit_sha256':sha(prlimit),'max_concurrent_kernel_postprocessors':a.max_workers,'peak_concurrent_postprocess_Python':peak_processes,'peak_polled_spill_bytes':peak_spill,'aggregate_scratch_polled_limit_bytes':a.aggregate_spill_budget,'per_shard_expanded_x3_budget_bytes':a.per_shard_scratch_budget,'external_recursive_whole_phase_guard_required':True,'scratch_is_not_filesystem_quota':True,'per_process_RLIMIT_AS_bytes':1536*2**20,'memory_scope':'Each Python and inherited sort process has separate limit; no false2-process aggregate RAM claim','no_GPU_execution':True,'source_KEEP':True,'caller_must_own_RTX_writer_lease_for_NAS_outputs':True}
    save(output,result);print(json.dumps(result))
if __name__=='__main__':main()
