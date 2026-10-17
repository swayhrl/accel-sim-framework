"""Exact r2 certificate adapter plus independently bound native-byte semantics.

Reuses the frozen r17 native consumer and all of its identity/raw/body/64-slice
checks. Does not change a producer spec, certificate, trace, parser or ledger.
Unknown qualification/semantic schemas fail closed; output directory is new.
"""
import argparse,hashlib,importlib.util,json,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--workload',choices=['convolutionSeparable','FWT_7_21'],required=True);ap.add_argument('--output-dir',type=Path,required=True);args=ap.parse_args()
R=args.repo.resolve();P=args.output_dir.resolve();assert not P.exists();P.mkdir()
OLD=R/'docs/ep_l2/review_packs/FT20261017_LANE6_R17_SAD_INTAKE_r1'
s=importlib.util.spec_from_file_location('r18_frozen_engine',OLD/'intake_engine.py');e=importlib.util.module_from_spec(s);s.loader.exec_module(e);e.R=R;e.P=P
def write(name,data):e.write(name,data)
try:
 head=e.live_reader()(R);e.git('fetch','--no-tags','--no-recurse-submodules','origin',head)
 read=lambda path:e.git('show',head+':'+path)
 adapter=json.loads((OLD/'next_adapters'/(args.workload+'.json')).read_text());item=adapter['native_pairs'][0];pair=json.loads(read(item['pair_repository_path']+'/PAIR_RECEIPT.json'))
 paths={s['qualified_release'][s['qualified_release'].index('docs/ep_l2/'):] for s in pair['specs']};assert len(paths)==1
 path=paths.pop();assert path=='docs/ep_l2/codex_handoff/fast_track_2026_10_16_v1/lane5/R0_1_A1_B1_LEGACY_TRACE_INDEPENDENTLY_QUALIFIED_r2.json'
 qraw=read(path);q=json.loads(qraw);assert q['input_adapter_revision']['runtime_gates_source_binary_config_unchanged'] is True
 assert q['input_adapter_revision']['source_commit']=='98870b3d41cc216b0bb17820d8816a9312a78171'
 for spec,result in zip(pair['specs'],pair['results']):
  assert Path(spec['qualified_release']).read_bytes()==qraw
  assert result['audit']['qualified_release_sha256']==e.sha(qraw)
  proof=json.loads(Path(spec['atomic_input_scope']['path']).read_text())
  tool=e.git('show',proof['tooling_source_commit']+':util/ep_l2/ft_lane5/atomic_trace_scope.py');assert e.sha(tool)==proof['tool_sha256']==q['atomic_input_auditor_sha256']
 adapter['qualification_publication']=head;adapter['qualification_path']=path
 write('NATIVE_ADAPTER_SAD.json',adapter);write('native_pair_intake_v2a.py',(OLD/'native_pair_intake_v2a.py').read_bytes())
 write('validation/QUALIFICATION_ADAPTER.json',{'old_prepared_adapter':str((OLD/'next_adapters'/(args.workload+'.json')).relative_to(R)),'new_certificate_publication':head,'path':path,'sha256':e.sha(qraw),'reason':'Actual frozen input audit uses the official legacy r2 certificate; no scope/source/binary/config change'})
 e.receive()
 evidence=json.loads((P/'SAD_NATIVE_INTAKE.json').read_text());authority=evidence['current_authority'];read=lambda path:e.git('show',authority['publication_commit']+':'+path)
 report_path='docs/ep_l2/review_packs/FT20261017_LANE5_R17_NATIVE_BYTE_SEMANTIC_PROOF_r1/NATIVE_LEGACY_BYTE_SEMANTIC_PROOF_R17_r1.json'
 raw=read(report_path);report=json.loads(raw)
 assert e.sha(raw)=='9b62884190b8f6bd77d3b3bf873d0e3e60ce718db9e7c51a9797ec99bd46dce2'
 assert report['schema_version']=='EPL2_NATIVE_ZERO_MASK_SOURCE_AND_FULL_BYTES_PROOF_V1' and report['status']=='PASS_FULL_NATIVE_BYTE_AND_ZERO_MASK_SEMANTIC_PROOF'
 assert e.sha(e.git('show',report['tooling_source_commit']+':util/ep_l2/ft_lane5/native_legacy_trace_proof.py'))==report['tool_sha256']
 identity=pair['specs'][0]['identity'];assert report['source_identity']=={k:identity[k] for k in report['source_identity']}
 bindings=[]
 for path,digest in report['native_framework_files_sha256'].items():
  source=e.git('show',identity['framework_source_commit']+':'+path);assert e.sha(source)==digest;bindings.append({'commit':identity['framework_source_commit'],'path':path,'sha256':digest})
 core=R.parent/'gpgpu-sim-ep-l2-ft20261016-lane1-r0-1';source=subprocess.check_output(['git','-C',str(core),'show',identity['core_source_commit']+':src/abstract_hardware_model.cc']);assert e.sha(source)==report['core_memory_generator_sha256'];assert b'if (m_warp_active_mask.count() == 0) return;' in source
 rows=[r for r in report['workloads'] if r['workload']==args.workload];assert len(rows)==1;row=rows[0];assert row['status']=='FULL_ORIGINAL_BYTES_AND_NATIVE_ZERO_MASK_SEMANTICS_PROVEN'
 for spec,result in zip(pair['specs'],pair['results']):
  expected=sorted([{k:f[k] for k in ('name','bytes','sha256')} for f in row['files']],key=lambda r:r['name'])
  assert expected==[r for r in result['audit']['traces'] if r['name']!=spec['entry_trace_name']]
  assert sum(f['all_active_lane_records'] for f in row['files'])==result['summary']['instructions']
 assert e.live_reader()(R)==authority['publication_commit']
 write('validation/NATIVE_BYTE_SEMANTIC_REPORT.json',raw)
 write('validation/LEGACY_R2_EXTRA_CLOSURE.json',{'status':'PASS','authority':authority,'report_path':report_path,'report_sha256':e.sha(raw),'report_tooling_source':report['tooling_source_commit'],'Framework_source_bindings':bindings,'Core_memory_generator_sha256':report['core_memory_generator_sha256'],'complete_body_hashes_independently_rehashed':True,'native_terminal_parser_reparsed':True,'full_original_records_retained':True,'new_numeric_SASS_scope':False,'producer_or_ledger_mutations':0})
 write('INTAKE_RECEIPT.json',{'status':'PASS_COMPLETE_NATIVE_V2_R2_SEMANTIC_INTAKE','workload':args.workload,'authority':authority,'qualification_sha256':e.sha(qraw),'new_simulators':0})
 print(json.dumps({'workload':args.workload,'status':'PASS_COMPLETE_NATIVE_V2_R2_SEMANTIC_INTAKE'}))
except BaseException as error:
 write('FAILURE.json',{'status':'FAIL_CLOSED','type':type(error).__name__,'reason':str(error),'workload':args.workload});raise
