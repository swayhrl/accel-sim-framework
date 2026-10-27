
#!/usr/bin/env python3
"""Incremental CPU-only actual SM89 consumer check.
Accept a completed asset directory containing ASSET.json and traces/kernelslist.g.
Replay the first complete CTA from every kernel with fixed private consumer/core
and byte-pinned SM89 configs; output must be an absent NAS traces directory.
This does not qualify unselected CTAs, numerical outputs, arbitrary CFI or hardware.
"""
import argparse,pathlib,json,lzma,sys,hashlib
import batch_core_fix as m
P=pathlib.Path;D=P(__file__).resolve().parent
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--asset-dir',type=P,required=True);ap.add_argument('--output',type=P,required=True);a=ap.parse_args()
 pins=m.read(D/'LAUNCHER_PINS.json');root=P(pins['NAS_output_root']).resolve();out=a.output.resolve()
 if out==root or root not in out.parents or out.exists():raise RuntimeError('output must be an absent child of NAS traces root')
 obj=a.asset_dir.resolve();meta=m.read(obj/'ASSET.json')
 if not(obj/'traces/kernelslist.g').is_file():raise RuntimeError('no grouped trace index; capture/CPU POST must finish first')
 for p in [pins['binary'],pins['core']]+pins['configs']:
  if m.sha(P(p['path']))!=p['sha256']:raise RuntimeError('frozen consumer/core/config hash drift')
 m.OUT=out;out.mkdir(parents=True);m.SAMPLES=out/'samples';m.SAMPLES.mkdir();m.RUNS=out/'runs';m.RUNS.mkdir()
 m.BIN=P(pins['binary']['path']);m.CFG=[P(p['path'])for p in pins['configs']]
 m.consumer.update(binary=str(m.BIN),binary_sha256=pins['binary']['sha256'],config_sha256={p['path']:p['sha256']for p in pins['configs']},core_library=pins['core'],source_build=str(D/'frozen_v3/SOURCE_BUILD_V3.json'),core_build=str(D/'private_core_v1/SOURCE_BUILD.json'),launcher_proc_map_witness=str(D/'launcher_actual_nasconfig_v2/ACTUAL_PROCESS_CORE_MAP.json'))
 row=m.prepare({'asset_id':meta['asset_id'],'object_path':str(obj)},meta.get('kind','UNKNOWN'))
 row['qid']=meta.get('source_queue_id',meta.get('qid','UNKNOWN_NOT_PRESENT'));row['source_KEEP']=True;row['release_bytes']=0;row['hardware_performance_scientific_numerical_qualification']=False
 # The selected executed path is checked, including explicit CALL/RET exclusion.
 cfi=0
 for f in row['selected_files']:
  for line in lzma.open(f['sample'],'rt'):
   if ' ADA'in line:
    a=line.split();cfi+=a[3+int(a[2])].split('.')[0]in('CALL','RET')
 row['executed_CALL_RET_selected_records']=cfi
 if cfi:
  row['status']='UNQUALIFIED_EXECUTED_CALL_RET_TARGET_SEMANTICS';row['actual_result']=None
 else:
  r=m.run(row);row['actual_result']=r;row['status']=('PASS_ALL_ASSET_RECORDS_FUNCTIONAL'if row['coverage']=='ENTIRE_ASSET_SOURCE_RECORDS'else'PASS_FIRST_CTA_PER_KERNEL_FUNCTIONAL')if r['status']=='PASS'else'ACTUAL_SIM_FAILED_OR_BOUNDED_INCOMPLETE'
 row['full_record_functional_replay_qualified']=row['status']=='PASS_ALL_ASSET_RECORDS_FUNCTIONAL';row.pop('full_job_qualified',None)
 m.write(out/'INCREMENTAL_RESULT.json',row)
 print(json.dumps({'asset_id':row['asset_id'],'status':row['status'],'coverage':row['coverage'],'result':str(out/'INCREMENTAL_RESULT.json'),'no_numerical_performance_scientific_qualification':True},indent=2))
 return 0 if row['status'].startswith('PASS_')else 2
if __name__=='__main__':
 try:sys.exit(main())
 except Exception as e:print(json.dumps({'status':'PRECONDITION_OR_CHECK_FAILURE','error':str(e)}),file=sys.stderr);sys.exit(2)
