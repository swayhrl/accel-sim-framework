"""Independent complete finite-matrix consumer, including unaccepted attempts.

Never launches, refunds, deletes or qualifies a failed model as performance.
Requires the actual native batch closure; incomplete live cohorts cannot pass.
"""
import pathlib,json,hashlib,importlib.util,subprocess,datetime,collections
from fractions import Fraction
P=pathlib.Path;T=P('/root/data/dtc_main_v100_sweep_20261025_v1');N=P('/root/data/ep_l2_dtc_l1_native_v2');REQ='DTC_AE_V100_FULL_SWEEP_20261025_V1';ARMS={'CM','CH','DM','DH'}
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def load(name,file):
 s=importlib.util.spec_from_file_location(name,T/'tools'/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def comparison(key,aliases,rows):
 cycles={c:rows[c]['cycles'] for c in ARMS};c=Fraction(cycles['CM'],cycles['CH']);d=Fraction(cycles['DM'],cycles['DH']);interaction=d/c
 return {'input_digest':key,'program':aliases[0]['program'],'suite':aliases[0]['suite'],'bundle_aliases':[r['bundle_id'] for r in aliases],'cycles':cycles,'C_speedup':float(c),'D_speedup':float(d),'C_cycle_reduction':float(1-1/c),'D_cycle_reduction':float(1-1/d),'R':float(interaction),'exact_fractions':{'C':str(c),'D':str(d),'R':str(interaction)}}
def incomplete(key,aliases,rows,failed):
 pairs={}
 for family,off,on in [('C','CM','CH'),('D','DM','DH')]:
  if off in rows and on in rows:
   speedup=Fraction(rows[off]['cycles'],rows[on]['cycles']);pairs[family]={'OFF_cycles':rows[off]['cycles'],'ON_cycles':rows[on]['cycles'],'exact_speedup':str(speedup),'speedup':float(speedup),'cycle_reduction':float(1-1/speedup),'scope':'Only this fully accepted within-design pair;four-cell interaction unavailable'}
 return {'status':'FOUR_ATTEMPTS_CLOSED_NO_COMPLETE_COMPARISON','input_digest':key,'program':aliases[0]['program'],'suite':aliases[0]['suite'],'bundle_aliases':[r['bundle_id'] for r in aliases],'accepted_complete_arms':{c:{'cohort':p['cohort'],'uuid':p['uuid'],'cycles':p['cycles']} for c,p in rows.items()},'failed_unaccepted_arms':{c:{'cohort':p['cohort'],'uuid':p['uuid'],'cycles':None,'classification':p['failure_classification']} for c,p in failed.items()},'available_within_design_pairs':pairs,'R':None,'omission_from_full_comparison_is_explicit_not_zero_or_negative_gain':True}
def main():
 closed=read(T/'analysis/BATCH_NATIVE_CLOSED.json');assert closed['state']=='ALL_APPLICABLE_NATIVE_ATTEMPTS_CLOSED_ARCHIVED_RESTORED_WITH_CLASSIFIED_FAILURES'
 native=load('complete_consumer_native','sweep_native_cap1m.py');strict=load('complete_consumer_strict','sweep_strict_cap1m.py');outbox=load('complete_consumer_outbox','sweep_outbox.py');failure=load('complete_consumer_failure','sweep_failure_review_telemetry_v1.py');profiles=load('complete_consumer_operational_profiles','sweep_runtime_provenance_v5.py')
 reg,epoch=native.read_current_authority();q=reg['registered_future_requests'][REQ];profile_binding=profiles.bind(q,native);host_profiles=load('complete_consumer_host_profiles','sweep_host_provenance_v2.py');host_binding=host_profiles.bind(q)
 assert q['state']=='ALL_STARTS_CLOSED_PENDING_COMPLETE_SCIENTIFIC_DELIVERY' and q['remaining']==0 and q['budget']==356
 assert q['controller_sha256']==sha(T/'tools/sweep_native.py') and q['strict_sha256']==sha(T/'tools/sweep_strict.py') and q['outbox_sha256']==sha(T/'tools/sweep_outbox.py')
 assert q['spec_request_sha256']==sha(T/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json')
 assert not read(T/'control/POOL_DISPATCH_RESERVATIONS.json')['claims']
 for p in (T/'control').glob('CONTROLLER_LAUNCH_R*.json'):
  launch=read(p);proc=P('/proc')/str(launch['pid'])
  if proc.exists():assert int((proc/'stat').read_text().rsplit(')',1)[1].split()[19])!=launch['start_ticks'],'controller generation still live'
 before=read(T/'control/REGISTRY_AT_INSTALL.json')
 assert all(reg['registered_future_requests'][key]==row for key,row in before['registered_future_requests'].items())
 assert reg['old_source_history']==before['old_source_history'] and reg['qualification_history']==before['qualification_history']
 body=read(T/'analysis/BODY_QUALIFICATION_PROGRESS.json');assert body['closed']==body['total_unique']==89 and body['state']=='ALL_FINITE_BODY_QUALIFICATIONS_CLOSED'
 assert len(q['consumed'])+len(q['sealed'])==q['budget'] and len(set(q['sealed']))==len(q['sealed']);assert not set(q['consumed'])&set(q['sealed'])
 grouped={}
 for r in read(T/'control/INTAKE_CANDIDATES.json')['inputs']:grouped.setdefault(r['input_digest'],[]).append(r)
 assert set(grouped)=={r['input_digest'] for r in body['rows']} and len(body['rows'])==89
 input_reader=load('complete_consumer_actual_input_SHA_reader','sweep_input_sha_replay_v1.py');input_sha_session=input_reader.start_session(native)
 points=[];failures=[];uuids=set();archive_entries=0;checked_inputs={};attempt_arms=collections.defaultdict(set)
 for cell,row in q['consumed'].items():
  assert row['uuid'] not in uuids;uuids.add(row['uuid'])
  intentfile=T/'control/qualification_ledger'/(cell+'.INTENT.json');intent=read(intentfile);done=read(intentfile.with_name(cell+'.DONE.json'));out=P(intent['output'])
  assert sha(intentfile)==row['intent_sha256'] and done==row['execution_receipt'] and done==read(out/'NATIVE_EXIT.json') and intent['uuid']==row['uuid']==done['uuid']
  spec=native.spec_for(cell);key=spec['input_digest'];assert key in q['admitted_inputs'] and spec['cell'] not in attempt_arms[key];attempt_arms[key].add(spec['cell'])
  if key not in checked_inputs:checked_inputs[key]=input_reader.replay(spec,native,input_sha_session)
  receipt=read(T/'control'/(cell+'_ARCHIVE_RECEIPT.json'));assert receipt['status']=='ARCHIVE_VERIFIED_AND_RESTORE_VERIFIED_NATIVE_TARGET'
  bundle=P(receipt['target_mount_path']);manifest=outbox.manifest_for(cell);assert manifest==read(bundle/'SOURCE_MANIFEST.json')
  f,v=outbox.libraries(bundle);index=f.verify_archive(bundle,manifest);proof=f.check_native(P(receipt['native_restore']),manifest)
  assert len(proof)==len(manifest['entries']) and index['archive_sha256']==receipt['archive_sha256'];archive_entries+=len(proof)
  result=read(T/'analysis'/(cell+'.RESULT.json'));assert result['uuid']==row['uuid']
  profile_proof=profiles.verify(cell,profile_binding,native);host_proof=host_profiles.verify(cell,host_binding,native)
  common={'host_execution_profile':host_proof,'operational_profile':profile_proof,'cohort':cell,'input_digest':key,'cell':spec['cell'],'program':spec['program'],'suite':spec['suite'],'uuid':row['uuid'],'raw_compressed_sha256':done['raw_sha256'],'raw_uncompressed_sha256':done['raw_uncompressed_sha256'],'spec_sha256':profile_proof['selected_spec_sha256'],'original_spec_sha256':profile_proof['original_spec_sha256'],'selected_spec_path':profile_proof['selected_spec_path'],'strict_parser_source_sha256':q['strict_sha256'] if cell in profile_binding['old_cells'] else profile_binding['profile']['strict_sha256'],'intent_sha256':sha(intentfile),'done_sha256':sha(intentfile.with_name(cell+'.DONE.json')),'elapsed_seconds_diagnostic_only':done['elapsed_seconds'],'archive':receipt,'all_restore_entries_rechecked':len(proof),'native_values':'UNPROVEN','PPA':'UNPROVEN'}
  if result['state']=='PASS_STRICT_ARCHIVE_NATIVE_RESTORE':
   assert receipt['scientific_status']=='AEFAIR_SCIENCE_QUALIFIED';stored=read(out/'AEFAIR_STRICT.json');assert strict.terminal(cell)==stored
   point=dict(common,status='PASS_STRICT_ARCHIVE_NATIVE_RESTORE',cycles=stored['cycles'],instructions=stored['instructions'],CTA=stored['CTA'],kernels=stored['kernel_count'],per_kernel=stored['kernels'],strict_sha256=sha(out/'AEFAIR_STRICT.json'),full_independent_strict_replayed=True);points.append(point)
  else:
   assert result['state']=='FAIL_CLOSED_UNACCEPTED_ARCHIVED_NO_RETRY' and receipt['scientific_status']=='STOP_UNACCEPTED'
   classificationfile=T/'analysis'/(cell+'.FAILURE_CLASSIFICATION_R5.json');assert classificationfile.exists();classification=failure.classify(cell)
   assert classification==result['failure_classification'] and classification['accepted_cycles'] is None and not (out/'AEFAIR_STRICT.json').exists()
   assert cell in closed['closed_unaccepted_points'];failures.append(dict(common,status=classification['status'],cycles=None,failure_classification=classification,failure_classification_sha256=sha(classificationfile),full_independent_failure_replayed=True))
 assert {p.name for p in (T/'DTC/run/results').iterdir()}==uuids and len(points)+len(failures)==len(q['consumed'])
 assert set(attempt_arms)==set(q['admitted_inputs']) and all(arms==ARMS for arms in attempt_arms.values()),'an original applicable input has unattempted cells'
 assert set(closed['closed_unaccepted_points'])=={p['cohort'] for p in failures}
 comparisons=[];unrun=[];unpaired=[];expected_sealed=set()
 for key,aliases in grouped.items():
  rows={p['cell']:p for p in points if p['input_digest']==key};bad={p['cell']:p for p in failures if p['input_digest']==key}
  if not rows and not bad:
   assert key in closed['input_holds'] and key not in q['admitted_inputs'];unrun.append({'input_digest':key,'program':aliases[0]['program'],'suite':aliases[0]['suite'],'bundle_aliases':[r['bundle_id'] for r in aliases],'hold':closed['input_holds'][key]});expected_sealed.update('E2-AEV100-'+key[:16]+'-'+c for c in ARMS);continue
  assert set(rows)|set(bad)==ARMS and not set(rows)&set(bad)
  if bad:unpaired.append(incomplete(key,aliases,rows,bad))
  else:
   paired=comparison(key,aliases,rows);paired['per_arm_runtime_profiles']={c:r['operational_profile']['operational_resource_profile'] for c,r in rows.items()};paired['within_design_observational_revision_mixed']={'C':rows['CM']['operational_profile']['binary_sha256']!=rows['CH']['operational_profile']['binary_sha256'],'D':rows['DM']['operational_profile']['binary_sha256']!=rows['DH']['operational_profile']['binary_sha256']};comparisons.append(paired)
 assert expected_sealed==set(q['sealed']) and set(closed['input_holds'])=={p['input_digest'] for p in unrun}
 assert len(comparisons)+len(unpaired)+len(unrun)==89
 assert set(checked_inputs)==set(q['admitted_inputs']) and all(p['status']=='ALL_ORDERED_MEMBERS_FRESH_FULL_SHA_MATCH' and not p['reused_prior_session_reads'] for p in checked_inputs.values())
 for key in checked_inputs:native.check_input(native.spec_for('E2-AEV100-'+key[:16]+'-CM')) # Fresh current stat/command binding after the full-byte replay and point rechecks.
 signs={family:dict(collections.Counter('positive' if r['cycles'][off]>r['cycles'][on] else 'negative' if r['cycles'][off]<r['cycles'][on] else 'zero' for r in comparisons)) for family,off,on in [('C','CM','CH'),('D','DM','DH')]}
 profile_counts=dict(collections.Counter(p['operational_profile']['operational_resource_profile'] for p in points+failures));assert profile_counts.get('ORIGINAL_CAP8192_WALL21600',0)==105 and profile_counts.get('OBSERVABILITY_CAP1M_WALL90_V1',0)==len(q['consumed'])-105
 assert set(q['effective_specs'])==set(q['consumed'])-profile_binding['old_cells'],'runtime specs exist for unattempted or old spent cells at closure'
 result={'schema':'DTC_V100_FULL_SWEEP_COMPLETE_CONSUMER_V8','operational_profile_counts':profile_counts,'host_execution_profile_counts':dict(collections.Counter(p['host_execution_profile']['profile'] for p in points+failures)),'host_execution_source_and_per_point_actual_CPU_replayed':True,'host_execution_provenance_source_sha256':sha(T/'tools/sweep_host_provenance_v2.py'),'per_attempt_source_and_wall_profile_replayed':True,'operational_profile_verifier_sha256':sha(T/'tools/sweep_runtime_provenance_v5.py'),'status':'ALL_APPLICABLE_ATTEMPTS_AND_HOLDS_ARCHIVE_NATIVE_RESTORE_REPLAYED','candidate_full_vectors':89,'normal_entry_aliases':93,'explicit_fraction_entries_excluded':25,'uncommitted_not_available':7,'applicable_four_attempt_inputs':len(attempt_arms),'eligible_complete_four_cell_inputs':len(comparisons),'inputs_with_unaccepted_arms':len(unpaired),'preserved_input_holds':len(unrun),'new_native_attempts':len(q['consumed']),'accepted_complete_points':len(points),'classified_unaccepted_points':len(failures),'max_registered_starts':356,'sealed_never_started_cells':len(q['sealed']),'remaining':0,'model_automatic_retries':0,'same_Core_cache_mechanism_config_family_as_GEMM_and_short3':True,'all_points_same_Framework_binary_SHA':False,'observational_Framework_revision':{'original':'cfd3ff56d7ba6642dab6c7710ec4f6065168174e','revised':'3b362ab5c0934fdcea9697b10244c6de5c4a14ae','delta':'one observational exporter record-limit constant;Core/cache/performance source unchanged','original_binary':'ab6c717dcbe7932af8bbb6dfbad0b1df9ec0ba447c067085cb92855fb8628a8e','revised_binary':'b963139b72ea1fe5000c35803386f3a5b5eaf4905e127f1bdb12f16e13486329'},'whole_input_sha_and_declared_geometry_only_not_full_native_capture_certification':True,'comparisons':comparisons,'incomplete_comparisons':unpaired,'unrun_input_holds':unrun,'per_point_evidence':points,'per_failed_point_evidence':failures,'hash_effect_sign_counts_complete_four_cell_inputs_only':signs,'verified_native_restored_entries':archive_entries,'all_applicable_original_four_cells_attempted_exactly_once':True,'each_unique_applicable_input_current_full_SHA_rechecked_once':len(checked_inputs),'input_full_SHA_reader_sha256':input_sha_session['reader_sha256'],'input_full_SHA_replay_session':input_sha_session,'per_input_full_SHA_replay':checked_inputs,'fresh_input_bytes_read_after_native_closure':sum(p['fresh_bytes_read'] for p in checked_inputs.values()),'input_stat_bindings_rechecked_after_all_full_SHA_and_point_replays':True,'prior_request_rows_and_old_history_unchanged':True,'local_safety_floor_bytes':5*1024**3,'all_outputs_SOURCE_KEEP_at_consumer':True,'no_completion_biased_interim_mean':True,'no_equal_area_or_unique_DTC_causality_claim':True,'paper_mother':'Englishv0.23 preserved,actual package unavailable,no manuscript promotion','verified_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 domain_gate=load('explicit_current_source_domain_review_gate','sweep_close_delivery_v8.py');result['domain_adjudication_proof']=domain_gate.domain_review_gate(result)
 with (T/'analysis/COMPLETE_RESULT.json').open('x') as f:json.dump(result,f,indent=2);f.write(chr(10))
 print(json.dumps({k:v for k,v in result.items() if k not in ['comparisons','incomplete_comparisons','unrun_input_holds','per_point_evidence','per_failed_point_evidence']},indent=2))
 return result
if __name__=='__main__':main()
