"""Draft CPU-only qualifier. Requires independently bound, published X2 identity and diff review.

Never invokes the trace executable, kernel list, simulator main or a full-attempt UUID.
Unexecuted while X2 is unavailable. Publication of a PASS and actual runner release
are separate manual campaign steps; this program cannot start the matrix.
"""
from common import *
from event_snapshots import snapshot as event_snapshot,fixture_snapshots,QualificationError
import argparse

def publics(text,label,side):
    m=re.search(r'^AA5_PUBLIC_'+side+' label='+re.escape(label)+r'\nY2_COUNTERS (\{[^\n]+\})\s*$',text,re.M)
    assert m,(label,side)
    return json.loads(m[1])

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--binding',required=True);ap.add_argument('--run-label',required=True);args=ap.parse_args()
    assert re.fullmatch(r'[A-Za-z0-9_-]+',args.run_label)
    b=json.loads(Path(args.binding).read_text())
    assert b['status']=='AA5_INDEPENDENT_BINDING_OF_PUBLISHED_X2'
    new=b['Core_commit'];assert re.fullmatch('[0-9a-f]{40}',new) and new!=CANDIDATE_CORE
    assert git(CORE_REPO,'rev-parse','refs/aa5-bindings/X2_Core')==new
    assert git(FW_REPO,'rev-parse','refs/aa5-bindings/X2_Framework')==b['producer_Framework_commit']
    review=PACK/'X2_INDEPENDENT_DIFF_REVIEW.json';assert sha(review)==b['AA5_diff_review_sha256']
    dr=json.loads(review.read_text());assert dr['status']=='PASS_ONLY_PRINT_REACHABILITY_AND_TESTS' and dr['Core_new']==new and dr['Core_old']==CANDIDATE_CORE
    assert sha(b['libcudart_path'])==b['libcudart_sha256'] and sha(b['trace_executable_path'])==b['trace_executable_sha256']
    # Producer identity must itself be exact bytes in an immutable published Framework commit.
    source=b['producer_identity_document'];assert hashlib.sha256(blob(FW_REPO,b['producer_Framework_commit'],source['path'])).hexdigest()==source['sha256']
    run=ROOT/'normal-export-cpu'/args.run_label;run.mkdir(parents=True,exist_ok=False)
    src=run/'Core-source';src.mkdir();archive=run/'Core-headers.tar'
    archive.write_bytes(subprocess.check_output(['git','-C',str(CORE_REPO),'archive',new,'src','libcuda']))
    subprocess.run(['/usr/bin/tar','-xf',str(archive),'-C',str(src)],check=True)
    lib=Path(b['libcudart_path']).resolve();probe=run/'normal_export_fixture'
    command=['/usr/bin/g++','-std=c++17','-fno-access-control','-UNDEBUG','-DY2_HAS_K1=1','-DCUDART_VERSION=11080','-I'+str(src/'src'),'-I'+str(src/'libcuda'),'-I/usr/local/cuda-11.8/include',str(PACK/'scripts/normal_export_fixture.cc'),'-L'+str(lib.parent),'-Wl,-rpath,'+str(lib.parent),'-lcudart','-ldl','-o',str(probe)]
    env={'PATH':'/usr/bin:/bin','LANG':'C','LD_LIBRARY_PATH':str(lib.parent)}
    receipts=[]
    def call(argv,label):
        r=subprocess.run(argv,cwd=run,env=env,capture_output=True,text=True,timeout=180)
        for key in ['stdout','stderr']:(run/(label+'.'+key)).write_text(getattr(r,key))
        receipts.append(dict(label=label,argv=argv,returncode=r.returncode,stdout_sha256=sha(run/(label+'.stdout')),stderr_sha256=sha(run/(label+'.stderr'))))
        assert r.returncode==0,(label,r.returncode,r.stderr[-2000:]);return r.stdout
    call(command,'compile')
    ldd=call(['/usr/bin/ldd',str(probe)],'ldd');assert str(lib) in ldd and 'not found' not in ldd
    first=snapshot();time.sleep(10.1);second=snapshot();assert all(resource_checks(first,second).values())
    write(run/'CPU_RESOURCE_PROBE.json',dict(first=first,second=second))
    cases={}
    for name,K,flags in [('omitted',0,[]),('off',0,[K_OPTION,'0']),('on',1,[K_OPTION,'1'])]:
        text=call([str(probe),str(PACK/'inputs/CPU_EXPORT_FIXTURE_BASE.config'),*flags],name)
        loaded=re.findall(r'^Y2_LIBRARY (.+)$',text,re.M);assert len(loaded)==1 and Path(loaded[0]).resolve()==lib
        assert sha(loaded[0])==b['libcudart_sha256']
        entries=re.findall(r'^AA5_NORMAL_ENTRY_LIBRARY (.+)$',text,re.M);assert len(entries)==4 and all(Path(q).resolve()==lib for q in entries)
        parsed=fixture_snapshots(text,K);snaps=parsed['snapshots'];assert [(s['label'],s['public_cycle']) for s in snaps]==[('initial0',0),('terminal40_a',40),('terminal40_b',40),('terminal43',43)]
        public={}
        for s in snaps:
            before=publics(text,s['label'],'BEFORE');after=publics(text,s['label'],'AFTER');assert before==after
            public[s['label']]=before
        assert public['terminal40_a']==public['terminal40_b']
        if K:
            assert all(s['per_SM'][sm]['requests']==0 for sm in range(64) for s in snaps[:1])
            for s in snaps[1:]:
                final=s['label']=='terminal43';m=s['per_SM'][0]
                expected=dict(requests=7 if final else 4,idle=5 if final else 2,membar=1,config=1,ordinary_commits=6 if final else 3,changed=2,retained_at_event=1,reclaimed_at_event=1,no_op_requests=5 if final else 2,unspecified=0,pending_first_request=0,pending_last_request=0,first_request_cycle=10,last_request_cycle=43 if final else 36,first_ordinary_commit_cycle=23,last_ordinary_commit_cycle=43 if final else 36,event_records_omitted=13 if final else 7)
                assert all(m[k]==v for k,v in expected.items()),(s['label'],m,expected)
                for sm in range(1,64):
                    r=s['per_SM'][sm];assert r['requests']==(4 if final else 1) and r['config']==1 and r['idle']==(3 if final else 0) and r['ordinary_commits']==(4 if final else 1) and r['changed']==r['retained_at_event']==r['reclaimed_at_event']==0
                    assert r['first_request_cycle']==r['first_ordinary_commit_cycle']==32 and r['last_request_cycle']==r['last_ordinary_commit_cycle']==(43 if final else 32)
                    assert r['no_op_requests']==r['requests'] and r['event_records_omitted']==r['requests']+r['ordinary_commits'] and r['pending_first_request']==r['pending_last_request']==0
            assert parsed['last_snapshot']['totals']['requests']==259
            assert parsed['last_snapshot']['reclaimed_at_event']==1
            assert sum(s['reclaimed_at_event'] for s in snaps)==3 # deliberate non-final total, forbidden as observation
        cases[name]=dict(K=K,parsed=parsed,public=public,loaded_library=str(lib),library_sha256=sha(lib),stdout_sha256=sha(run/(name+'.stdout')))
    assert cases['omitted']['public']==cases['off']['public']
    # Mutate actual production output for rejecting negatives; no private printer data.
    text=(run/'on.stdout').read_text();body=re.search(r'^AA5_EXPORT_SNAPSHOT_BEGIN label=terminal43 expected_cycle=43\n(.*?)^AA5_EXPORT_SNAPSHOT_END label=terminal43',text,re.S|re.M)[1]
    lines=re.findall(r'^DTC_INVALIDATE_V1_SUMMARY .*$',body,re.M);assert len(lines)==64
    negatives=[]
    def reject(name,value,wrapped=False):
        try:fixture_snapshots(value,1) if wrapped else event_snapshot(value,1,43)
        except (QualificationError,AssertionError) as e:negatives.append(dict(case=name,rejected=True,reason=str(e)));return
        raise AssertionError(name+' accepted invalid actual-output mutation')
    reject('missing_SM',body.replace(lines[-1]+'\n','',1));reject('duplicate_SM',body+lines[0]+'\n');reject('same_length_duplicate_SM',body.replace(lines[-1],lines[0],1));reject('truncated_field',body.replace('reclaimed_at_event=1 ','',1));reject('wrong_public_boundary',body.replace('gpu_tot_sim_cycle = 43','gpu_tot_sim_cycle = 44',1));reject('truncated_last_snapshot',text.rsplit('AA5_EXPORT_SNAPSHOT_END',1)[0],True)
    initial=re.search(r'^AA5_EXPORT_SNAPSHOT_BEGIN label=initial0 expected_cycle=0\n(.*?)^AA5_EXPORT_SNAPSHOT_END label=initial0',text,re.S|re.M)[1]
    malformed=initial.replace('first_request_cycle='+str((1<<64)-1),'first_request_cycle=0',1)
    try:event_snapshot(malformed,1,0)
    except QualificationError:negatives.append(dict(case='no_event_sentinel',rejected=True))
    else:raise AssertionError('malformed sentinel accepted')
    write(PACK/'normal_export_gate_receipts'/args.run_label/'NORMAL_TERMINAL_EXPORT_GATE.json',dict(status='PASS_NORMAL_TERMINAL_EXPORT_GATE',Core_commit=new,libcudart_sha256=b['libcudart_sha256'],fixture_source_sha256=sha(PACK/'scripts/normal_export_fixture.cc'),fixture_binary_sha256=sha(probe),decoder_sha256=sha(PACK/'scripts/event_snapshots.py'),binding_sha256=sha(args.binding),run_directory=str(run),cases=cases,negative_tests=negatives,receipts=receipts,entry='actual production gpu_print_stat -> shader_print_dtc_l1_stats; no observer private print call',unique_SM_per_K1_snapshot=64,public_counter_before_after_print_exact=True,K0_missing_fields='UNAVAILABLE_NOT_ZERO',last_snapshot_only=True,full_Gaussian_attempts=0,publication_and_full_executable_registration='STILL_REQUIRED_BEFORE_PERFORMANCE',limitations='CPU synthetic coalesced instructions/captured lower transport; bounded normal-export qualification, not full ISA/value/coherence/PPA proof'))
    print('PASS normal export qualification only; publish immutable receipt and complete pre-registration before any full simulator.')

if __name__=='__main__':main()
