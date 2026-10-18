"""Run existing CPU normal-export fixture with AD ON. No compilation/workload."""
import argparse,hashlib,json,os,re,subprocess
from pathlib import Path
PREFIX='DTC_PROGRESSIVE_WAKE_V1'
SUMMARY={'sm','broadcasts','first_notify_cycle_sum','last_notify_cycle_sum','span_sum',
         'own_dep0_linewide_blocked_entry_cycles','notified_frontend_ready_entries',
         'notified_frontend_ready_entry_cycles','late_merges'}
LDST={'sm','admitted_notified_collectable','admitted_returns_to_retire_sum','retired'}
def fields(line,expected):
    try:
        pairs=[part.split('=',1) for part in line.split()[1:]]
        result={k:int(v) for k,v in pairs}
    except (ValueError,TypeError):raise ValueError('invalid fields')
    if len(result)!=len(pairs) or set(result)!=expected or any(v<0 for v in result.values()):
        raise ValueError('missing/duplicate/unexpected/negative fields')
    return result

def parse(text):
    snapshots=[];frame=None
    for line in text.splitlines():
        if line.startswith(PREFIX+'_SNAPSHOT_BEGIN '):
            if frame is not None:raise ValueError('nested snapshot')
            h=fields(line,{'version','sms','cycle','no_event_cycle_sentinel'})
            if h['version']!=1 or h['sms']!=64 or h['no_event_cycle_sentinel']!=2**64-1:
                raise ValueError('bad frame header')
            frame=dict(header=h,summary={},fanout={},ldst={},line={})
        elif line.startswith(PREFIX+'_SNAPSHOT_END '):
            if frame is None or fields(line,{'version'})!={'version':1}:raise ValueError('bad frame end')
            if any(set(frame[key])!=set(range(64)) for key in ('summary','fanout','ldst')):
                raise ValueError('missing SM')
            for sm in range(64):
                if set(frame['fanout'][sm])!=set(range(33)):raise ValueError('missing fanout bin')
                if sum(frame['fanout'][sm].values())!=frame['summary'][sm]['broadcasts']:
                    raise ValueError('fanout/broadcast conservation')
                if frame['summary'][sm]['last_notify_cycle_sum']-frame['summary'][sm]['first_notify_cycle_sum']!=frame['summary'][sm]['span_sum']:
                    raise ValueError('first/last/span mismatch')
            snapshots.append(frame);frame=None
        elif line.startswith(PREFIX+' '):
            if frame is None:raise ValueError('unframed summary')
            row=fields(line,SUMMARY);sm=row['sm']
            if sm not in range(64) or sm in frame['summary']:raise ValueError('bad/duplicate SM')
            frame['summary'][sm]=row
        elif line.startswith(PREFIX+'_FANOUT '):
            if frame is None:raise ValueError('unframed histogram')
            row=fields(line,{'sm','bin','count'});sm=row['sm'];bin=row['bin']
            if sm not in range(64) or bin not in range(33):raise ValueError('bad histogram key')
            hist=frame['fanout'].setdefault(sm,{})
            if bin in hist:raise ValueError('duplicate histogram bin')
            hist[bin]=row['count']
        elif line.startswith(PREFIX+'_LDST '):
            if frame is None:raise ValueError('unframed LDST row')
            row=fields(line,LDST);sm=row['sm']
            if sm not in range(64) or sm in frame['ldst']:raise ValueError('bad/duplicate LDST SM')
            frame['ldst'][sm]=row
        elif line.startswith(PREFIX+'_LINE '):
            # The existing fixture reclaims its two rows before snapshots.
            # Never silently accept an unexamined nonempty row population.
            raise ValueError('unexpected live LINE row for this fixture')
        elif line.startswith(PREFIX):raise ValueError('unknown AD row')
    if frame is not None or len(snapshots)!=3:raise ValueError('truncated/missing snapshot')
    return snapshots

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser()
    for name in ('build','config','raw'):ap.add_argument('--'+name,required=True,type=Path)
    a=ap.parse_args();a.raw.mkdir(parents=True,exist_ok=False)
    cfg=a.raw/'progressive_on.config';cfg.write_text(a.config.read_text()+'\n-gpgpu_dtc_l1_progressive_wakeup 1\n')
    probe=a.build/'dtc_l1_normal_export_probe';lib=a.build/'libcudart.so'
    inputs={key:dict(path=str(p.resolve()),sha256=sha(p)) for key,p in [('probe',probe),('library',lib),('base_config',a.config),('ON_config',cfg)]}
    env=dict(os.environ);env.pop('LD_PRELOAD',None);env['LD_LIBRARY_PATH']=str(a.build.resolve());env['CUDA_VISIBLE_DEVICES']=''
    cases=[];outputs={}
    for events,topology in [('no_event','1'),('events','1'),('events','8')]:
        label=events+'_'+topology;work=a.raw/label;work.mkdir()
        argv=[str(probe.resolve()),str(cfg.resolve()),'1',events,topology]
        with (work/'stdout').open('w') as out,(work/'stderr').open('w') as err:
            proc=subprocess.run(argv,env=env,cwd=work,stdout=out,stderr=err,timeout=60)
        stdout=(work/'stdout').read_text();stderr=(work/'stderr').read_text()
        assert proc.returncode==0,(label,proc.returncode,stderr[-2000:])
        assert re.findall(r'^X2_CPU_LOADED_LIBRARY path=(.*)$',stdout,re.M)==[str(lib.resolve())]
        assert re.findall(r'^X2_CPU_LOADED_ELF path=(.*)$',stdout,re.M)==[str(probe.resolve())]
        assert 'kernels=0 gpu_cycle_calls=0 simulation_threads_started=0 print_state_unchanged=1' in stdout
        snapshots=parse(stdout);assert [s['header']['cycle'] for s in snapshots]==[0,13,22]
        for index,s in enumerate(snapshots):
            for sm,row in s['summary'].items():
                active=events=='events' and index>0 and sm==0
                assert row['broadcasts']==(2 if active else 0)
                assert row['first_notify_cycle_sum']==row['last_notify_cycle_sum']==(6 if active else 0)
                assert row['span_sum']==row['late_merges']==row['own_dep0_linewide_blocked_entry_cycles']==0
                assert row['notified_frontend_ready_entries']==(2 if active else 0)
                assert s['fanout'][sm][1]==(2 if active else 0)
                assert all(count==0 for bin,count in s['fanout'][sm].items() if bin!=1)
                assert all(value==0 for key,value in s['ldst'][sm].items() if key!='sm')
        assert snapshots[1]['summary']==snapshots[2]['summary'] and snapshots[1]['fanout']==snapshots[2]['fanout']
        outputs[label]=stdout
        cases.append(dict(case=label,argv=argv,returncode=proc.returncode,snapshots=3,
            sms_per_snapshot=64,fanout_bins_per_SM=33,
            stdout_sha256=sha(work/'stdout'),stderr_sha256=sha(work/'stderr'),
            final_SM0_summary=snapshots[-1]['summary'][0],final_SM0_ldst=snapshots[-1]['ldst'][0]))
    text=outputs['events_1'];lines=text.splitlines()
    index=next(i for i,line in enumerate(lines) if line.startswith(PREFIX+' sm=4 '))
    corrupt={
        'missing_SM':'\n'.join(lines[:index]+lines[index+1:]),
        'duplicate_SM':'\n'.join(lines[:index]+[lines[index]]+lines[index:]),
        'truncated_frame':text.rsplit(PREFIX+'_SNAPSHOT_END',1)[0],
        'duplicate_field':text.replace(PREFIX+' sm=4 ',PREFIX+' sm=4 sm=4 ',1),
        'bad_histogram':text.replace(PREFIX+'_FANOUT sm=0 bin=1 count=0',PREFIX+'_FANOUT sm=0 bin=1 count=1',1),
        'bad_sentinel':text.replace(PREFIX+'_SNAPSHOT_BEGIN version=1 sms=64 cycle=0 no_event_cycle_sentinel=18446744073709551615',PREFIX+'_SNAPSHOT_BEGIN version=1 sms=64 cycle=0 no_event_cycle_sentinel=0',1),
    }
    negatives=[]
    for label,bad in corrupt.items():
        assert bad!=text,label
        try:parse(bad)
        except ValueError as error:negatives.append(dict(case=label,status='REJECTED_AS_REQUIRED',reason=str(error)))
        else:raise AssertionError('corruption accepted: '+label)
    for info in inputs.values():assert sha(Path(info['path']))==info['sha256']
    result=dict(status='PASS_EXISTING_CPU_NORMAL_ON_EXPORT_SPARSE_FRONTEND_SCOPE_ONLY',
        inputs=inputs,cases=cases,parser_negative_checks=negatives,compiler_invocations=0,
        full_simulators_started=0,GPU_cycle_calls=0,kernels=0,simulation_threads_started=0,
        actual_entrypoint='existing compiled gpgpu_sim::gpu_print_stat(0)',
        scope='9 real normal-print boundaries at64 SM, zero and two one-waiter frontend API broadcasts, K1 ordinary pending/commit, topology1/8. No cacheable LDST PIB/value traffic, no progressive fanout>4 or WB/common-boundary validation. Original CTest failures remain failures; ON acceptance STOP remains.')
    (a.raw/'EXISTING_NORMAL_ON_EXPORT.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],processes=len(cases),normal_boundaries=9,negative_parser_checks=len(negatives),compiler_invocations=0)))
if __name__=='__main__':main()
