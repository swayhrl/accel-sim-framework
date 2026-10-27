"""Independent terminal validation and storage closure, with no model starts."""
import json, os, pathlib, sys
from ep_perf_common import *


def postprocess(case):
    registry, unused = authority()
    row = registry['registered_future_requests'][GOAL]['consumed'][case]
    if row['state'] in ['CLOSED_ACCEPTED','CLOSED_UNACCEPTED']:
        return dict(status=row['state'],cohort=case,already_closed=True)
    path=ROOT/'cases'/case/'control/FROZEN_SPEC.json'
    need(sha(path)==registry['registered_future_requests'][GOAL]['admitted_specs'][case],'registered spec changed')
    s=read(path)
    engine=module(s['host_engine_ref'],'postprocess_exact_host_engine')
    need(engine.spec_for(case)==s,'closed Source/input/mode/RO qualification changed')
    done=exact(row['done_ref'])
    out=P(done['output'])
    if row['state']=='NATURAL_COMPLETE_PENDING_VALIDATION':
        try:
            need(done==read(out/'NATIVE_EXIT.json') and done['uuid']==row['uuid'],'DONE/EXIT population')
            need(done['launcher_wait_returncode']==0 and done['stop_reason'] is None and done['native_simulator_observed'],'not a natural complete model')
            need(done['source_identity']==s['source_identity'] and done['spec_ref']==ref(path),'natural Source/spec identity')
            intent=exact(row['intent_ref'])
            need(intent['uuid']==row['uuid'] and intent['source_identity']==s['source_identity'] and intent['consumed_before_launcher_fork']==1,'intent/consume binding')
            need(set(done['closed_artifact_refs'])=={'NATIVE_LAUNCH.json','NATIVE_SIMULATOR_PID_AND_MAPS.json','actual_file_process_network.log'},'closed actual source evidence missing')
            for item in done['closed_artifact_refs'].values():
                need(sha(item['path'])==item['sha256'],'closed actual evidence changed')
            launch=read(out/'NATIVE_LAUNCH.json')
            pid=read(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json')
            h=module(s['helpers_ref'],'postprocess_exact_helpers')
            need(not h.pid_generation_live(pid),'same model generation still alive')
            need(not h.pid_generation_live(dict(pid=launch['launcher_pid'],start_ticks=launch['launcher_start_ticks'])),'same launcher generation still alive')
            expected_env=dict(PATH='/usr/bin:/bin',LANG='C',LC_ALL='C',CUDA_VISIBLE_DEVICES='',
                 LD_LIBRARY_PATH=str(NATIVE/'common-lib'),OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',
                 MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1',TMPDIR=str(out/'tmp'),
                 XDG_CACHE_HOME=str(out/'cache'),**s['observer_env'])
            need(launch['environment']==intent['environment']==pid['environment']==expected_env,'closed exact environment')
            need(launch['model_argv']==intent['model_argv']==pid['cmdline']==h.command(s,out),'closed exact model argv')
            need(launch['launcher_argv']==intent['launcher_argv']==h.launch_command(s,out),'closed exact launcher')
            need(launch['spec_sha256']==sha(path) and launch['source_identity']==s['source_identity'],'launch Source/spec')
            need(pid['actual_environment_exact'] and pid['affinity']==[launch['dispatch_binding']['host_cpu']],'actual CPU/environment proof')
            for file,item in launch['launch_capsule'].items():
                need(sha(out/file)==item['sha256'],'sealed launch file changed')
            need(h.syscall_proof(out/'actual_file_process_network.log',s,pid['pid'])==done['syscall_proof'],'closed syscall proof mismatch')
            output=module(s['output_module_ref'],'postprocess_gzip')
            raw=out/'raw.log.gz'
            need(done['raw_compressed_ref']==ref(raw),'raw compressed reference changed')
            integrity=output.verify_raw(raw,done['raw_stream_receipt'])
            parser=module(s['validation_module_ref'],'postprocess_terminal')
            qualification=read(out/'NATIVE_PRELAUNCH_QUALIFICATION.json')
            bundle=parser.validate_case(raw,s,qualification,s['source_qualification_ref']['path'],s['source_qualification_ref']['sha256'])
            need(bundle['status']=='EP_FULL_PERF_VALIDATED_PENDING_MAIN_NOT_APPLICATION_ACCEPTED','terminal parser status')
            need(bundle['raw_logical_sha256']==integrity['raw_sha256'] and bundle['raw_stored_sha256']==integrity['stored_sha256'],'validation raw identities disagree')
            compact=module(s['compact_module_ref'],'postprocess_compact')
            receipt=compact.exact_bundle(bundle,out/'VALIDATED_APPLICATION_BUNDLE.json',s['limits']['result_bytes']-h.footprint(out))
            point=dict(status='EP_FULL_PERF_APPLICATION_ACCEPTED',archive_status='PENDING_MANDATORY_ARCHIVE_CLOSURE',goal=GOAL,
                cohort=case,uuid=row['uuid'],source_identity=s['source_identity'],spec_ref=ref(path),done_ref=row['done_ref'],
                validation_ref=ref(out/'VALIDATED_APPLICATION_BUNDLE.json'),validation_module_ref=s['validation_module_ref'],
                raw_stream_receipt=done['raw_stream_receipt'],mode=s['mode'],profile=s['profile'],
                input_identity_sha256=s['input_identity_sha256'],numeric_output='UNKNOWN',source_keep=True,
                **{k:bundle[k]for k in ['cycles','instructions','CTA','kernel_count','hardware_drained']})
            block=os.statvfs(out).f_frsize
            projected_point=((len(encoded(point))+block-1)//block)*block+2*block
            need(h.footprint(out)+projected_point<=s['limits']['result_bytes'],'exact compact point increment exceeds result bound')
            point_ref=put(out/'ACCEPTED_POINT.json',point,True)
            need(h.footprint(out)<=s['limits']['result_bytes'],'exact final compact result exceeds bound')
            def record(reg):
                current=reg['registered_future_requests'][GOAL]['consumed'][case]
                need(current['done_ref']==row['done_ref'] and current['state']=='NATURAL_COMPLETE_PENDING_VALIDATION','terminal row changed')
                current.update(state='ACCEPTED_PENDING_ARCHIVE',accepted_point_ref=point_ref,
                               validation_ref=point['validation_ref'],compact_bundle_receipt=receipt)
            transaction('RECORD_VALIDATED_POINT_PENDING_ARCHIVE_NO_RETRY',record)
        except Exception as exc:
            failure=put(out/'VALIDATION_HOLD.json',dict(goal=GOAL,cohort=case,reason=repr(exc),
                        scientific_acceptance_granted=False,spent_start_preserved=True,automatic_retry=False),True)
            def hold(reg):
                current=reg['registered_future_requests'][GOAL]['consumed'][case]
                need(current['state']=='NATURAL_COMPLETE_PENDING_VALIDATION','terminal row changed')
                current.update(state='PARSE_HOLD',validation_hold_ref=failure)
            transaction('PRESERVE_TERMINAL_PARSE_HOLD_NO_REFUND',hold)
            return dict(status='PARSE_HOLD',cohort=case,reason=repr(exc))
    archive=module(s['archive_module_ref'],'postprocess_archive')
    return archive.archive_case(case)


if __name__=='__main__':
    need(len(sys.argv)==2,'exact cohort required')
    print(json.dumps(postprocess(sys.argv[1])))
