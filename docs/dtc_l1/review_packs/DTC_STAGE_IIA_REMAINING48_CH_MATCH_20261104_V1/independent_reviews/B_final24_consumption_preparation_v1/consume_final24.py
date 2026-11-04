"""Root-invoked once after qualified all48terminal. No model/controller/Git actions."""
from pathlib import Path
import argparse,json,gzip,hashlib,subprocess,sys,resource,datetime,collections,re
from final24_output_utils import ChunkedJSONL,require_final_provider,selector_index,phase_fold,complete_phase,PUBLISHED_MEMBER_LIMIT
D=Path(__file__).resolve().parent

def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb')as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def put(p,v):Path(p).write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
def load_verified_provider(path):
 b=Path(path).read_bytes();p=json.loads(b);require_final_provider(p);mb=Path(p['manifest']['path']).read_bytes();assert hashlib.sha256(mb).hexdigest()==p['manifest']['sha256'];mf=json.loads(mb);assert mf['source_qualified']is True
 for x in p['files']:assert sha(x['path'])==x['sha256']
 f=next(x for x in p['files']if'CORE32_RESULTS.json.gz'in x['name']);core=json.load(gzip.open(f['path'],'rt'));return b,p,core

def process_extracted(extracted,core,out,selectors,trace_overlay):
 detail=ChunkedJSONL(out/'public/details','kernels');metadata=ChunkedJSONL(out/'public/details','source_metadata');commands=ChunkedJSONL(out/'public/details','commands');phases_out=ChunkedJSONL(out/'public/details','phase_summaries');cycles_out=ChunkedJSONL(out/'public/details','six_cell_kernel_cycles');phase_buckets={};cycle_rows={};source_counts={};source_summaries=[]
 for r in extracted['rows']:
  digest=r['input_digest'];cell=r['cell'];profile=r['profile'];source_id=r['RESULT_sha256'];source_counts.setdefault(digest,{})[cell+'_'+profile]=r['kernel_count'];src={k:v for k,v in r.items()if k not in ['kernels','runtime_commands','expected_commands','effective_options']};src['effective_options_sha256']=hashlib.sha256(json.dumps(r['effective_options'],sort_keys=True,separators=(',',':')).encode()).hexdigest();src['scope']='Raw-derived selected final cumulative metrics; source identity stays original/new role. Gauge/peak/mean snapshots not differenced.';src['active_frontend_domain']='CH_COMMON_PAPER_BASE_PIB256'if cell=='CH'else'DH_PAPER_OO_PIB128_GENERIC8_INACTIVE';metadata.write(src);source_summaries.append({k:r[k]for k in ['program','input_digest','cell','profile','source_role','RESULT_path','RESULT_sha256','cycles','kernel_count','kernel_scope']})
  for ev in r['runtime_commands']:commands.write({'source_RESULT_sha256':source_id,'input_digest':digest,'cell':cell,'profile':profile,**ev})
  for k in r['kernels']:
   ordinal=k['ordinal'];symbol=k['kernel'];phase=selectors.get(digest,{}).get(ordinal)
   if phase is None:
    if digest in selectors:raise ValueError('FIXED_PHASE_SELECTOR_GAP')
    phase={'phase_id':'TRACE_SYMBOL::'+symbol,'source_stage':symbol,'phase_evidence':'TRACE_SYMBOL_ONLY_NOT_SOURCE_PHASE_CERTIFIED'}
   overlay=trace_overlay.get((digest,ordinal));trace=None
   if overlay:
    assert overlay['symbol']==symbol and overlay['active_thread_instructions']==k['instructions'];trace={x:overlay.get(x)for x in ['kernel_ordinal','symbol','complete_CTAs','trace_file','trace_sha256','source_phase','accepted_ODE_step_or_adaptive_attempt_id']};trace['3DCONV_scalar_i']=None
   detail.write({'source_RESULT_sha256':source_id,'input_digest':digest,'actual_design':cell,'actual_profile':profile,'phase_candidate':phase,'fixed_trace_overlay':trace,**k})
   key=(digest,cell,profile,phase['phase_id']);b=phase_buckets.setdefault(key,{'program':r['program'],'input_digest':digest,'cell':cell,'profile':profile,'phase':phase,'kernel_count':0,'cycles_sum':0,'additive':{}});phase_fold(b,k)
   ck=(digest,ordinal);cr=cycle_rows.setdefault(ck,{'program':r['program'],'input_digest':digest,'trace_ordinal':ordinal,'kernel':symbol,'instructions':k['instructions'],'candidate_phase':phase,'cycles':{},'myocyte_accepted_ODE_step_or_attempt_id':None,'3DCONV_scalar_i':None});assert cr['kernel']==symbol and cr['instructions']==k['instructions'];cr['cycles'][cell+'_'+profile]=k['cycles']
 for k in sorted(phase_buckets):
  b=phase_buckets[k];phases_out.write({key:b[key]for key in ['program','input_digest','cell','profile','phase']}|complete_phase(b))
 for key in sorted(cycle_rows):
  row=cycle_rows[key]
  for c in ['CH','DH']:
   for p in ['P0','F128','F256']:row['cycles'].setdefault(c+'_'+p,None)
  cycles_out.write(row)
 parts=[]
 for w in [detail,metadata,commands,phases_out,cycles_out]:parts.extend(w.close())
 return source_summaries,source_counts,parts

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--provider',type=Path,required=True);ap.add_argument('--output-dir',type=Path,required=True);args=ap.parse_args();pb,provider,core=load_verified_provider(args.provider) # gate before output creation or any raw parse
 out=args.output_dir.resolve();assert out.is_relative_to((D/'updates').resolve())and not out.exists();out.mkdir(parents=True,exist_ok=False);(out/'private').mkdir();(out/'public').mkdir();(out/'private/CAPTURED_PROVIDER.json').write_bytes(pb)
 contract=json.loads((D/'FINAL24_CONSUMPTION_CONTRACT.json').read_bytes());assert sha(D/'final24_derived_parser.py')==contract['derived_parser']['sha256'];assert sha(D/'final24_output_utils.py')==contract['output_utils']['sha256'];counts=json.loads((D/'FIXED24_INPUT_COUNTS.json').read_bytes());expected={x['input_digest']:x['expected']['kernels']for x in counts['programs']};mapping=json.loads((D/'LONGTAIL_PHASE_SELECTORS.json').read_bytes());assert sha(mapping['source_manifest']['path'])==mapping['source_manifest']['sha256'];assert sha(mapping['trace_sequence']['path'])==mapping['trace_sequence']['sha256'];selectors=selector_index(mapping,expected);overlay={ (x['input_digest'],x['kernel_ordinal']):x for x in json.load(gzip.open(mapping['trace_sequence']['path'],'rt'))['rows']}
 limit=6*1024**3;soft,hard=resource.getrlimit(resource.RLIMIT_AS);resource.setrlimit(resource.RLIMIT_AS,(min(limit,hard)if hard!=resource.RLIM_INFINITY else limit,min(limit,hard)if hard!=resource.RLIM_INFINITY else limit)) # own process and parser child only, never any model
 parsed=out/'private/extraction';log=out/'private/PARSER_STDOUT.log'
 with log.open('wb')as f:res=subprocess.run([sys.executable,'-B',str(D/'final24_derived_parser.py'),'--provider',str(out/'private/CAPTURED_PROVIDER.json'),'--output-dir',str(parsed)],stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT)
 if res.returncode:
  put(out/'public/ANALYSIS_HOLD.json',{'status':'FINAL24_COUNTER_EXTRACTION_HOLD','parser_exit':res.returncode,'log_private':str(log),'scientific_results_not_changed':True,'do_not_drop_programs_or_rerun_models':True});raise RuntimeError('PARSER_HOLD; inspect private log. No partial mechanism completion claimed.')
 extracted=json.load(gzip.open(parsed/'CLOSED_SOURCE_KERNEL_COUNTERS.json.gz','rt'));source_summary,observed,parts=process_extracted(extracted,core,out,selectors,overlay)
 programs=[r for r in core['all_programs']if r['population_origin']=='AUTHORIZED_REMAINING24'];assert len(programs)==24 and {r['input_digest']for r in programs}==set(expected)
 for program in programs:
  for c in ['CH','DH']:
   for p in ['P0','F128','F256']:
    cell=program['six_source_cells'][c+'_'+p]
    if cell['accepted']:assert observed[program['input_digest']][c+'_'+p]==expected[program['input_digest']]
 assert sum(sum(v.values())for v in observed.values())<=43524
 compact=[{'program':p['program'],'suite':p['suite'],'input_digest':p['input_digest'],'six_source_cells':p['six_source_cells'],'metrics_by_profile':p['metrics_by_profile'],'common_both_F_accepted':p['common_both_F_accepted'],'mechanism_kernel_counts':observed.get(p['input_digest'],{})}for p in programs];put(out/'public/PROGRAM_SUMMARY.json',{'programs':compact,'accepted_source_rows':source_summary,'negative_cells_remain_null_not_missing_workloads':True,'phase_and_counter_boundaries':contract['counter_rules']})
 first8=json.loads((D/'FIRST8_REVIEWED_EVIDENCE_INDEX.json').read_bytes());put(out/'public/CORE32_MECHANISM_EVIDENCE_INDEX.json',{'first8_reviewed_evidence':first8,'remaining24':'PROGRAM_SUMMARY.json and details/*','upstream_CORE32_quantitative_provider':{'observed_utc':provider['observed_utc'],'snapshot_manifest':provider['manifest'],'core32_common_both_F_n':provider['summary']['core32_common_both_F_n']},'unified_source_identity':'Actual source_profile/cohort/UUID/SHA, including inherited P0 aliases; comparison context is not identity.','no_phase_or_counter_coverage_promotion':True})
 put(out/'public/SOURCE_AND_COMPLETION_RECEIPT.json',{'captured_provider_sha256':hashlib.sha256(pb).hexdigest(),'upstream_provider_manifest':provider['manifest'],'all48terminal':True,'new48_accepted':provider['summary']['accepted_CH'],'new48_archived_negative':provider['summary']['archived_negative_CH'],'fixed24_input_n':24,'parsed_accepted_source_n':len(source_summary),'parsed_kernel_records':sum(sum(v.values())for v in observed.values()),'max_kernel_records_if_all_accepted':43524,'analysis_own_RLIMIT_AS_bytes':limit,'live_raw_consumed':False,'new_model_starts':0,'native_scientific_writes':0})
 files=[]
 for p in sorted((out/'public').rglob('*')):
  if p.is_file():
   assert p.stat().st_size<PUBLISHED_MEMBER_LIMIT;files.append({'path':str(p.relative_to(out)),'bytes':p.stat().st_size,'sha256':sha(p)})
 put(out/'MANIFEST.json',{'schema':'DTC_REMAINING24_FINAL_CLOSED_MECHANISM_ARTIFACTS_V1','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':files,'private_staging_excluded':True,'each_published_member_lt8MiB':True,'upstream_performance_statuses_not_modified':True,'new_models_or_runtime_actions':0});assert(out/'MANIFEST.json').stat().st_size<PUBLISHED_MEMBER_LIMIT;print(json.dumps({'status':'FINAL24_READONLY_CONSUMPTION_COMPLETE','manifest':str(out/'MANIFEST.json'),'manifest_sha256':sha(out/'MANIFEST.json'),'programs':24,'accepted_sources':len(source_summary),'kernel_records':sum(sum(v.values())for v in observed.values())}))
if __name__=='__main__':main()
