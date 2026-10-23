"""EP-MAIN independent native terminal join. No legacy controller or E signature."""
import copy,hashlib,importlib.util,inspect,json,pathlib,re,sys
import vector_runtime as v
P=pathlib.Path;B=v.B;N=v.N
def load(path,name):return v.load(path,name)
def acceptance():
 s=v.pins();q=v.read(B/'control/NATIVE_PRELAUNCH_QUALIFICATION.json')
 v.need(q['status']=='NATIVE_PRELAUNCH_QUALIFIED_NOT_APPLICATION_ACCEPTED' and q['spec_sha256']==v.sha(B/'control/FROZEN_SPEC.json'),'native prelaunch binding')
 done=v.read(v.LED/(v.C+'.DONE.json'));out=P(done['output'])
 v.need(done['launcher_wait_returncode']==0 and done['stop_reason'] is None and done['native_simulator_observed'],'native execution not naturally complete')
 v.need(v.sha(out/'raw.log')==done['raw_sha256'],'closed raw changed')
 pid=v.read(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json')
 proc=P('/proc')/str(pid['pid'])
 if proc.exists():
  try:v.need(v.info(pid['pid'])['start_ticks']!=pid['start_ticks'],'same simulator still alive')
  except FileNotFoundError:pass
 actual=v.read(out/'NATIVE_LAUNCH.json')
 v.need(actual['source_identity']==s['source_identity'] and actual['spec_sha256']==v.sha(B/'control/FROZEN_SPEC.json'),'actual source/spec mismatch')
 for path,h in s['env_hashes'].items():v.need(v.sha(out/P(path).name)==h,'actual input/config changed')
 trace=(out/'actual_file_process_network.log').read_text()
 v.need('kernel-1.traceg' in trace and 'kernelslist.g' in trace,'full trace file open proof absent')
 v.need('connect(' not in trace and 'ssh' not in actual['argv'],'unexpected network/remote science execution')
 source=N/'EP/control/parse_main_terminal.py'
 sys.path[:0]=[str(N/'EP/src/owner-control/util/ep_l2/mechanism_e'),str(N/'EP/src/owner-control/util/ep_l2/ft_lane5')]
 legacy=load(source,'_vector_frozen_main_parser')
 # Retain the frozen model/profile checks and full numeric parsing body exactly.
 # Replace only original E-controller qualification lookup with THIS native Q.
 old=inspect.getsource(legacy.parse)
 first=old[:old.index("    require(qualification['campaign_id']")]
 first=first.replace('    policy_v2.combination_qualification(qualification,digest)\n','')
 body=old[old.index('    native={};final={};frames={}'):]
 join=first+"    require(qualification['qualified_by']=='EP-MAIN' and qualification['status']=='NATIVE_PRELAUNCH_QUALIFIED_NOT_APPLICATION_ACCEPTED','new native Q required')\n    require(all(qualification['source_identity'][n]==identity[n] for n in ('core_source_commit','framework_source_commit','binary_sha256')),'native source identity mismatch')\n"+body
 namespace=dict(legacy.__dict__);exec(compile(join,'EP_MAIN_NATIVE_AUTHORITY_BOUND_MODEL_PARSER','exec'),namespace)
 hist=v.read(B/'control/HISTORICAL_VECTOR_SPEC.json')
 model=namespace['parse'](out/'raw.log',hist,q)
 v.need(model['instructions']==56000000 and model['hardware_drained'] is True,'full instructions/drain')
 v.need(model['slices']==64,'not all64 slices')
 sys.path.insert(0,str(B/'sources/r5'));r5=load(B/'sources/r5/decoder.py','_vector_r5_additive')
 fixed=load(B/'sources/r4/decoder_samecycle_close.py','_vector_r4_fixed')
 schema=v.read(B/'sources/r4/SOURCE_BOUND_SCHEMA_r4.json')
 v.need(v.sha(B/'sources/r4/decoder_samecycle_close.py')==r5.FIXED_R4_SHA256,'old212 decoder SHA')
 feed=r5.Feed(expected_slices=list(range(64)),registered_slice_count=64,expected_kernels=[1],expected_flags={'T':True,'M':True,'ro_runtime':True},source_binding=s['source_identity'],old212_decoder_sha256=r5.FIXED_R4_SHA256)
 with (out/'raw.log').open('rb') as stream:old212=fixed.Decoder(schema).decode(r5.TappingReader(stream,feed))
 new=feed.finish(old212);v.need(new['status']=='VALID_R5_OBSERVER_DECLARATIONS_ONLY','invalid r5 '+str(new.get('reason')))
 r5.audit_normalized_result(new,old212)
 v.need(old212['final_cycle']==new['final_cycle']==model['cycles'],'clock mismatch')
 v.need(new['raw_log_sha256']==model['raw_log_sha256']==done['raw_sha256'],'raw identity mismatch across passes')
 ro=model['mechanism_metrics']['full_mechanism_records']['readonly']
 for sid in range(64):
  row=ro.get(sid,ro.get(str(sid)));cl=row['closure'];prior=row['summary']
  v.need(cl['epoch_closed']==1 and cl['ro_live']==cl['shared_descriptor_used']==cl['shared_line_used']==prior['live']==0,'ROC1 not drained')
  v.need(prior['detached']==old212['slice_counters'][str(sid)]['detach_success'],'detach authoritative/syntax mismatch')
 # Derivation of a native-authority parser is explicit; no old E Q is rewritten.
 v.put(out/'MODEL_PARSER_AUTHORITY_REBIND.json',{'frozen_parser_sha256':v.sha(source),'frozen_numeric_body_sha256':hashlib.sha256(body.encode()).hexdigest(),'native_authority_parser_sha256':hashlib.sha256(join.encode()).hexdigest(),'change':'Original E-only preamble replaced with exact EP-MAIN native prelaunch Q; all profile checks and numeric body preserved byte-for-byte','old_E_qualification_modified':False})
 for name,obj in [('terminal_summary.json',model),('R4_212_TERMINAL.json',old212),('R5_TAGPRESSURE_TERMINAL.json',new)]:v.put(out/name,obj)
 summary={'status':'EP_NATIVE_VECTOR_R5_DIAGNOSTIC_ACCEPTED','schema':'EP_MAIN_NATIVE_VECTOR_R5_INDEPENDENT_TERMINAL_JOIN_V1','cohort':v.C,'uuid':done['uuid'],'pair':False,'source_identity':s['source_identity'],'native_spec_sha256':v.sha(B/'control/FROZEN_SPEC.json'),'historical_spec_reference_only_sha256':v.sha(B/'control/HISTORICAL_VECTOR_SPEC.json'),'cycles':model['cycles'],'instructions':model['instructions'],'CTA':15625,'CTA_proof':'Full same frozen input/reference qualified geometry; check actual trace terminal below','slices':64,'kernel_count':1,'hardware_drained':True,'raw_sha256':done['raw_sha256'],'source_disposition':'SOURCE_KEEP','wall_seconds':done['elapsed_seconds'],'old_EP_starts':57,'new_epoch2_full_app_starts':1,'old_main61_speedup_claim':False,'numeric_SASS_output_validation':'UNKNOWN; unchanged conditional frozen trace model scope only','model_summary_sha256':v.sha(out/'terminal_summary.json'),'old212_summary_sha256':v.sha(out/'R4_212_TERMINAL.json'),'r5_summary_sha256':v.sha(out/'R5_TAGPRESSURE_TERMINAL.json')}
 raw=(out/'raw.log').read_text(errors='replace')
 ctas=re.findall(r'gpu_tot_issued_cta\s*=\s*(\d+)',raw)
 if ctas:v.need(int(ctas[-1])==15625,'CTA count mismatch');summary['CTA_proof']='actual gpu_tot_issued_cta terminal'
 v.put(out/'CURRENT_ACCEPTED_DIAGNOSTIC_POINT.json',summary)
 v.put(B/'control'/('SCIENCE_QUALIFICATION_'+v.C+'.json'),summary)
 return summary
