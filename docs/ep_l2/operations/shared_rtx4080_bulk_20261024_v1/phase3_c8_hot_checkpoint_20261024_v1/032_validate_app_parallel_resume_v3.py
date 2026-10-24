"""Closed-raw ordinary55 validation, bounded parallelism over complete kernels."""
import argparse, collections, concurrent.futures, csv, hashlib, json, os
import pathlib, re, resource, shutil, signal, subprocess, threading, time

F9='f9f8a05ca7e0f8afe60e7d9a34f4884a9d1cb920b2212e41ed9a4faf19975af1'
F4='f4a811c779e9b106c0977af45634d1b7dc01025c9e9b2805b74de6c6c82b879b'
P55='55c6f4829e8c92e11e0ab54496bf8f507f6cfa3a10cd01a857c6de147ee68b73'
def sha(p):
    h=hashlib.sha256()
    with p.open('rb')as f:
        for b in iter(lambda:f.read(2**20),b''):h.update(b)
    return h.hexdigest()
def dump(p,o):
    with p.open('x')as f:json.dump(o,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
def final_snapshot(root,raw,declared,fingerprints,ctxname,statsname,source_control):
    for p,digest in source_control.items():assert sha(pathlib.Path(p))==digest,'whole application metadata changed'
    assert {p.name for p in(root/'traces').glob('kernel*.trace.xz')}==set(declared),'raw set changed after delegate completion'
    assert {p.name for p in(root/'traces').glob('kernelslist_ctx_*')}=={ctxname}
    assert {p.name for p in(root/'traces').glob('stats_ctx_*')}=={statsname}
    for name in declared:
        p=raw[name];st=p.stat();assert(st.st_size,st.st_mtime_ns,sha(p))==fingerprints[name],'raw changed after an early delegate completed'
def main():
    ap=argparse.ArgumentParser();ap.add_argument('root');ap.add_argument('map');ap.add_argument('--helper',required=True);ap.add_argument('--parser',required=True);ap.add_argument('--work',required=True);ap.add_argument('--output',required=True);ap.add_argument('--max-workers',type=int,default=2);ap.add_argument('--reuse-manifest');ap.add_argument('--reuse-manifest-sha256');a=ap.parse_args()
    root=pathlib.Path(a.root).resolve();mapfile=pathlib.Path(a.map).resolve();work=pathlib.Path(a.work).resolve();out=pathlib.Path(a.output);helper=pathlib.Path(a.helper);parser=pathlib.Path(a.parser)
    assert a.max_workers in (1,2,8,16),'Explicit bounded concurrency candidates'
    assert sha(helper)==F9 and sha(parser)==F4,'Frozen delegated validator/parser identity'
    nice=pathlib.Path('/usr/bin/nice');prlimit=pathlib.Path('/usr/bin/prlimit')
    assert sha(nice)=='6e3fd69addd6cff40185a406577b80ca03072588d593387a6a6ef73e9bc36348'
    assert sha(prlimit)=='a63d6a3b741b085776716c55a23f763280b509095faf43e5d435af7191b5e3e7'
    assert not work.exists() and not out.exists();work.mkdir(parents=True)
    execution=json.loads((root/'EXECUTION.json').read_text());m=json.loads(mapfile.read_text())
    assert execution['exit_code']==0 and execution['binary_sha256']==m['binary_sha256'] and execution['tool_sha256']==P55
    ctx=list((root/'traces').glob('kernelslist_ctx_*'));assert len(ctx)==1
    declared=[]
    for line in ctx[0].read_text().splitlines():
        name=line.strip()
        if not name or name.startswith('Memcpy'):continue
        assert pathlib.PurePosixPath(name).name==name and name.startswith('kernel-') and name.endswith('.trace.xz')
        declared.append(name)
    assert declared and len(declared)==len(set(declared)),'zero/duplicate declared kernel'
    raw={p.name:p for p in (root/'traces').glob('kernel*.trace.xz')}
    assert set(raw)==set(declared),'whole application missing/extra raw'
    contexts={re.search(r'ctx_(0x[0-9a-fA-F]+)',n).group(1)for n in declared};assert len(contexts)==1
    context=next(iter(contexts));assert ctx[0].name=='kernelslist_ctx_'+context
    stats=list((root/'traces').glob('stats_ctx_*'));assert len(stats)==1
    assert stats[0].name=='stats_ctx_'+context
    with stats[0].open()as f:rows=list(csv.reader(f))
    header=rows[0];statrows=[r for r in rows[1:]if r]
    named={r[0].strip():r for r in statrows}
    assert len(named)==len(statrows)==len(declared) and set(named)==set(declared),'whole application stats exact set'
    assert [r[0].strip()for r in statrows]==declared,'stats and commandlist launch order'
    fingerprints={n:(p.stat().st_size,p.stat().st_mtime_ns,sha(p))for n,p in raw.items()}
    source_control={str(p):sha(p)for p in [root/'EXECUTION.json',mapfile,ctx[0],stats[0]]}
    # Only the immutable helper's parser-location assignment is adapted. Algorithm bytes stay identical.
    original=helper.read_text();needle="H=pathlib.Path('/data/c16/ada_trace_semantics_20261024_v1/frozen/ada7_contract_v1/validate_v7.py')"
    assert original.count(needle)==1
    portable=work/'delegated_validator_portable.py';portable.write_text(original.replace(needle,'H=pathlib.Path('+repr(str(parser))+')'))
    cache={};reused=[]
    if a.reuse_manifest:
        cp=pathlib.Path(a.reuse_manifest);assert a.reuse_manifest_sha256 and sha(cp)==a.reuse_manifest_sha256
        cm=json.loads(cp.read_text())
        assert cm['schema']=='ADA7_EXACT_CLOSED_KERNEL_RECEIPT_CACHE_V1'
        assert cm['root']==str(root)and cm['source_control_files']==source_control
        assert cm['map_sha256']==sha(mapfile)and cm['delegated_original_validator_sha256']==F9 and cm['frozen_parser_sha256']==F4
        assert cm['delegated_portable_validator_sha256']==sha(portable)
        for row in cm['kernels']:
            name=row['name'];assert name in declared and name not in cache
            assert tuple(row['raw_fingerprint'])==fingerprints[name]
            for p,h in row['proof_files'].items():assert sha(pathlib.Path(p))==h,'cached proof mutated'
            q=json.loads(pathlib.Path(row['receipt']).read_text())
            assert q==json.loads(pathlib.Path(row['stdout']).read_text()),'receipt and completed stdout differ'
            assert q['status']=='ADA7_ORDINARY_FULL_RECORD_PASS'and q['kernels']==1 and q['all_declared_warps_terminate']
            assert q['kernel_commandlist_exact_set']and q['stats_record_counts_match']and q['capture_map_binary_binding']and q['strict_single_stream_ordinary']
            assert q['map_sha256']==sha(mapfile)and q['frozen_parser_sha256']==F4 and q['validator_sha256']==sha(portable)
            assert len(q['source_files'])==1 and next(iter(q['source_files'].values()))==fingerprints[name][2]
            assert len(q['per_kernel'])==1 and q['per_kernel'][0]['name']==name and q['counts']['sass_records']==int(named[name][-1])
            virtual=pathlib.Path(row['receipt']).parent
            assert (virtual/'EXECUTION.json').read_bytes()==(root/'EXECUTION.json').read_bytes()
            assert (virtual/'traces'/ctx[0].name).read_text()==name+'\n'
            with(virtual/'traces'/stats[0].name).open()as f:assert list(csv.reader(f))==[header,named[name]]
            assert (virtual/'traces'/name).resolve()==raw[name].resolve()
            cache[name]=q
    children={};lock=threading.Lock();stop=threading.Event();deadline=time.time()+86400;peaks={'concurrent_helper_processes':0}
    def run_one(name):
        assert not stop.is_set(),'cancelled before delegate spawn'
        if name in cache:
            with lock:reused.append(name)
            return name,cache[name]
        r=work/name.replace('.trace.xz','');(r/'traces').mkdir(parents=True)
        (r/'EXECUTION.json').write_bytes((root/'EXECUTION.json').read_bytes())
        (r/'traces'/ctx[0].name).write_text(name+'\n')
        (r/'traces'/name).symlink_to(raw[name])
        with(r/'traces'/stats[0].name).open('x',newline='')as f:csv.writer(f).writerows([header,named[name]])
        with(r/'stdout.log').open('x')as stdout,(r/'stderr.log').open('x')as stderr:
            with lock:
                assert not stop.is_set(),'cancelled before actual spawn'
                p=subprocess.Popen([str(nice),'-n','15',str(prlimit),'--as='+str(1536*2**20),'--','python3','-B',str(portable),str(r),str(mapfile)],stdout=stdout,stderr=stderr,start_new_session=True)
                children[p.pid]=p;peaks['concurrent_helper_processes']=max(peaks['concurrent_helper_processes'],len(children))
            rc=p.wait()
            with lock:children.pop(p.pid,None)
        assert rc==0,(name,rc,(r/'stderr.log').read_text()[-2000:])
        result=json.loads((r/'stdout.log').read_text());assert result['status']=='ADA7_ORDINARY_FULL_RECORD_PASS' and result['kernels']==1
        assert result['counts']['sass_records']==int(named[name][-1]),'original stats count'
        st=raw[name].stat();assert(st.st_size,st.st_mtime_ns,sha(raw[name]))==fingerprints[name],'raw changed during validation'
        return name,result
    pool=concurrent.futures.ThreadPoolExecutor(max_workers=a.max_workers);futures=[]
    try:
        futures=[pool.submit(run_one,n)for n in declared]
        while not all(f.done()for f in futures):
            assert time.time()<deadline,'finite wrapper deadline'
            assert shutil.disk_usage(work).free>5*2**30,'private control metadata free reserve'
            for f in futures:
                if f.done() and f.exception():raise f.exception()
            time.sleep(.5)
        values=dict(f.result()for f in futures)
    except BaseException as error:
        # Stop before executor shutdown; queued tasks cannot create later children under the same lock.
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
            dump(work/'UNRESOLVED_CHILDREN_FAILURE.json',{'status':'OWN_CHILDREN_PENDING_KERNEL_EXIT_NO_COMPLETE_RESULT','pids':unresolved,'error':repr(error),'source_KEEP':True})
            os._exit(70)
        raise
    finally:pool.shutdown(wait=True,cancel_futures=True)
    final_snapshot(root,raw,declared,fingerprints,ctx[0].name,stats[0].name,source_control)
    counts=collections.Counter();per=[];streams=set()
    for n in declared:
        q=values[n];counts.update(q['counts']);per+=q['per_kernel'];streams.update(q['stream_ids'])
    assert len(streams)==1,'whole app multiple streams'
    result={'schema':'ADA7_CLOSED_APP_PARALLEL_VALIDATION_RESUME_V3','status':'ADA7_ORDINARY_FULL_RECORD_PASS','kernels':len(declared),'ctas':sum(q['ctas']for q in values.values()),'warps':sum(q['warps']for q in values.values()),'counts':dict(counts),'per_kernel':per,'stream_ids':sorted(streams),'context_count':1,'all_declared_warps_terminate':True,'kernel_commandlist_exact_set':True,'stats_record_counts_match':True,'source_files':{str(raw[n]):fingerprints[n][2]for n in declared},'source_control_files':source_control,'map_sha256':sha(mapfile),'capture_map_binary_binding':True,'validator_sha256':sha(pathlib.Path(__file__)),'delegated_original_validator_sha256':F9,'delegated_portable_validator_sha256':sha(portable),'portable_change':'Only frozen parser absolute location; full helper semantics unmodified','frozen_parser_sha256':F4,'max_concurrent_helpers':a.max_workers,'reused_closed_kernel_names':reused,'reused_closed_kernel_count':len(reused),'reuse_manifest_sha256':a.reuse_manifest_sha256,'all_source_raws_rehashed_at_start_and_final':True,'peaks':peaks,'per_process_RLIMIT_AS_bytes':1536*2**20,'no_GPU_execution':True,'source_KEEP':True,'partial_virtual_views_are_not_separately_claimed_full_applications':True}
    dump(out,result);print(json.dumps(result))
if __name__=='__main__':main()
