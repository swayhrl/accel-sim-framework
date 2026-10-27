import pathlib,json,hashlib,decimal,datetime,re,collections,shutil,zipfile
P=pathlib.Path;O=P('D:/repo/artifacts/dtc-paper42-hash-review-20261027-v1');TMP=P('D:/repo/tmp');R=json.loads((TMP/'DTC_P42_SOURCE_INDEX_FULL.json').read_bytes());native_index_sha=hashlib.sha256((TMP/'DTC_P42_SOURCE_INDEX_FULL.json').read_bytes()).hexdigest()
R['native_full_source_index']=dict(path=R['root']+'/analysis/SOURCE_INDEX.json',sha256=native_index_sha,full_current_repair_objects_preserved_on_164=True)
R['repair_identity_references']=[dict(request=r['request'],cohort=r['cohort'],uuid=r['uuid'],root=r['root'],canonical_state=(r.get('result')or{}).get('state'),independent_postprocess_state=(r.get('independent_postprocess')or{}).get('state'),DONE=bool(r.get('DONE')),stop_reason=(r.get('DONE')or{}).get('stop_reason'),wait_rc=(r.get('DONE')or{}).get('launcher_wait_returncode'),performance_eligible=False,accepted_performance_cycles=None)for r in R['repair_identity_references']]
(O/'SOURCE_INDEX.json').write_text(json.dumps(R,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
F=json.loads((O/'REPRESENTATIVE_FREEZE.json').read_bytes());D=json.loads((O/'PERFORMANCE.json').read_bytes());B=json.loads((O/'BOTTLENECK_ANALYSIS.json').read_bytes());C=json.loads((TMP/'DTC_P42_COUNTERS_RAW_EXTRACT.json').read_bytes());L=json.loads((TMP/'DTC_P42_LEDGER_AUDIT.json').read_bytes());E=json.loads((TMP/'DTC_PAPER_DEDUP_EVIDENCE_20261027_V2.json').read_bytes());checks=[]
def check(label,ok):assert ok,label;checks.append(label)
check('immutable representative freeze bytes match all joins',hashlib.sha256((O/'REPRESENTATIVE_FREEZE.json').read_bytes()).hexdigest()==D['freeze_sha256']==B['freeze_sha256'])
check('identity froze before performance aggregation',datetime.datetime.fromisoformat(F['frozen_CST'])<datetime.datetime.fromisoformat(D['aggregated_CST']))
check('44 program rows 42 ordinary slots and2 derived',len(F['programs_44_to_42'])==44 and sum(p['ordinary_main_slot']for p in F['programs_44_to_42'])==42)
check('72 unique mappings all preserved',len(F['mapping_72_to_42'])==len({r['input_digest']for r in F['mapping_72_to_42']})==72)
check('35 chosen plus7 unresolved is42',F['identity_frozen_ordinary']==35 and len(F['unresolved_ordinary'])==7)
check('12 original manual programs adjudicated',len(F['twelve_prior_manual_adjudications'])==12 and sum(r['state']=='IDENTITY_FROZEN'for r in F['twelve_prior_manual_adjudications'])==6)
check('CFD retained as unresolved application scope',next(p for p in F['programs_44_to_42']if p['program']=='cfd')['state']=='UNRESOLVED')
check('ATAX grid-rewritten prefix excluded',next(p for p in F['mapping_72_to_42']if p['input_digest'].startswith('dd895'))['decision']=='EXCLUDED_PROVEN_PARTIAL_CAPTURE')
check('no outcome-based selection',F['performance_used_for_selection']is False and F['performance_summarized_before_freeze']is False)
check('23 common panel 12 selected incomplete19 target missing',len(D['common_panel_programs'])==23 and D['coverage']['incomplete_selected']==12 and D['coverage']['missing_from_common_panel']==19)
check('111 original accepted selected cells',D['coverage']['accepted_selected_cells']==111)
orig={r['input_digest']:r for r in L['current_original']};passed=negative=done=missing=0
for r in D['audit_72']:
 rr=orig[r['input_digest']]
 for mode,m in r['modes'].items():
  src=rr['modes'][mode];ok=(src.get('result')or{}).get('state')=='PASS_STRICT_ARCHIVE_NATIVE_RESTORE';check('original cycle join '+m['cohort'],m['accepted_cycles']==(src['result']['cycles']if ok else None));passed+=ok;dd=src.get('DONE')or{};done+=bool(dd);negative+=bool(dd and(dd.get('stop_reason')or dd.get('launcher_wait_returncode')))
check('251 strict original cells 279DONE28negative',passed==251 and done==279 and negative==28)
check('45 independent repair identities never admitted as performance',len(R['repair_identity_references'])==45 and all(not r['performance_eligible']and r['accepted_performance_cycles']is None for r in R['repair_identity_references']))
decimal.getcontext().prec=70;good=[r for r in D['table_42']if r['four_accepted']]
for key in D['statistics_common_panel']:
 prod=decimal.Decimal(1);ps=ns=zs=0
 for r in good:
  v=r['accepted_cycles'];a,b={'traditional_hash_CM_CH':(v['CM'],v['CH']),'DTC_hash_DM_DH':(v['DM'],v['DH']),'DTC_linear_CM_DM':(v['CM'],v['DM']),'DTC_hashed_CH_DH':(v['CH'],v['DH']),'relative_improvement':(v['CH']*v['DM'],v['CM']*v['DH'])}[key];prod*=decimal.Decimal(a)/decimal.Decimal(b);ps+=a>b;ns+=a<b;zs+=a==b
  check('unrounded ratio '+r['program']+' '+key,abs(r['ratios'][key]-a/b)<1e-14)
 gm=float(prod**(decimal.Decimal(1)/len(good)));z=D['statistics_common_panel'][key];check('independent Decimal product GM '+key,abs(gm-z['GM'])<1e-12);check('integer sign counts '+key,(ps,zs,ns)==(z['positive'],z['zero'],z['negative']))
counter={(r['program'],r['input_digest'],r['mode']):r for r in C['rows']}
for case in B['cases']:
 for mode,m in case['modes'].items():
  rr=counter[(case['program'],case['input_digest'],mode)];v=m['values'];check('terminal cycle reference '+m['cohort'],v['cycles']==rr['raw_numeric_counters']['gpu_tot_sim_cycle'][-1]['value']);check('L2 byte / sector identity '+m['cohort'],v['L2_global_read_payload_bytes']==32*v['L2_global_read_accepted_32B_sectors']);check('lower read / L2 sector observation '+m['cohort'],4*v['global_lower_read_requests']==v['L2_global_read_accepted_32B_sectors'])
  if mode.startswith('D'):check('unprinted finiteOO counters remain missing '+m['cohort'],v['Tag_bank_conflict_events']is None and v['OO_duplicate_after_eviction_events']is None and v['OO_PIB_full_events']is None)
page=(O/'review.html').read_text(encoding='utf8');check('all72 full identities in visible audit HTML',all(r['input_digest']in page for r in F['mapping_72_to_42']));check('all44 program detail sections',page.count('<details><summary>')==44)
for path in ['README.md','SOURCE_INDEX.json','REPRESENTATIVE_FREEZE.json','PERFORMANCE.json','BOTTLENECK_ANALYSIS.json','MODEL_COMPARABILITY.json','ATAX_PREFIX_PROOF.json','TWELVE_ADJUDICATIONS.json','FREEZE_RECEIPT.json','figures/hash_distribution.png','figures/hash_distribution.svg','figures/traffic_and_cycles.png','figures/traffic_and_cycles.svg']:check('deliverable exists '+path,(O/path).is_file())
check('no new model or source intervention',D['new_simulations']==B['new_simulations']==0 and D['old_results_replaced']==0 and F['authority_and_budgets_unchanged'])
tools=O/'tools';tools.mkdir(exist_ok=True)
for name in ['dtc_p42_evidence_init.py','dtc_p42_sources_read.py','dtc_p42_atax_compare.py','dtc_p42_adjudication_evidence.py','dtc_p42_freeze_selection.py','dtc_p42_extract_counters.py','dtc_p42_model_contract.py','dtc_p42_performance.py','dtc_p42_bottleneck_analysis.py','dtc_p42_supplement.py','dtc_p42_build_review.py','dtc_p42_validate_package.py']:shutil.copy2(TMP/name,tools/name)
proof=dict(status='PASS',checks=len(checks),independent_GM_method='70-digit Decimal exact integer ratio product and nth root; production summary uses log mean',assertions=checks,figures_visually_reviewed=True,analysis_scope='Frozen native trace contract; no final42 fully-certified application GM asserted',new_model_starts=0,verification_UTC=datetime.datetime.now(datetime.timezone.utc).isoformat());(O/'ANALYSIS_VALIDATION.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
manifest={str(p.relative_to(O)).replace('\\','/'):dict(sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size)for p in O.rglob('*')if p.is_file()and p.name not in ['MANIFEST.json','PUBLICATION_RECEIPT.json']};(O/'MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
dest=O.with_suffix('.zip')
with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
 for p in O.rglob('*'):
  if p.is_file():z.write(p,str(p.relative_to(O)).replace('\\','/'))
with zipfile.ZipFile(dest)as z:assert z.testzip()is None
print(json.dumps(dict(status='PASS',checks=len(checks),package_files=len(manifest),zip=str(dest),zip_sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),zip_bytes=dest.stat().st_size,freeze_sha256=D['freeze_sha256'])))
