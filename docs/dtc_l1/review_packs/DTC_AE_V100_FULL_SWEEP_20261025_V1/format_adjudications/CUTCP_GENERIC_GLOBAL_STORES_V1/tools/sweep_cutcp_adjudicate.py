"""Publish a separate current-source format adjudication; original HOLD persists."""
import pathlib,json,copy,hashlib,datetime
P=pathlib.Path;T=P('/root/data/dtc_main_v100_sweep_20261025_v1');KEY='af7320f9d9dc662971b1856cac87f29f9b8e4b2a65a7f9d4223bb7a74803fef8';ROOT=T/'analysis/cutcp_generic_domain_v1'
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def main():
 review_path=ROOT/'RESULT.json';review=read(review_path);original_path=T/'qualification'/KEY/'QUALIFICATION.json';before=sha(original_path);original=read(original_path)
 assert review['status']=='CURRENT_SOURCE_GENERIC_CONTRACT_PASS_PENDING_EXPLICIT_SCIENTIFIC_ADMISSION' and review['members']==len(review['rows'])==11 and not review['issues'] and review['input_digest']==KEY
 assert original['prior_scientific_statuses_preserved']==[] and len(original['issues'])==11 and {i['reason'] for i in original['issues']}=={'GENERIC_SOURCE_ADDRESS_CLASSIFICATION_REQUIRED'}
 assert review['original_qualification_sha256']==before and review['source_contract']['LOCAL_MEM_SIZE_MAX']==16384
 for field in ['resolver','core_header']:assert sha(review['source_contract'][field+'_path'])==review['source_contract'][field+'_sha256']
 qualified=copy.deepcopy(original);qualified.update(schema='DTC_CURRENT_SOURCE_FULL_INPUT_FORMAT_ADJUDICATION_V2',status='BODY_COMPLETE_SHA_AND_BASIC_FORMAT_PASS',issues=[])
 counts=[]
 for row,proof in zip(qualified['rows'],review['rows']):
  assert row['ordinal']==proof['ordinal'] and row['path']==proof['path'] and row['sha256']==proof['full_current_sha256'] and not proof['issues'] and proof['trace_version']==3
  generic=row['memory_instruction_paths']['GENERIC_SOURCE_ADDRESS_CLASSIFICATION_REQUIRED'];assert generic==proof['generic_records']
  assert proof['generic_opcode_and_space_counts']==[{'opcode':'ST','resolved_space':'GLOBAL','records':generic}]
  assert proof['widths']==[{'opcode':'ST.E.SYS','trace_width':4,'parser_width':4,'records':generic}]
  assert int(proof['headers']['-shmem base_addr'],16)>0 and int(proof['headers']['-local mem base_addr'],16)>0
  del row['memory_instruction_paths']['GENERIC_SOURCE_ADDRESS_CLASSIFICATION_REQUIRED'];row['memory_instruction_paths']['ORDINARY_STORE']=row['memory_instruction_paths'].get('ORDINARY_STORE',0)+generic
  row['current_source_generic_store_adjudication']={'review_sha256':sha(review_path),'member_review_sha256':sha(ROOT/('kernel_'+str(row['ordinal'])+'.json')),'records':generic,'native_resolution':'ALL_ACTIVE_LANES_GLOBAL;memory_store;CACHE_ALL;width4','original_body_member_sha256':row['sha256']};counts.append(generic)
 qualified['explicit_current_source_format_adjudication']={'original_qualification_path':str(original_path),'original_qualification_sha256':before,'review_path':str(review_path),'review_sha256':sha(review_path),'classification':'Previously unclassified genericST.E.SYS is source-proven ordinary GLOBALstore on every active lane;no parser/model change','old_HOLD_not_erased':True,'prior_hard_scientific_HOLDs_absent':True,'performance_acceptance_granted':False}
 qpath=ROOT/'QUALIFIED_INPUT_V2.json'
 with qpath.open('x') as f:json.dump(qualified,f,indent=2);f.write(chr(10))
 assert sha(original_path)==before
 adjudication={'schema':'DTC_CUTCP_EXPLICIT_CURRENT_SOURCE_FORMAT_ADJUDICATION_V1','status':'CURRENT_SOURCE_FORMAT_GATE_PASS_ORIGINAL_HOLD_RETAINED','input_digest':KEY,'members':11,'full_current_bytes_verified':review['full_bytes_read'],'generic_ST_E_SYS_global_store_records':sum(counts),'trace_and_parser_width':4,'all_active_lanes_first_lane_space_consistent':True,'shared_and_local_bases_present_all11':True,'source_contract':review['source_contract'],'original_qualification_path':str(original_path),'original_qualification_sha256':before,'original_status':original['status'],'new_qualified_input_path':str(qpath),'new_qualified_input_sha256':sha(qpath),'review_sha256':sha(review_path),'native_values':'UNPROVEN','complete_original_native_capture':'UNPROVEN;declared full trace only','model_or_cache_or_config_or_input_modified':False,'old_HOLDs_or_performance_rows_rewritten':False,'new_model_starts':0,'automatic_model_retries':0,'next_action':'Publish/review this exact finite current-source adjudication. At R5closed boundary,prepare precise metadata admission for the four original NEVER-SPENT Cutcp cells under the same runtime/config family and original356maximum. Preserve R5HOLD/sealing snapshot/history;no consumed credit refund or old attempt rerun.','observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 with (ROOT/'EXPLICIT_FORMAT_ADJUDICATION.json').open('x') as f:json.dump(adjudication,f,indent=2);f.write(chr(10))
 print(json.dumps({k:v for k,v in adjudication.items() if k!='source_contract'},indent=2))
 return adjudication
if __name__=='__main__':main()
