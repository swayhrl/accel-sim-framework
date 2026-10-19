#!/usr/bin/env python3
"""Fresh bounded read-only SHA pass over the two exact original inputs only."""
from common import *
import csv
import io
import time
from resource_policy import headroom,GIB
from audit_site import snapshot


def main():
    audit=json.loads((PACK/'CURRENT_SITE_AUDIT.json').read_text())
    assert audit['all_resource_checks_pass']
    assert audit['authority']['status']=='PASS_CURRENT_NO_OTHER_DTC_DISPATCH_AUTHORITY'
    os.nice(19)
    dest=RAW/'input-member-sha';dest.mkdir(exist_ok=True)
    body=list(csv.DictReader(io.StringIO((PACK/'inputs/T/inputs/KERNEL_BODY_AUDIT.tsv').read_text()),delimiter='\t'))
    complete=[]
    started=time.monotonic();total_bytes=0;last_report=started;last_resource=started-10
    source_events=None
    def gate():
        nonlocal last_resource,source_events
        if time.monotonic()-last_resource<10:return
        s=snapshot();cg=s['cgroup'];last_resource=time.monotonic()
        assert s['host']=='huangrulin-174' and s['uid']==0
        assert s['host_MemAvailable_bytes']>=32*GIB and headroom(s)>=32*GIB
        assert s['disk_free_bytes']>=10*GIB
        assert float(s['pressure']['memory']['full']['avg10'])<=1 and float(s['pressure']['io']['full']['avg10'])<=25
        if source_events is None:source_events=cg['events']
        assert all(source_events[k]==cg['events'][k] for k in ['oom','oom_kill'])
    try:
        for workload,expected_n,expected_inst in [('GEMM',1,739246080),('Gaussian',510,283685120)]:
            spec=json.loads((PACK/f'inputs/T/inputs/{workload}_OO128_SPEC.json').read_text())
            assert len(spec['members'])==expected_n and spec['expected_instructions']==expected_inst
            original_list=Path(spec['trace_list'])
            data=original_list.read_bytes()
            assert hashlib.sha256(data).hexdigest()==spec['trace_list_sha256']
            assert data==(PACK/f'inputs/T/inputs/{workload}_kernelslist.g').read_bytes()
            names=[l for l in data.decode().splitlines() if l.startswith('kernel-')]
            assert names==[Path(m['path']).name for m in spec['members']]
            rr=sorted([r for r in body if r['workload'].lower()==workload.lower()],key=lambda r:int(r['ordinal']))
            assert sum(int(r['active_thread_instructions']) for r in rr)==expected_inst
            assert len(rr)==expected_n
            for ordinal,(m,b) in enumerate(zip(spec['members'],rr),1):
                gate()
                assert m['path']==b['path'] and m['sha256']==b['sha256']
                p=Path(m['path']);st=p.stat()
                identity={k:getattr(st,k) for k in ['st_dev','st_ino','st_size','st_mtime_ns','st_ctime_ns']}
                assert st.st_size==m['bytes']
                checkpoint=dest/f'{workload}_{ordinal:04d}.json'
                if checkpoint.exists():
                    row=json.loads(checkpoint.read_text())
                    assert row['stat_identity']==identity and row['actual_sha256']==m['sha256']
                else:
                    digest=hashlib.sha256()
                    with p.open('rb',buffering=1024*1024) as f:
                        for data in iter(lambda:f.read(1024*1024),b''):
                            digest.update(data);total_bytes+=len(data);gate()
                            delay=total_bytes/(8*1024*1024)-(time.monotonic()-started)
                            if delay>0:time.sleep(min(delay,.25))
                    after=p.stat()
                    assert identity=={k:getattr(after,k) for k in identity}
                    assert digest.hexdigest()==m['sha256']
                    row=dict(workload=workload,ordinal=ordinal,path=str(p),bytes=st.st_size,
                        expected_sha256=m['sha256'],actual_sha256=digest.hexdigest(),stat_identity=identity,
                        kernel=b['kernel'],active_thread_instructions=int(b['active_thread_instructions']),
                        complete_ctas=int(b['complete_ctas']),utc=now(),identity='PASS_FRESH_SHA256')
                    write(checkpoint,row,exclusive=True)
                complete.append(row)
                if time.monotonic()-last_report>=30:
                    print(json.dumps(dict(verified_members=len(complete),new_bytes_read=total_bytes,simulation_attempts=0)),flush=True)
                    last_report=time.monotonic()
        assert len(complete)==511
        table(PACK/'ORIGINAL_MEMBERS_SHA256.tsv',[{k:r[k] for k in ['workload','ordinal','path','bytes','expected_sha256','actual_sha256','kernel','active_thread_instructions','complete_ctas','identity']} for r in complete])
        write(PACK/'INPUT_STAT_IDENTITIES.json',complete)
        write(PACK/'INPUT_FULL_IDENTITY.json',dict(status='PASS_FRESH_ALL_511_MEMBER_SHA256',
            source_T_commit=T,full_commands=True,full_CTA_and_instruction_proof=True,
            roi='ALL_ORIGINAL_COMMANDS_ALL_KERNELS_NATURAL_EXIT_REQUIRED',members=len(complete),
            expected=dict(GEMM=dict(kernels=1,instructions=739246080),Gaussian=dict(kernels=510,instructions=283685120)),
            sha_table_sha256=sha(PACK/'ORIGINAL_MEMBERS_SHA256.tsv'),decoder_changes=0,trace_writes=0,
            simulation_attempts=0,new_bytes_read=total_bytes))
        print('PASS fresh SHA identities:',len(complete),flush=True)
    except Exception as exc:
        write(dest/'STOP.json',dict(status='STOP_CPU_SHA_VERIFICATION',reason=repr(exc),verified_members=len(complete),
            completed_checkpoints_preserved=True,simulation_attempts=0))
        raise


if __name__=='__main__':main()
