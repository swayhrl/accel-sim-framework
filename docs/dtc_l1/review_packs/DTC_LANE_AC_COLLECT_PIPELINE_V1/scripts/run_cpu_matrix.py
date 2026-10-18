"""CPU-only production-LDST qualification. Never executes a simulator main."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
from parse_collect_wb import parse, PREFIX

CASES = [('pair',4,0),('pair',8,0),('pair',16,0),('single',4,0),('single',16,0),
         ('empty',4,0),('denied',4,0),('denied',16,0),('arbitration',4,0),
         ('fence',4,0),('same_warp',4,0),('partial',8,0),('partial',16,0),
         ('late_waiter',4,0),('generation',4,1),('k1_refs',8,1),('sidecars',4,0)]


def digest(data): return hashlib.sha256(data).hexdigest()
def numbers(line): return {k:int(v) for k,v in re.findall(r'([a-z_]+)=(\d+)',line)}
def common(text):
    return '\n'.join(line for line in text.splitlines()
                     if line.startswith(('AC_EDGE ', 'AC_ENTRY ', 'AC_STATE '))) + '\n'
def normal(text):
    sections=re.findall(r'AC_NORMAL_BEGIN id=\d+\n(.*?)AC_NORMAL_END id=\d+\n', text, re.S)
    assert len(sections)==3
    # This one existing source field divides GPU instructions by host wall time.
    # It is excluded explicitly; no simulated metric or DTC statistic is removed.
    return ['\n'.join(line for line in part.splitlines()
                      if not line.startswith('gpu_total_sim_rate='))+'\n' for part in sections]


def main():
    p=argparse.ArgumentParser()
    for key in ['probe','baseline-probe','core','baseline-library','output']:
        p.add_argument('--'+key,required=True,type=Path)
    args=p.parse_args(); root=args.output; root.mkdir(parents=True,exist_ok=False)
    paths=[args.probe,args.baseline_probe,args.probe.parent/'libcudart.so',args.baseline_library]
    identities={str(path):digest(path.read_bytes()) for path in paths}
    config=args.core/'configs/tested-cfgs/SM7_GV100/gpgpusim.config'
    receipts=[]; outputs={}; compares=[]; normals=[]; negatives=[]
    def run(label,exe,flag,case,sectors,k1=0,sms=1,mode=3,finite=1,expect=True):
        lib=args.baseline_library if exe==args.baseline_probe else args.probe.parent/'libcudart.so'
        env=os.environ.copy(); env.pop('LD_PRELOAD',None); env.pop('LD_AUDIT',None)
        env['LD_LIBRARY_PATH']=str(lib.parent)
        argv=[str(exe),str(config),flag,case,str(sectors),str(mode),str(finite),str(k1),str(sms)]
        proc=subprocess.run(argv,env=env,cwd=root,capture_output=True,timeout=60)
        out=root/(label+'.stdout'); err=root/(label+'.stderr')
        out.write_bytes(proc.stdout); err.write_bytes(proc.stderr)
        txt=proc.stdout.decode(); error=proc.stderr.decode()
        rec={'case':label,'argv':argv,'returncode':proc.returncode,
             'stdout':{'path':str(out),'sha256':digest(proc.stdout)},
             'stderr':{'path':str(err),'sha256':digest(proc.stderr)},
             'probe_sha256':identities[str(exe)],'loaded_library':str(lib),
             'loaded_library_sha256':identities[str(lib)],
             'actual_library_maps':[line for line in txt.splitlines() if line.startswith('AC_LIBRARY_MAP ')]}
        receipts.append(rec)
        if not expect:
            assert proc.returncode!=0 and 'DTC_COLLECT_WB_REQUIRES_PAPER_OO_FINITE_V1_L1D_STOP' in error,(label,error[-2000:])
            rec['verdict']='REJECTED_UNSUPPORTED_CONFIGURATION'
            return txt
        assert proc.returncode==0,(label,error[-3000:])
        assert f'AC_LIBRARY {lib}\n' in txt and f'AC_ELF {exe}\n' in txt
        assert rec['actual_library_maps']
        assert 'AC_RESULT status=PASS_CPU_LDST_COMPONENT' in txt or case=='mode_only'
        rec['verdict']='PASS_REAL_LDST_CPU_COMPONENT' if case!='mode_only' else 'PASS_MODE_INIT_ONLY'
        if case=='mode_only': return txt
        decoded=parse(txt,enabled=(flag=='1'),sms=sms)
        if flag=='1':
            assert decoded['snapshots']==3
            r=decoded['rows'][0]
            edges=[numbers(line) for line in txt.splitlines() if line.startswith('AC_EDGE ')]
            assert r['samples']==len(edges)
            assert r['collected_sectors']==sum(e['sectors'] for e in edges)
            assert r['retires']==sum(e['retires'] for e in edges)
            prior_closed=0; measured_overlap=0
            for edge in edges:
                measured_overlap += bool(edge['sectors'] and edge['closed'] > prior_closed)
                prior_closed=edge['closed']
            assert r['overlap_cycles']==measured_overlap
            if case=='pair': assert r['overlap_cycles']>0
            if case=='denied':
                assert r['wb_denied_attempts']>0 and r['peak_buffered_sectors']>=8
                if sectors==4:
                    assert r['result_backpressure_cycles']>0 and r['collect_idle_eligible_cycles']>0
            if case=='arbitration': assert r['wb_arbitration_blocked_cycles']>0
            if sms==64:
                assert all(row['samples']==0 and row['first_cycle']==(1<<64)-1 for sm,row in decoded['rows'].items() if sm!=0)
            rec['last_pipeline_snapshot']=decoded
        outputs[label]=txt
        return txt
    for case,sectors,k1 in CASES:
        key=f'{case}-{sectors}-k{k1}'
        base=run('base-'+key,args.baseline_probe,'omitted',case,sectors,k1)
        omitted=run('omitted-'+key,args.probe,'omitted',case,sectors,k1)
        zero=run('zero-'+key,args.probe,'0',case,sectors,k1)
        one=run('one-'+key,args.probe,'1',case,sectors,k1)
        assert common(base)==common(omitted)==common(zero),(key,'per-edge state/quota/ledger mismatch')
        compares.append({'case':key,'status':'BYTE_IDENTICAL_TYPED_CPU_STATE_EACH_EDGE',
                         'sha256':digest(common(base).encode()),'edges':common(base).count('AC_EDGE ')})
        for boundary,(b,o,z) in enumerate(zip(normal(base),normal(omitted),normal(zero))):
            assert b==o==z,(key,boundary,'normal public statistics mismatch')
            normals.append({'case':key,'boundary':boundary,'status':'BYTE_IDENTICAL_OLD_NORMAL_PUBLIC_OUTPUT_EXCEPT_HOST_RATE', 'sha256':digest(b.encode())})
        if case=='pair':
            def retirement_edges(txt): return [numbers(line)['cycle'] for line in txt.splitlines() if line.startswith('AC_EDGE ') and numbers(line)['retires']]
            assert retirement_edges(one)[0]==retirement_edges(zero)[0]
            assert retirement_edges(one)[-1]+1==retirement_edges(zero)[-1]
        if case in ['single','empty']:
            assert common(zero)==common(one),(key,'isolated/empty behavior differs')
    full=run('one-normal64-k1',args.probe,'1','pair',16,1,64)
    run('one-empty64',args.probe,'1','empty',4,0,64)
    run('zero-empty64',args.probe,'0','empty',4,0,64)
    for mode in [0,1,2,4]:
        run(f'bad-mode-{mode}',args.probe,'1','mode_only',4,0,1,mode,0,False)
        run(f'off-mode-{mode}',args.probe,'0','mode_only',4,0,1,mode,0,True)
    run('bad-finite-zero',args.probe,'1','mode_only',4,0,1,3,0,False)
    # Corrupt only the last frame, leaving older valid frames to test no fallback.
    start=full.rfind(PREFIX+'SNAPSHOT_BEGIN '); end=full.index(PREFIX+'SNAPSHOT_END ',start)
    lines=full[start:end].splitlines(keepends=True); row=lines[1]
    corruptions={
      'missing_sm':full[:start]+''.join(lines[:1]+lines[2:])+full[end:],
      'duplicate_sm':full[:end]+row+full[end:],
      'truncated_final':full[:end],
      'truncated_row':full[:end]+row[:-8],
      'missing_field':full[:start]+full[start:].replace('samples=0 ','',1),
      'duplicate_field':full[:end]+row.replace('sm=0','sm=0 sm=0')+full[end:],
      'oversize_field':full[:start]+full[start:].replace('samples=0','samples=18446744073709551616',1),
      'bad_sentinel':full[:start]+full[start:].replace('first_cycle=18446744073709551615','first_cycle=0',1),
      'bad_sector_total':full[:start]+full[start:].replace('collected_sectors=0','collected_sectors=1',1),
      'bad_capacity':full[:start]+full[start:].replace('total_buffer_capacity_bytes=163840','total_buffer_capacity_bytes=1',1),
      'bad_cycle_quota':full[:start]+full[start:].replace('last_cycle_sectors=0','last_cycle_sectors=5',1),
      'unframed_private':row,
      'missing_export':''.join(line for line in full.splitlines(keepends=True) if not line.startswith(PREFIX)),
      'bad_version':full[:start]+full[start:].replace('version=1','version=2',1),
      'final_newline_missing':full.rstrip('\n'),
    }
    for case,txt in corruptions.items():
        try: parse(txt,sms=64)
        except ValueError as error: negatives.append({'case':case,'status':'REJECTED_AS_REQUIRED','reason':str(error)})
        else: raise AssertionError('accepted corruption '+case)
    try: parse(full,enabled=False,sms=64)
    except ValueError: negatives.append({'case':'OFF_unexpected_export','status':'REJECTED_AS_REQUIRED'})
    else: raise AssertionError('OFF accepted export')
    assert identities=={str(path):digest(path.read_bytes()) for path in paths}
    result={'status':'PASS_CPU_REAL_LDST_PIPELINE_SCOPE_ONLY','core':subprocess.check_output(['git','-C',str(args.core),'rev-parse','HEAD'],text=True).strip(),
            'config':{'path':str(config),'sha256':digest(config.read_bytes())},
            'binary_hashes_before_after_identical':identities,'processes':receipts,
            'OFF_state_equivalence':compares,'OFF_normal_stat_equivalence':normals,
            'negative_parser_checks':negatives,'snapshot_semantics':'last whole population; cumulative; never summed',
            'sampling_scope':'CPU component edges, not workload performance',
            'full_simulators_started':0,'canary_simulators_started':0,'native_or_GPU_programs_started':0,
            'instruction_value_correctness':'UNPROVEN','full_ISA_integration':'NOT_TESTED',
            'seams':'controlled issue/admission alignment; actual LDST cycle, RFU denial, lower CPU packets and normal gpu_print_stat'}
    (root/'CPU_TEST_RECEIPTS.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'processes':len(receipts),'OFF_state_cases':len(compares),'OFF_normal_boundaries':len(normals),'negative_parser_checks':len(negatives)}))

if __name__=='__main__': main()
