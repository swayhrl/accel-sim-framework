"""Read-only independent oracle-artifact review; no trace-body rescan or runtime grant."""
import argparse
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
import re
import sqlite3
import subprocess
from coordinator import Coordinator,CAMPAIGN,digest,require,write_json
from registry import canonical


def csv_counts(path):
    with Path(path).open() as stream:
        rows=list(csv.DictReader(stream))
    return {r['reason']:(int(r['lines']),int(r['read_lane_references'])) for r in rows}


def review(candidate_path,selection,core_repo):
    candidate=json.loads(Path(candidate_path).read_text());manifest_path=Path(candidate['manifest'])
    require(digest(manifest_path)==candidate['manifest_sha256'],'oracle manifest changed')
    manifest=json.loads(manifest_path.read_text());root=manifest_path.parent
    require(manifest['schema']=='EP_L2_RO_ORACLE_V1' and manifest['status']=='CERTIFIED_WITH_MODEL_SCOPE'
            and manifest['scope']=='TRACE_MODEL_CLOSED_WORLD' and manifest['epoch']=='whole_commandlist',
            'candidate does not have full explicit model scope')
    require(not manifest['unresolved_opcodes'],'unresolved whole-epoch opcode/address scope')
    require(candidate['tool_source_commit']==manifest['framework_source_commit'],'producer identity mismatch')
    raw=subprocess.check_output(['git','show',candidate['tool_source_commit']+':'+candidate['tool_source_path']])
    require(hashlib.sha256(raw).hexdigest()==candidate['tool_source_sha256'],'oracle producer hash differs from fetched Git')
    source=selection['full_input_identity']['runtime_independent_input_source'];entry=Path(source['entry_trace_path'])
    require(digest(entry)==manifest['commandlist_sha256'],'command list bytes changed')
    kernels=[];host_updates=[];initial_copies=[]
    for line in entry.read_text().splitlines():
        if line.startswith('kernel'):kernels.append(str((entry.parent/line).resolve()))
        elif line.startswith('MemcpyHtoD,'):
            _,addr,n=line.split(',');addr=int(addr,16);n=int(n)
            if not n:continue
            if kernels:host_updates.append([addr&~127,(addr+n-1)&~127])
            else:initial_copies.append({'address':addr,'bytes':n})
        elif not line.strip() or line.startswith(('#','MemcpyDtoH,')):continue
        else:raise ValueError('unreviewed command')
    require(kernels==[str(Path(k['path']).resolve()) for k in manifest['kernels']],'partial/reordered kernel epoch')
    require(manifest['kernel_count']==len(kernels)==candidate['kernel_count'],'kernel coverage count mismatch')
    require(host_updates==manifest['host_updates_excluded'],'post-initialization host updates not excluded')
    # Bind D's actual full-body scan to the preregistered input, without reading
    # those large bodies again. Fresh runtime admission still rehashes actual bytes.
    trace_manifest=[{'name':entry.name,'sha256':digest(entry),'bytes':entry.stat().st_size}]
    seen=set()
    for k in manifest['kernels']:
        p=Path(k['path']);require(p.name not in seen,'duplicate bodies require an explicit repeat adapter');seen.add(p.name)
        trace_manifest.append({'name':p.name,'sha256':k['sha256'],'bytes':p.stat().st_size})
    trace_hash=hashlib.sha256(canonical(sorted(trace_manifest,key=lambda x:x['name']))).hexdigest()
    require(trace_hash==selection['full_input_identity']['trace_content_sha256']==candidate['trace_content_sha256'],
            'oracle input differs from D preregistration')
    artifacts={}
    for name,sha in manifest['artifacts'].items():
        require(Path(name).name==name and digest(root/name)==sha,'oracle artifact changed: '+name)
        artifacts[name]={'sha256':sha,'bytes':(root/name).stat().st_size}
    # The producing runtime's inactive-warp memory behavior matters for legacy
    # traces. Check unchanged real source, rather than interpreting zero-mask
    # residual address tokens as actual GPU writes.
    memory_source='src/abstract_hardware_model.cc'
    data=subprocess.check_output(['git','-C',str(core_repo),'show','44c940b748fceaec8f21fa2b443907d5afd2756b:'+memory_source])
    parent=subprocess.check_output(['git','-C',str(core_repo),'show','84359d4ba492acb639a2092fa271e9169038bf7d:'+memory_source])
    require(data==parent and b'if (m_warp_active_mask.count() == 0) return;' in data,'native inactive-warp memory semantics changed')
    counts=Counter();refs=Counter();rows=0;ro_first=ro_last=None;range_start=range_end=None
    db=sqlite3.connect('file:'+str(root/'oracle.sqlite3')+'?mode=ro',uri=True)
    db.execute('PRAGMA query_only=ON');db.execute('PRAGMA cache_size=-16384')
    require(db.execute('PRAGMA integrity_check').fetchall()==[('ok',)],'oracle SQLite integrity failure')
    with (root/'certified_lines.txt').open() as certified,(root/'certified_ranges.csv').open() as ranges:
        ranges_reader=csv.DictReader(ranges)
        def check_range(first,last):
            row=next(ranges_reader,None)
            require(row is not None and int(row['first_line'],16)==first and int(row['last_line_inclusive'],16)==last,
                    'certified range export differs from real read/no-write/no-atomic set')
        for address,reads,writes,atomics in db.execute('SELECT address,reads,writes,atomics FROM lines ORDER BY address'):
            require(re.fullmatch('[0-9a-f]{16}',address) and int(address,16)%128==0,'invalid canonical line')
            require(min(reads,writes,atomics)>=0,'negative oracle coverage')
            rows+=1
            reason=('NO_GLOBAL_READ' if reads==0 else 'SAME_LINE_ATOMIC' if atomics else
                    'SAME_LINE_STORE' if writes else 'CERTIFIED_RO')
            counts[reason]+=1;refs[reason]+=reads
            if reason=='CERTIFIED_RO':
                value=int(address,16)
                require(all(not a<=value<=b for a,b in host_updates),'host-written line incorrectly certified')
                actual=certified.readline().strip();require(actual==address,'certified line set differs from independent SQL predicate')
                if ro_first is None:ro_first=value
                ro_last=value
                if range_end is not None and value!=range_end+128:check_range(range_start,range_end);range_start=None
                if range_start is None:range_start=value
                range_end=value
        require(not certified.read().strip(),'extra certified lines')
        if range_start is not None:check_range(range_start,range_end)
        require(next(ranges_reader,None) is None,'extra certified ranges')
    db.close()
    derived={name:(counts[name],refs[name]) for name in counts}
    require(csv_counts(root/'coverage.csv')==derived,'coverage CSV differs from independent database derivation')
    require(csv_counts(root/'exclusion.csv')=={k:v for k,v in derived.items() if k!='CERTIFIED_RO'},'exclusion CSV differs')
    for name,(number,references) in derived.items():
        require(manifest['counts'][name+'_lines']==number and manifest['counts'][name+'_read_lane_references']==references,
                'manifest differs from independent counts: '+name)
    return {'campaign_id':CAMPAIGN,'status':'INPUT_ORACLE_ARTIFACT_AND_SCOPE_REVIEW_PASS_PENDING_C_RUNTIME_AND_E_NATIVE_QUALIFICATION',
       'candidate_path':str(Path(candidate_path).resolve()),'candidate_sha256':digest(candidate_path),
       'manifest_path':str(manifest_path),'manifest_sha256':digest(manifest_path),'trace_content_sha256':trace_hash,
       'producer_commit':candidate['tool_source_commit'],'producer_sha256':candidate['tool_source_sha256'],
       'model_scope':manifest['scope'],'assumptions_not_measured':manifest['assumptions'],
       'epoch_boundary_clarification':'all selected kernels and intervening commands; initial HtoD prefix completes/drains before oracle activation; every later HtoD line excluded',
       'initial_HtoD_prefix':initial_copies,'post_activation_host_updates_excluded':host_updates,
       'database_rows_independently_checked':rows,'counts':{k:{'lines':v[0],'read_lane_references':v[1]} for k,v in derived.items()},
       'certified_first_line':None if ro_first is None else hex(ro_first),'certified_last_line':None if ro_last is None else hex(ro_last),
       'artifacts':artifacts,'full_trace_bodies_rescanned_by_E':False,
       'fresh_trace_bytes_required_at_runtime_admission':True,'native_zero_mask_generator_sha256':hashlib.sha256(data).hexdigest(),
       'data_version_or_runtime_qualification_granted':False,'application_performance_evidence':False,
       'interpretation_limit':'trace-model oracle and active-lane read references; not actual L2 misses, retained victims, useful in-flight requests or DRAM transactions'}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--candidate',type=Path,required=True)
    p.add_argument('--selection-id',required=True);p.add_argument('--core-repo',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    args=p.parse_args();selected=Coordinator().snapshot()['input_selections'][args.selection_id]
    require(digest(selected['path'])==selected['sha256'],'D registration changed')
    write_json(args.out,review(args.candidate,selected['selection'],args.core_repo))

if __name__=='__main__':main()
