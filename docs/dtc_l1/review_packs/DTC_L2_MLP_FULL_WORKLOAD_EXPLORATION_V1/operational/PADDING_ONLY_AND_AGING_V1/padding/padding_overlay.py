"""A-only target-field-masked padding transfer, future admission only. No signals.
Frozen providers/bindings/specs and all existing supervisors remain unchanged.
"""
import pathlib,json,hashlib,math,os,time,copy,importlib.util,sys,threading
P=pathlib.Path;G=1024**3;M=1024**2;REQ='DTC_L2_MLP_FULL_WORKLOAD_EXPLORATION_20261027_V1';R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1');TARGET_KEYS={'-gpgpu_cache:dl2','-gpgpu_frfcfs_dram_sched_queue_size'};CLASS='A_SAME_DESIGN_TARGET_FIELD_MASKED_FORECAST_TRANSFER';MARKER='DTC_L2_MLP_PADDING_ONLY_OVERLAY_V1'
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def canonical(v):return(json.dumps(v,sort_keys=True,indent=2)+'\n').encode()
def jsonsha(v):return hashlib.sha256(canonical(v)).hexdigest()
def compactsha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def proc(pid):
 a=(P('/proc')/str(pid)/'stat').read_text().rsplit(')',1)[1].split();return dict(start_ticks=int(a[19]),state=a[0],RSS_bytes=int(a[21])*os.sysconf('SC_PAGE_SIZE'))
def target_signature(options):
 values=options['-gpgpu_cache:dl2'];values=values if isinstance(values,list)else[values];value=values[-1];parts=value.split(',');assert len(parts)==5 and parts[0]=='S:128:128:16'and parts[1]=='L:B:m:L:L'and parts[4]=='32';mshr=parts[2].split(':');queue=parts[3].split(':');assert mshr[0]=='A'and queue[1]=='0';E,L,Q=map(int,[mshr[1],mshr[2],queue[0]]);fr=options['-gpgpu_frfcfs_dram_sched_queue_size'];F=int(fr[-1]if isinstance(fr,list)else fr);assert E in[192,384,768]and L in[4,8,16]and Q in[32,64,128]and F in[64,128,256];assert sum(a!=b for a,b in zip([E,L,Q,F],[192,4,32,64]))<=1,'Combinations/extensions have no padding certificate';masked=list(values);masked[-1]=parts[0]+','+parts[1]+',A:<E>:<M>,<Q>:0,32';return dict(masked_cache_values=masked,effective_initial_factor_values=[E,L,Q,F])
def non_target(options):return{k:v for k,v in options.items()if k not in TARGET_KEYS}
def prediction(Peak,multiplier,additive,floor,metadata):return max(floor,math.ceil(Peak*multiplier)+additive)+metadata
def envelope(pred,RSS,hard):return max(0,min(hard,max(pred,math.ceil(RSS*1.10)))-RSS)
def row_arithmetic(cert,spec,base_row,actual):
 assert cert['eligibility_class']==CLASS and cert['actual_cohort']==spec['cohort'];assert cert['canonical_spec_sha256']==cert.get('snapshot_canonical_spec_sha256',cert['canonical_spec_sha256']);assert spec['cell']==cert['cell']and spec['input_digest']==cert['input_digest'];assert all(spec[k]==cert[k]for k in ['core_commit','framework_commit','binary_sha256','input_binding_sha256']);assert spec['expected']==cert['expected_population'];assert non_target(spec['expected_options'])==cert['normalized_non_target_options'];assert compactsha(non_target(spec['expected_options']))==cert['normalized_non_target_options_sha256'];target_signature(spec['expected_options'])
 Rpeak=cert['old_peak_provenance_P'];approved=cert['approved_new_formula_input_P'];matched=cert['certified_sameDesign_peak_P'];assert type(Rpeak)is int and Rpeak>0 and approved>=max(Rpeak,matched);floor=cert['minimum_prediction_bytes'];metadata=cert['metadata_margin_bytes'];assert floor==768*M and metadata==128*M
 old=prediction(Rpeak,1.20,256*M,floor,metadata);new=prediction(approved,1.10,128*M,floor,metadata);assert old==cert['old_estimated_peak_bytes']==spec['estimated_peak_model_RAM_bytes'];assert new==cert['approved_new_estimated_peak_bytes'];assert cert['max_prediction_reduction_bytes']==max(0,old-new)
 rss0=base_row['RSS_bytes'];rss=max(rss0,actual['RSS_bytes']);hard=spec['limits']['max_process_tree_rss_bytes'];assert cert['hard_cap_bytes']==hard;oldgrowth=envelope(old,rss0,hard);assert oldgrowth==base_row['additional_reserved_bytes'],'Base generation envelope mismatch';newgrowth=envelope(new,rss,hard);delta=max(0,envelope(old,rss,hard)-newgrowth);delta=min(delta,cert['snapshot_max_future_discount_bytes'],cert['max_prediction_reduction_bytes'],oldgrowth)
 reason='A_CERTIFIED_PADDING_ONLY'
 if rss>matched:delta=0;reason='CURRENT_RSS_ABOVE_CERTIFIED_SAME_DESIGN_PEAK'
 return dict(cohort=spec['cohort'],uuid=cert['uuid'],pid=cert['pid'],start_ticks=cert['start_ticks'],canonical_spec_sha256=cert['canonical_spec_sha256'],old_peak_provenance_P=Rpeak,approved_new_formula_input_P=approved,certified_sameDesign_peak_P=matched,old_prediction=old,new_prediction=new,base_observed_RSS_bytes=rss0,current_observed_RSS_bytes=actual['RSS_bytes'],conservative_RSS_bytes=rss,hard_cap_bytes=hard,base_old_growth_bytes=oldgrowth,new_growth_bytes=oldgrowth-delta,discount_bytes=delta,snapshot_max_discount_bytes=cert['snapshot_max_future_discount_bytes'],reason=reason)

def at_pointer(value,pointer):
 for key in pointer.strip('/').split('/')if pointer not in['','/']else[]:value=value[int(key)]if isinstance(value,list)else value[key.replace('~1','/').replace('~0','~')]
 return value
def population(proof):return dict(CTA=proof['CTA'],instructions=proof['instructions'],kernels=proof.get('kernel_count',len(proof['kernels'])if isinstance(proof.get('kernels'),list)else proof.get('kernels')))
def effective_own_rows(snapshot):
 proof=snapshot['additional_padding_admission_proof'];rows=proof['base_own_growth_rows'];assert len({x['cohort']for x in rows})==len(rows);discount={x['cohort']:x['discount_bytes']for x in proof['discount_rows']};topup={x['cohort']:x['topup_bytes']for x in proof['claim_candidate_topups']};return[dict(x,base_future_growth_bytes=x['additional_reserved_bytes'],discount_bytes=discount.get(x['cohort'],0),topup_bytes=topup.get(x['cohort'],0),additional_reserved_bytes=max(0,x['additional_reserved_bytes']-discount.get(x['cohort'],0)+topup.get(x['cohort'],0)))for x in rows]

CONFIG_EQUAL_KEYS=['request','overlay_id','source_sha256','frontend_sha256','extra_strict_sha256','owner_sha256','history_validator_sha256','policy_sha256','certificate_sha256','QA_sha256','readback_sha256','allowed_cohorts']
def validate_active_config(cfg,q):
 assert cfg['status']=='ACTIVE_FUTURE_ONLY'and cfg['request']==q['request']==REQ;allowed=cfg['allowed_cohorts'];assert allowed and len(set(allowed))==len(allowed)and set(allowed)<=set(q['admitted_specs']);record=q['additional_operational_overlays'][cfg['overlay_id']];assert record['status']=='ACTIVE'
 for key in CONFIG_EQUAL_KEYS:assert record[key]==cfg[key],key
 for key in['source','frontend','extra_strict','owner','history_validator','policy','certificate','QA','readback']:assert sha(cfg[key+'_path'])==cfg[key+'_sha256'],key
 qa=read(cfg['QA_path']);published=read(cfg['readback_path']);assert qa['status']=='PASS'and published['verified']is True and qa['native_prefix_qualified']is True and qa['owner_instance_qualified']is True and qa['additional_strict_qualified']is True
 expected={key:cfg[key+'_sha256']for key in['source','frontend','extra_strict','owner','history_validator']}
 for proof in[qa,published]:assert proof['qualified_sources']==expected and proof['policy_sha256']==cfg['policy_sha256']and proof['certificate_sha256']==cfg['certificate_sha256']
 assert cfg['source_sha256']==sha(__file__);return copy.deepcopy(record)

class PaddingOverlay:
 def __init__(self,root,policy_path,certificate_path,policy_sha256,certificate_sha256,registry_loader,base_provider):
  self.root=P(root);self.policy_path=P(policy_path);self.certificate_path=P(certificate_path);assert sha(policy_path)==policy_sha256 and sha(certificate_path)==certificate_sha256;self.policy=read(policy_path);self.certificate=read(certificate_path);self.registry_loader=registry_loader;self.base_provider=base_provider;self.policy_sha=policy_sha256;self.certificate_sha=certificate_sha256;self.immutable_verified={};self.last_proof=None;self.base_forecast=None;self.activation_context={};validator_path=P(__file__).with_name('history_evidence_validator.py');validator_path=validator_path if validator_path.exists()else P(__file__).with_name('PADDING_HISTORY_VALIDATOR.py');assert sha(validator_path)==self.policy['history_validator_sha256'];sp=importlib.util.spec_from_file_location('padding_history_validator',validator_path);self.validator=importlib.util.module_from_spec(sp);sp.loader.exec_module(self.validator)
  assert self.policy['request']==REQ and self.policy['A_only']is True and self.policy['candidate_full_original']is True;assert sha(self.root/'control/RESOURCE_POLICY.json')==self.policy['base_policy_sha256']==self.certificate['original_policy_sha256'];assert self.policy['base_resource_source_sha256']=='6ad97e35de88ff5876bc0af674324f979f35c211f31d182976d2f66abb9c4854';self.rows={x['actual_cohort']:x for x in self.certificate['certificates']};assert len(self.rows)==len(self.certificate['certificates']);assert sha(self.certificate['quantification_path'])==self.certificate['quantification_sha256'];self.quantification=read(self.certificate['quantification_path']);self.snapshot_cap=sum(x['snapshot_max_future_discount_bytes']for x in self.rows.values())
 def binding(self):return dict(dict(schema='ADDITIONAL_PADDING_ONLY_ADMISSION_BINDING_V1',request=REQ,epoch=2,overlay_id=self.policy['overlay_id'],overlay_source_sha256=sha(__file__),overlay_source_path=str(P(__file__)),history_validator_sha256=self.policy['history_validator_sha256'],policy_sha256=self.policy_sha,certificate_sha256=self.certificate_sha,effective_contract='BASE_PLUS_A_ONLY_PADDING_V1',base_binding_preserved=True,no_signals=True),**self.activation_context)
 def verify_certificate(self,c):
  cert=self.rows[c];ident=jsonsha(cert);assert cert['eligibility_class']==CLASS and cert['scope']=='INITIAL9_SINGLE_FACTOR_ONLY_NOT_FULL_OPTIONS_EQUIVALENCE';pins={x['path']:x['sha256']for x in cert['pinned_files']};assert len(pins)==len(cert['pinned_files'])and pins
  fingerprint=tuple((path,P(path).stat().st_size,P(path).stat().st_mtime_ns,P(path).stat().st_ino,P(path).stat().st_dev,P(path).stat().st_mode)for path in pins)
  if self.immutable_verified.get(ident)==fingerprint:return
  for path,digest in pins.items():assert sha(path)==digest,path
  current=read(cert['canonical_spec_path']);assert pins[cert['canonical_spec_path']]==cert['canonical_spec_sha256']==sha(cert['canonical_spec_path']);assert current['input_digest']==cert['input_digest']and current['input_binding_sha256']==cert['input_binding_sha256'];target_signature(current['expected_options'])
  provenance=cert['old_peak_provenance'];assert pins[provenance['path']]==provenance['sha256'];source=at_pointer(read(provenance['path']),provenance['json_pointer']);assert source['historical_peak_bytes']==cert['old_peak_provenance_P']and source['predicted_peak_RAM_bytes']==cert['old_estimated_peak_bytes']and not source['failed_only_lower_bound']
  peaks=[]
  for ev in cert['evidence']:
   peak=self.validator.validate_history(cert,ev,get=read,getraw=lambda path:P(path).read_bytes());assert target_signature(read(ev['spec_path'])['expected_options'])['masked_cache_values']==target_signature(current['expected_options'])['masked_cache_values'];peaks.append(peak)
  assert peaks and max(peaks)==cert['certified_sameDesign_peak_P'];self.immutable_verified[ident]=fingerprint
 def full_prediction(self,spec,history):
  if self.base_forecast is None:
   path=self.root/'tools/l2_resources.py';assert sha(path)==self.policy['base_resource_source_sha256'];sp=importlib.util.spec_from_file_location('padding_frozen_forecast',path);mod=importlib.util.module_from_spec(sp);sp.loader.exec_module(mod);self.base_forecast=mod.forecast
  forecast=self.base_forecast(spec,history,read(self.root/'control/RESOURCE_POLICY.json'));return max(spec['estimated_peak_model_RAM_bytes'],forecast['predicted_peak_RAM_bytes'])
 def project(self,base,candidate,fresh_source=True):
  assert sha(self.policy_path)==self.policy_sha and sha(self.certificate_path)==self.certificate_sha;assert base['source_module_sha256']==self.policy['base_resource_source_sha256'];q=self.registry_loader();assert q['request']==REQ;assert len({x['cohort']for x in base['own_ram_forecasts']})==len(base['own_ram_forecasts']);discounts=[];skips=[];topups=[];history=read(self.root/'control/HISTORICAL_RSS.json')if fresh_source else None
  if fresh_source:
   for row in base['own_ram_forecasts']:
    c=row['cohort'];cert=self.rows.get(c)
    if not cert or row['kind']!='LIVE_MODEL':continue
    consumed=q['consumed'].get(c)
    if not consumed or consumed.get('execution_receipt')or consumed['uuid']!=cert['uuid']:continue
    try:
     self.verify_certificate(c);spec_path=self.root/'control/specs'/(c+'.json');assert sha(spec_path)==q['admitted_specs'][c]==cert['canonical_spec_sha256'];spec=read(spec_path);assert P(cert['canonical_spec_path'])==spec_path;ip=self.root/'control/qualification_ledger'/(c+'.INTENT.json');assert sha(ip)==consumed['intent_sha256'];intent=read(ip);assert intent['uuid']==cert['uuid']and intent['cohort']==c;mp=P(intent['output'])/'NATIVE_SIMULATOR_PID_AND_MAPS.json';proof=read(mp);assert proof['pid']==cert['pid']and proof['start_ticks']==cert['start_ticks'];actual=proc(cert['pid']);db_path=self.root/'control/dispatch_bindings'/(c+'.json');db=read(db_path);dbsha=sha(db_path);assert intent['dispatch_binding_sha256']==proof['dispatch_binding_sha256']==dbsha;assert db['canonical_spec_sha256']==cert['canonical_spec_sha256'];assert db['resolved_spec_sha256']==jsonsha(dict(spec,host_cpu=db['host_cpu']));pp=P('/proc')/str(cert['pid']);cmd=(pp/'cmdline').read_bytes().replace(b'\0',b' ').decode();aff=sorted(os.sched_getaffinity(cert['pid']));ns=os.readlink(pp/'ns/mnt');assert cmd==proof['cmdline']and aff==proof['host_cpu_affinity_actual']==[db['host_cpu']]and ns==proof['mnt_namespace']==spec['execution_mnt_namespace'];identity=dict(intent_path=str(ip),intent_sha256=sha(ip),PIDproof_path=str(mp),PIDproof_sha256=sha(mp),dispatch_binding_path=str(db_path),dispatch_binding_sha256=dbsha,actual_cmdline=cmd,actual_affinity=aff,actual_mnt_namespace=ns)
     if actual['start_ticks']!=cert['start_ticks']or actual['state']in['Z','X']:continue
     calculation=row_arithmetic(cert,spec,row,actual);calculation['process_identity_evidence']=identity;discounts.append(calculation)
    except(FileNotFoundError,ProcessLookupError):continue
    except(AssertionError,KeyError,TypeError,ValueError)as error:skips.append(dict(cohort=c,discount_bytes=0,reason='CERTIFICATE_HOLD_NO_DISCOUNT',detail=str(error)))
  if fresh_source:
   for row in base['own_ram_forecasts']:
    if row['kind']!='CLAIM_OR_CANDIDATE':continue
    c=row['cohort'];path=self.root/'control/specs'/(c+'.json');assert sha(path)==q['admitted_specs'][c];spec=read(path);full=self.full_prediction(spec,history);topups.append(dict(cohort=c,canonical_prediction=spec['estimated_peak_model_RAM_bytes'],full_max_prediction=full,topup_bytes=max(0,full-spec['estimated_peak_model_RAM_bytes']),spec_sha256=sha(path),spec=spec))
  total_topup=sum(x['topup_bytes']for x in topups);total_discount=sum(x['discount_bytes']for x in discounts);assert total_discount<=self.snapshot_cap;old_total=base['total_projected_additional_RAM_bytes'];new_total=old_total-total_discount+total_topup;assert new_total>=0;decision=dict(base['admission_decision'],additional_reserved_RAM_bytes=new_total,pass_admission=not base['admission_decision']['pressure_reasons']and new_total<=base['admission_decision']['admission_RAM_budget_bytes']);proof=dict(schema='A_ONLY_PADDING_ADMISSION_PROOF_V1',binding=self.binding(),monotonic=time.monotonic(),candidate_cohort=candidate.get('cohort'),fresh_source=fresh_source,base_total_additional_RAM_bytes=old_total,effective_total_additional_RAM_bytes=new_total,total_discount_bytes=total_discount,snapshot_total_discount_cap_bytes=self.snapshot_cap,base_RAM_pass=base['physical_RAM_pass'],base_decision=base['admission_decision'],base_resource_sample={k:base.get(k)for k in ['monotonic','host_MemAvailable_bytes','cgroup_effective_headroom_bytes','native_free_bytes','required_free_bytes','free_inodes','physical_disk_pass','own_write_ceiling_pass','own_remaining_write_and_restore_bytes']},effective_decision=decision,discount_rows=discounts,claim_candidate_topups=topups,total_topup_bytes=total_topup,base_own_growth_rows=base['own_ram_forecasts']if fresh_source else[],base_peer_RAM_rows=base.get('RAM_reservation_entries',[])if fresh_source else[],history_snapshot=history,history_snapshot_sha256=jsonsha(history)if history is not None else None,certificate_holds=skips,all_foreign_and_claims_unchanged=True,candidate_full_original=True,no_physical_headroom_credit=True)
  result=dict(base,total_projected_additional_RAM_bytes=new_total,reserved_additional_live_and_candidate_RAM_bytes=new_total,admission_decision=decision,physical_RAM_pass=decision['pass_admission']if fresh_source else base['physical_RAM_pass'],additional_padding_admission_binding=self.binding(),additional_padding_admission_proof=proof);
  if fresh_source:self.last_proof=proof
  return result
 def resources(self,spec,fresh_source=False):return self.project(self.base_provider(spec,fresh_source),spec,fresh_source)
 def claims_view(self,claims,proof):
  view=copy.deepcopy(claims);rows={x['cohort']:x['additional_reserved_bytes']for x in proof['base_own_growth_rows']};discounts={x['cohort']:x['discount_bytes']for x in proof['discount_rows']};topups={x['cohort']:x['topup_bytes']for x in proof['claim_candidate_topups']}
  for c,v in view.items():
   if c in rows:v['additional_reserved_bytes']=rows[c]-discounts.get(c,0)+topups.get(c,0)
  return view
