"""Full-byte/native-source proof for legacy zero-mask extended memory address rows."""
import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import time

import atomic_trace_scope as opcode_audit
from registry import Registry,write_json,process_identity,local_resources
from run import digest,content_hash,result_disk_free_bytes,RESULT_DISK_FLOOR

MEMORY={'LD','LDG','LDS','LDL','LDC','ST','STG','STS','STL'}


def native_fields(line,version,lineinfo):
    """Independently index the exact fields consumed by native parse_from_string."""
    w=line.split();i=(4 if version<3 else 0)+lineinfo
    pc=int(w[i],16);mask=int(w[i+1],16);i+=2;nd=int(w[i]);i+=1+nd
    opcode=w[i];i+=1;ns=int(w[i]);i+=1+ns;width=int(w[i]);i+=1
    tail=w[i:];n=mask.bit_count();extended=False
    if width:
        mode=int(tail[0]);fields=tail[1:]
        if mode==0:
            assert len(fields)>=n
            for token in fields[:n]:assert 0<=int(token,16)<2**64
            # Standard list_all reads exactly popcount(mask) addresses. A sole
            # following scalar may be native imm. Full32 residual address fields
            # are permitted here ONLY if mask0, ordinary LD/ST and trace v0/1/2.
            if len(fields)>n+1:
                if not(version<3 and mask==0 and len(fields)==32 and opcode.split('.')[0] in MEMORY):
                    raise ValueError('UNSUPPORTED_TRACE_FORMAT: nonzero/modern/nonmemory extended address tail')
                assert all(0<=int(token,16)<2**64 for token in fields)
                extended=True
    return pc,mask,opcode,extended


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--preparation',type=Path,required=True);ap.add_argument('--framework',type=Path,required=True);ap.add_argument('--core',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--deadline-unix',type=float,required=True);a=ap.parse_args()
    if a.out.exists():raise ValueError('Frozen proof exists')
    def stop(signum,frame):raise KeyboardInterrupt('owned semantic input proof stopped')
    signal.signal(signal.SIGTERM,stop)
    report={'status':'INCOMPLETE_NO_NEW_SCOPE_CLEARANCE','schema_version':'EPL2_NATIVE_ZERO_MASK_SOURCE_AND_FULL_BYTES_PROOF_V1','tool_sha256':digest(__file__),'tooling_source_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'controller':process_identity(os.getpid()),'workloads':[],'new_compiler_or_simulator_executions':0};lease=None
    def guard():
        r=local_resources()
        if time.time()>=a.deadline_unix-5 or r['disk_free_bytes']<48*1024**3 or r['available_memory_bytes']<64*1024**3 or result_disk_free_bytes()<RESULT_DISK_FLOOR:raise ValueError('Original resource/deadline floor')
    try:
        guard();lease=Registry().build_lease('lane5',cpu=1,memory=4*1024**3);report['resource_lease']=lease
        spec=json.loads((a.preparation/'specs/convolutionSeparable_B16_BANKED.json').read_text());identity=spec['identity'];maps,bindings=opcode_audit.source_maps(a.framework,identity['framework_source_commit']);report['native_framework_files_sha256']=bindings
        source='src/abstract_hardware_model.cc';data=(a.core/source).read_bytes();assert data==subprocess.check_output(['git','show',identity['core_source_commit']+':'+source],cwd=a.core);report['core_memory_generator_sha256']=hashlib.sha256(data).hexdigest();assert b'if (m_warp_active_mask.count() == 0) return;' in data
        report['source_identity']={k:identity[k] for k in ('core_source_commit','framework_source_commit','binary_sha256')};assert digest(spec['binary'])==identity['binary_sha256'];write_json(a.out,report)
        original=opcode_audit.instruction
        for workload,revision in [('convolutionSeparable','r2'),('FWT_7_21','r1')]:
            spec=json.loads((a.preparation/'specs'/f'{workload}_B16_BANKED.json').read_text());prior=json.loads((a.preparation/f'{workload}_ATOMIC_SCOPE_{revision}.json').read_text());assert prior['input_scope']=='COMPLETE_INPUT_HAS_NO_NATIVE_ATOMIC_OPCODE_RECORDS';expected={r['name']:r for r in prior['trace_files']};wr={'workload':workload,'files':[],'native_source_semantics':'List_all consumes only active-lane addresses and sets inactive addresses0. Then ss>>imm attempts first residual scalar; trace.imm is consumed only by OP_DEPBAR, never any observed extended ordinary memory opcode. Trace-driven copies original mask; generate_mem_accesses returns before any request when mask.count()==0. Zero-mask instruction records remain in full native input and front-end timing; no rows/bytes removed.'}
            report['workloads'].append(wr)
            for item in spec['trace_files']:
                guard()
                if item['name']==spec['entry_trace_name']:continue
                stats={'extended_zero_mask_rows':0,'not_native_address_fields':0,'extended_opcodes':Counter(),'all_records':0,'all_active_lane_records':0,'normalized_extended_rows_sha256':hashlib.sha256(),'examples':[]}
                def wrapped(line,version,lineinfo,block,warp,opcodes):
                    result=original(line,version,lineinfo,block,warp,opcodes);pc,mask,op,extended=native_fields(line,version,lineinfo);assert result[0]==op and result[2]==mask.bit_count();stats['all_records']+=1;stats['all_active_lane_records']+=mask.bit_count()
                    if extended:
                        stats['extended_zero_mask_rows']+=1;stats['not_native_address_fields']+=32;stats['extended_opcodes'][op]+=1;stats['normalized_extended_rows_sha256'].update((line+'\n').encode())
                        if len(stats['examples'])<2:stats['examples'].append({'normalized_full_instruction':line,'pc':pc,'mask':mask,'native_lane_addresses':[0]*32,'memory_requests':0,'residual_first_field':'attempted as imm; semantically unused by this memory opcode'})
                    return result
                opcode_audit.instruction=wrapped
                try:parsed,raw=opcode_audit.kernel(item['path'],maps,guard)
                finally:opcode_audit.instruction=original
                e=expected[item['name']];assert raw=={k:e[k] for k in ('sha256','bytes')};assert parsed['instruction_records']==stats['all_records']==e['instruction_records'];assert parsed['active_lane_instruction_records']==stats['all_active_lane_records']==e['active_lane_instruction_records'];assert parsed['atomic_absence']
                stats['normalized_extended_rows_sha256']=stats['normalized_extended_rows_sha256'].hexdigest();stats['extended_opcodes']=dict(stats['extended_opcodes']);wr['files'].append({'name':item['name'],**raw,**stats});write_json(a.out,report)
            wr['status']='FULL_ORIGINAL_BYTES_AND_NATIVE_ZERO_MASK_SEMANTICS_PROVEN'
        report['status']='PASS_FULL_NATIVE_BYTE_AND_ZERO_MASK_SEMANTIC_PROOF';report['scope']='Source-derived independently indexed field proof plus complete raw-byte/record closure; no native C++ unit invocation or numerical SASS claim. Existing formal applications consume the untouched full original files; require their normal full native terminal separately.'
    except BaseException as error:report['status']='FAILED_NO_NEW_SCOPE_CLEARANCE';report['error']=repr(error);raise
    finally:
        if lease:Registry().release_build(lease,'lane5');report['lease_terminal']='RELEASED'
        write_json(a.out,report)
    print(json.dumps({'status':report['status'],'workloads':[(w['workload'],sum(f['extended_zero_mask_rows'] for f in w['files'])) for w in report['workloads']],'report':str(a.out)}))


if __name__=='__main__':main()
