"""Existing native terminal review and V2 payload, extended to one local endpoint."""
import argparse,json,shutil,subprocess
from pathlib import Path
from registry import Registry,write_json,PARALLEL
from run import digest,require
from acceptance import load_current_authority,current_manifest
from review_r0_1_pair import review
from package_r0 import freeze_checksums
from headroom_metrics import analyze

REPO=Path(__file__).resolve().parents[3]


def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--spec',type=Path,required=True);p.add_argument('--pack',type=Path,required=True);a=p.parse_args();spec=json.loads(a.spec.read_text());require(spec.get('scientific_scope') in ('LOCAL_IDEAL_NATIVE_V1','UNIFIED_NATIVE_V1','ALL_DATA_REFERENCE_V1') and spec['experiment_id']==PARALLEL,'Unqualified endpoint scope');require(not a.pack.exists(),'Preserve old endpoint revision')
 state=load_current_authority();ledger=current_manifest(state);r=Registry();lease=r.build_lease('lane5',cpu=1,memory=2*2**30)
 try:
  snapshot=r.snapshot();result,directory=review(spec,snapshot);require(not any(x['run_key']==result['run_key'] for x in ledger['rows']),'Previously accepted endpoint')
  a.pack.mkdir();arm=a.pack/spec['mode'];arm.mkdir()
  for name in ['input_spec.json','input_audit.json','run_status.json','terminal_summary.json','raw.log']:shutil.copyfile(directory/name,arm/name)
  identity=spec['identity'];row={'run_key':result['run_key'],'identity':identity,**{k:identity[k] for k in ['core_source_commit','framework_source_commit','binary_sha256','runtime_config_sha256','trace_content_sha256','workload']},'mode':spec['mode'],'experiment_id':PARALLEL,'regime':'H0','profile':spec['profile'],'cell_id':spec['cell_id'],'scientific_scope':spec['scientific_scope'],'scientific_acceptance':'CURRENT_ACCEPTED','original_terminal_status':'COMPLETE_VALID','raw_log_sha256':result['raw_log_sha256'],'observed_cycles':result['summary']['cycles'],'instructions':result['summary']['instructions']}
  source={'mode':spec['mode'],'profile':spec['profile'],'identity':identity,'run_key':result['run_key'],'qualification_sha256':result['audit']['qualified_release_sha256'],'atomic_input_scope':spec['atomic_input_scope'],'input_audit':result['audit'],'hardware_terminal':result['summary'],'registry_terminal':snapshot['runs'][result['run_key']]};write_json(a.pack/'SOURCE_MANIFEST.json',{'runs':[source]})
  write_json(a.pack/'SCIENTIFIC_REVIEW.json',{'status':'INDEPENDENT_TERMINAL_AND_CURRENT_AUTHORITY_REVIEW_PASS','diagnostic_kind':'LOCAL_IDEAL_SINGLE' if spec['scientific_scope']=='LOCAL_IDEAL_NATIVE_V1' else 'SCOPED_SINGLE','experiment_id':PARALLEL,'regime':'H0','profile':spec['profile'],'cell_id':spec['cell_id'],'workload':identity['workload'],'scientific_acceptance_rows_proposed':[row],'checked_current_authority':state['binding'],'independent_review_resource_lease':lease,'scope':('Full native input/source/binary/config and original-instruction/access/reference/store/UID/snapshot/drain; physical bypassed structuresN/A, same-binary OFF only, no EP-L2 speedup or numericSASS' if spec['scientific_scope']=='ALL_DATA_REFERENCE_V1' else 'Full native input/source/binary/config, actual64slice physical/reference closure; explicit finite/local profile, same-binary OFF only. Not an EP-L2 pair or system ALL_DATA endpoint.')})
  baselines=[v for v in ledger['rows'] if v.get('profile')=='B16_OFF' and v['scientific_acceptance']=='CURRENT_ACCEPTED' and all(v['identity'][k]==identity[k] for k in ['core_source_commit','framework_source_commit','binary_sha256','trace_content_sha256','workload','epoch_range','termination_contract'])]
  comparison={'kind':'ALL_DATA_REFERENCE_ENDPOINT' if spec['scientific_scope']=='ALL_DATA_REFERENCE_V1' else 'FINITE_OR_LOCAL_ENDPOINT','profile':spec['profile'],'cycles':row['observed_cycles'],'instructions':row['instructions'],'same_binary_OFF':None,'OFF_over_endpoint':None,'EP_L2_speedup':None,'geomean':None,'diagnostic_only':True}
  if spec['profile']!='B16_OFF':
   require(len(baselines)==1 and baselines[0]['instructions']==row['instructions'],'Exact accepted same-binary/input OFF anchor missing');b=baselines[0];comparison.update(same_binary_OFF={'run_key':b['run_key'],'cycles':b['observed_cycles']},OFF_over_endpoint=b['observed_cycles']/row['observed_cycles'])
  write_json(a.pack/'COMPARISON.json',comparison)
  # Reuse the existing physical downstream observer; never rename it ALL_DATA.
  write_json(a.pack/'PRESSURE.json',analyze(directory) if spec['scientific_scope']!='ALL_DATA_REFERENCE_V1' else {'scope':'ALL_DATA_REFERENCE_V1','physical_data_WB_cache_DRAM':'NOT_APPLICABLE','reference':result['summary']['reference_terminal'],'instruction_fetch':'NATIVE_UNCHANGED'});write_json(a.pack/'RAW_LOG_INDEX.json',[{'path':str(directory/'raw.log'),'sha256':row['raw_log_sha256'],'run_key':row['run_key']}]);freeze_checksums(a.pack)
 finally:r.release_build(lease,'lane5')
 print(json.dumps({'status':'INDEPENDENT_LOCAL_ENDPOINT_REVIEW_PASS','profile':spec['profile'],'cycles':row['observed_cycles'],'pack':str(a.pack)}))
if __name__=='__main__':main()
