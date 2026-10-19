"""Collect completed whole-input oracle candidates without re-reading bodies.

Copies small hashed evidence only; raw SQLite/full address lists stay in the
new D namespace and count towards E's output cap. Never upgrades a runtime.
"""
import csv
import hashlib
import json
from pathlib import Path
import shutil
from prepare_full_v2 import OUT, WORKLOADS, dump, table, UNKNOWN

RAW=Path('/workspace/ep_l2_ms20261019_e_results/D_OFFLINE_INPUT_ANALYSIS')

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def collect():
    index=json.loads((OUT/'SEVEN_INPUTS.json').read_text());reports=[]
    for row in index['workloads']:
        w=row['workload'];root=RAW/(w+('_r1' if w=='convolutionSeparable' else '_v2_r1'))
        receipt=root/'RECEIPT.json'
        if not receipt.exists():continue
        r=json.loads(receipt.read_text())
        if r.get('worker_exit_code')!=0 or not (root/'CANDIDATE.json').exists():
            row['readonly_evidence']='OFFLINE_INCOMPLETE_NO_CERTIFICATE_FALLBACK';continue
        c=json.loads((root/'CANDIDATE.json').read_text());manifest=root/'oracle/manifest.json'
        if digest(manifest)!=c['manifest_sha256']:raise ValueError('changed whole-input manifest')
        m=json.loads(manifest.read_text())
        if c['trace_content_sha256']!=row['full_trace_content_sha256'] or c['kernel_count']!=row['kernel_count']:
            raise ValueError('cannot attach another input certificate')
        files=[]
        # Full raw list/SQLite identities come from the immutable producer.
        # Only small visible evidence is copied. Never duplicate the big bodies.
        for name in ['coverage.csv','exclusion.csv','certified_ranges.csv']:
            f=root/'oracle'/name
            if digest(f)!=m['artifacts'][name]:raise ValueError('changed oracle artifact '+name)
            files.append({'path':str(f),'sha256':m['artifacts'][name],'bytes':f.stat().st_size})
        copied=[];dest=OUT/'readonly_evidence'/w;dest.mkdir(parents=True,exist_ok=True)
        for f in [root/'CANDIDATE.json',receipt,manifest]+[Path(a['path']) for a in files]:
            if f.stat().st_size<=512*1024:
                target=dest/f.name;shutil.copyfile(f,target);copied.append(str(target.relative_to(OUT)))
        counts=c['counts'];complete_model=c['oracle_status']=='CERTIFIED_WITH_MODEL_SCOPE' and not c['unresolved_opcodes']
        total_lines=sum(n for k,n in counts.items() if k.endswith('_lines'))
        total_read_lines=sum(n for k,n in counts.items() if k.endswith('_lines') and not k.startswith('NO_GLOBAL_READ'))
        total_read_refs=sum(n for k,n in counts.items() if k.endswith('_read_lane_references'))
        certified=counts.get('CERTIFIED_RO_lines',0) if complete_model else 0
        refs=counts.get('CERTIFIED_RO_read_lane_references',0) if complete_model else 0
        row.update(readonly_evidence='WHOLE_EPOCH_MODEL_CANDIDATE_PENDING_C_E_REVIEW' if w!='convolutionSeparable' else row['readonly_evidence'],
          model_certified_lines=certified,model_certified_read_lane_references=refs,
          model_line_coverage=certified/total_lines if total_lines else UNKNOWN,
          model_read_line_coverage=certified/total_read_lines if total_read_lines else UNKNOWN,
          model_read_reference_coverage=refs/total_read_refs if total_read_refs else UNKNOWN,
          model_total_global_lines=total_lines,model_total_read_lines=total_read_lines,
          model_total_read_lane_references=total_read_refs,
          model_unresolved_opcodes=c['unresolved_opcodes'],model_exclusion_counts={k:v for k,v in counts.items() if not k.startswith('CERTIFIED_RO')},
          model_scope=c['scope'],model_manifest_sha256=c['manifest_sha256'],
          model_manifest_path=str(manifest),model_assumptions=c['closed_world_assumptions'],
          model_host_updates_excluded=m.get('host_updates_excluded',[]),
          model_evidence_qualification='INPUT_ONLY_NOT_HARDWARE_OR_RUNTIME_CERTIFICATION',
          native_blocked_UID_intersection=UNKNOWN,
          active_runtime_certified_lines=0,active_runtime_coverage=0)
        if not complete_model:row['readonly_evidence']='COMPLETE_INPUT_UNRESOLVED_EPOCH_ZERO_CERTIFIABLE_LINES_NOT_ZERO_OPPORTUNITY'
        reports.append({'workload':w,'trace':c['trace_content_sha256'],'candidate_path':str(root/'CANDIDATE.json'),
          'candidate_sha256':digest(root/'CANDIDATE.json'),'manifest_sha256':c['manifest_sha256'],
          'counts':counts,'scope':c['scope'],'model_complete':complete_model,'runtime_qualified':False,
          'source_driver_commit':r['driver_framework_commit'],'tool_commit':c['tool_source_commit'],
          'worker':r['worker_process'],'worker_exit':r['worker_exit_code'],
          'elapsed_seconds':r['elapsed_seconds'],'peak_RSS_bytes':r['peak_worker_RSS_bytes'],
          'peak_output_bytes':r['peak_output_bytes'],
          'final_bytes':sum(f.stat().st_size for f in root.rglob('*') if f.is_file()),
          'artifacts':files,'raw_artifact_hashes':m['artifacts'],'small_git_evidence':copied,
          'tool_tests_reused':c['tool_unit_tests'],
          'new_tool_tests':c.get('new_tool_unit_tests',21 if w=='convolutionSeparable' else UNKNOWN),
          'new_simulations':0,'new_native_tests':0})
    dump('SEVEN_INPUTS.json',index)
    table('INPUT_READONLY_COVERAGE.csv',[{k:(json.dumps(v,ensure_ascii=False) if isinstance(v,(list,dict)) else v) for k,v in r.items() if k not in ['commandlist_literal','capture_provenance','body_files']} for r in index['workloads']])
    dump('WHOLE_INPUT_ORACLE_INDEX.json',{'reports':reports,'scope':'TRACE_MODEL_CLOSED_WORLD',
      'seven_distinct_inputs_no_certificate_reuse':True,'native_qualified':False,
      'new_simulations':0,'worker_count':1,'production_resource_floor':'UNCHANGED',
      'actual_blocked_UID_overlap':'UNKNOWN for all inputs; not inferable from trace address counts'})
    print(json.dumps({'whole_inputs_completed':len(reports),'new_runtime_qualified':0,'new_app_starts':0}))

if __name__=='__main__':collect()
