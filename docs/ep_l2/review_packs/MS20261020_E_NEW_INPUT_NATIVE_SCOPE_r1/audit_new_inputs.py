"""Finite missing native-input proof for btree/dwt2d, not a simulator/qualifier.

Retains the five existing complete input proofs. Reuses pinned native opcode
and exact zero-mask field decoders with a reviewed current source schema. The
parent alone owns one original E test lease and monitors only its own child.
"""
from pathlib import Path
import hashlib, json, os, signal, subprocess, sys, time
sys.path.insert(0,'/workspace/worktrees/accel-sim-ep-l2-ms20261019-e-eval-v1/util/ep_l2/mechanism_e')
import coordinator as c
import run as legacy
import atomic_trace_scope as op
import native_legacy_trace_proof as fields
from runner import disable_owned_core_dumps

PREPARATION=Path(__file__).with_name('PREPARATION.json')
OUT=c.OUTPUT/'E_NEW_BTREE_DWT_NATIVE_INPUT_SCOPE_r1'


def worker():
    os.nice(10)
    p=json.loads(PREPARATION.read_text())
    for name in ('opcode_tool','byte_semantic_tool'):
        c.require(c.digest(p[name]['path'])==p[name]['sha256'],'pinned input decoder changed')
    c.require(c.digest(p['schema_path'])==p['schema_sha256'],'current reviewed source schema changed')
    op.SCHEMA=Path(p['schema_path']) # This child only; original old schema stays immutable.
    maps,bindings=op.source_maps(p['framework'],p['source_identity']['framework_source_commit'])
    source='src/abstract_hardware_model.cc';data=(Path(p['core'])/source).read_bytes()
    c.require(data==subprocess.check_output(['git','show',p['source_identity']['core_source_commit']+':'+source],cwd=p['core']) and
              b'if (m_warp_active_mask.count() == 0) return;' in data,'actual native memory generator changed')
    report=dict(status='INPUT_SCOPE_RUNNING_NOT_QUALIFIED',source_identity=p['source_identity'],workloads=[],
                source_bindings=bindings,memory_generator_sha256=hashlib.sha256(data).hexdigest(),
                compiler_or_simulator_starts=0,tool_sha256=c.digest(__file__))
    for selected in p['selections']:
        w=dict(selection_id=selected['selection_id'],files=[],status='PENDING')
        report['workloads'].append(w)
        try:
            c.require(c.digest(selected['selection_path'])==selected['selection_sha256'],'D input preregistration changed')
            inp=selected['selection']['full_input_identity'];src=inp['runtime_independent_input_source']
            manifest=legacy.asset_manifest(src['trace_files'])
            c.require(legacy.content_hash(manifest)==inp['trace_content_sha256'],'complete input bytes changed')
            legacy.validate_trace_closure(dict(trace_files=src['trace_files'],entry_trace_name=src['entry_trace_name']))
            w['trace_manifest']=manifest;w['trace_content_sha256']=inp['trace_content_sha256']
            for item in src['trace_files']:
                if item['name']==src['entry_trace_name']:continue
                original=op.instruction;extended=[0];hist={}
                def checked(line,version,lineinfo,block,warp,opcodes):
                    decoded=original(line,version,lineinfo,block,warp,opcodes)
                    pc,mask,opcode,extra=fields.native_fields(line,version,lineinfo)
                    c.require(opcode==decoded[0] and mask.bit_count()==decoded[2],'native field decoding mismatch')
                    if extra:extended[0]+=1;hist[opcode]=hist.get(opcode,0)+1
                    return decoded
                op.instruction=checked
                try:parsed,raw=op.kernel(item['path'],maps)
                finally:op.instruction=original
                expected=next(r for r in manifest if r['name']==item['name'])
                c.require(raw=={k:expected[k] for k in ('bytes','sha256')},'full raw-byte closure changed')
                c.require(parsed['atomic_absence'],'native atomic records outside current application scope')
                w['files'].append(dict(name=item['name'],**raw,**parsed,
                    extended_native_zero_mask_records=extended[0],extended_opcodes=hist))
                c.write_json(OUT/'SCOPE.json',report)
            c.require(sum(v['active_lane_instruction_records'] for v in w['files'])==inp['expected_full_instructions'],
                      'D full instruction count does not match complete native source input')
            w['status']='COMPLETE_ORIGINAL_NATIVE_NONATOMIC_BYTE_AND_ZERO_MASK_SCOPE_PASS'
        except BaseException as error:
            w.update(status='FAILED_INPUT_SCOPE_NOT_AUTHORIZED',error=repr(error))
        c.write_json(OUT/'SCOPE.json',report)
    report['status']='ALL_TWO_NEW_INPUT_SCOPES_PASS' if all(w['status'].endswith('_PASS') for w in report['workloads']) else 'AFFECTED_INPUT_SCOPES_FAILED'
    c.write_json(OUT/'SCOPE.json',report)
    print(report['status'],flush=True)


def supervise():
    def interrupted(signum,frame):raise KeyboardInterrupt('owned input audit interrupted')
    signal.signal(signal.SIGTERM,interrupted);disable_owned_core_dumps()
    c.tooling_binding();p=json.loads(PREPARATION.read_text());coord=c.Coordinator()
    c.require(p['source_identity']==coord.snapshot()['final_source_identity'],'wrong final input/source scope')
    c.require(not OUT.exists(),'frozen input audit exists; no replay')
    OUT.mkdir(exist_ok=False);(OUT/'tmp').mkdir();lease=None;proc=None;status='INCOMPLETE';start=time.monotonic();peak=0
    receipt=dict(source_identity=p['source_identity'],input_audit_only=True,compiler_or_simulator_starts=0,
                 preparation_sha256=c.digest(PREPARATION),entry_sha256=c.digest(__file__))
    try:
        lease=coord.reserve_work('E','test',1,4*c.GIB,128*2**20,OUT)
        receipt['lease']=lease
        with (OUT/'raw.log').open('xb') as log:
            proc=subprocess.Popen([sys.executable,'-B',str(Path(__file__).resolve()),'--worker'],cwd=OUT,
                stdout=log,stderr=subprocess.STDOUT,start_new_session=True,
                env=dict(os.environ,TMPDIR=str(OUT/'tmp'),TMP=str(OUT/'tmp'),TEMP=str(OUT/'tmp'),
                         PYTHONDONTWRITEBYTECODE='1',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1'))
            receipt['process']=coord.bind_work_process(lease['lease_id'],'E',proc.pid)
            c.write_json(OUT/'RECEIPT.json',dict(receipt,status='ACTUAL_INPUT_AUDIT_RUNNING'))
            while proc.poll() is None:
                live=c.local_resources();usage=c.output_usage();peak=max(peak,legacy.process_tree_rss(proc.pid))
                incident=c.disk_policy.stop_detail(live,lease)
                if incident or live['share_disk_free_bytes']<40*c.GIB or live['available_memory_bytes']<64*c.GIB or peak>4*c.GIB or c.retained_tree_bytes(OUT)>=128*2**20 or usage['new_bytes']>=6*c.GIB or usage['total_bytes']>=20*c.GIB:
                    status='RESOURCE_LIMIT';receipt['resource_limit']=dict(incident or {},process=receipt['process'],
                        lease_id=lease['lease_id'],resources=live,source_identity=p['source_identity'],output_usage=usage)
                    c.write_json(OUT/'RESOURCE_LIMIT.json',receipt['resource_limit']);legacy.terminate_owned(proc);break
                c.require(time.monotonic()-start<5400 and time.time()<c.INTAKE_DEADLINE,'bounded input-audit timeout')
                time.sleep(lease['monitor_interval_seconds'])
        if status!='RESOURCE_LIMIT':
            c.require(proc.returncode==0,'input worker failed; partial evidence retained')
            result=json.loads((OUT/'SCOPE.json').read_text());status=result['status']
    except BaseException as error:
        receipt['error']=repr(error)
        if status!='RESOURCE_LIMIT':status='FAILED_INPUT_AUDIT_NO_SCOPE_GRANT'
    finally:
        if proc:legacy.terminate_owned(proc)
        receipt.update(status=status,peak_rss_bytes=peak,wall_seconds=time.monotonic()-start,
            exit_code=proc.returncode if proc else None,raw_sha256=c.digest(OUT/'raw.log') if (OUT/'raw.log').exists() else None)
        if 'resource_limit' in receipt:
            receipt['resource_limit'].update(exit_code=receipt['exit_code'],raw_sha256=receipt['raw_sha256'])
            c.write_json(OUT/'RESOURCE_LIMIT.json',receipt['resource_limit'])
        if lease:coord.release_work(lease['lease_id'],'E','finite missing native input proof terminal; all evidence retained',no_child_started=proc is None)
        c.write_json(OUT/'RECEIPT.json',receipt)
    print(json.dumps(dict(status=status,lease_id=lease['lease_id'] if lease else None)))


if __name__=='__main__':
    if '--worker' in sys.argv:worker()
    else:supervise()
