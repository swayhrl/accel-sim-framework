"""Close review/runtime recovery delivery. No model launch or authority mutation."""
import pathlib,json,hashlib,subprocess,shutil,importlib.util,datetime
P=pathlib.Path;T=P('/root/data/dtc_main_short3_20261024_v1');F=T/'docs-worktree';D=F/'docs/dtc_l1/review_packs/DTC_AE_MATCHED_HASH_SHORT3_20261024_V1';N=P('/root/data/ep_l2_dtc_l1_native_v2')
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def cp(a,b):b.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(a,b)
def load(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def git(*a):return subprocess.check_output(['git','-C',str(F),*a],text=True).strip()
def main():
 receipt=read(T/'analysis/FINAL_REVIEW_ARCHIVE_RECEIPT.json');assert receipt['status']=='FINAL_REVIEW_RUNTIME_ARCHIVE_AND_NATIVE_RESTORE_VERIFIED' and receipt['new_model_starts']==0
 original=read(T/'analysis/FINAL_SCIENCE_COMMIT.json');assert git('rev-parse','HEAD')==original['commit'] and not git('status','--porcelain')
 outbox=load('copyonly_delivery_bundle_engine',T/'tools/short3_result_base.py');bundle=P(receipt['target_mount_path']);m=read(bundle/'SOURCE_MANIFEST.json');f,v=outbox.libraries(bundle)
 idx=f.verify_archive(bundle,m);proof=f.check_native(P(receipt['native_restore']),m)
 assert idx['archive_sha256']==receipt['archive_sha256'] and len(proof)==receipt['restored_entries'] and m['source_commit']==original['commit']
 reg=read(N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json');q=reg['registered_future_requests']['DTC_AEFAIR_SHORT3_EPOCH2_20261024_V1']
 assert q['state']=='COMPLETE' and len(q['consumed'])==q['budget']==12 and q['remaining']==0
 before=read(T/'control/PREIMAGE_NATIVE_SCIENCE_REGISTRY.json')
 assert all(reg['registered_future_requests'][k]==row for k,row in before['registered_future_requests'].items())
 result=read(T/'analysis/COMPLETE_RESULT.json')
 for row in result['points']:
  intent=read(T/'control/qualification_ledger'/(row['cohort']+'.INTENT.json'));out=P(intent['output'])
  assert sha(out/'raw.log')==row['raw_sha256'] and sha(out/'AEFAIR_STRICT.json')==row['strict_sha256']
 final=D/'final';delivery=final/'delivery';delivery.mkdir()
 for name in ['SOURCE_MANIFEST.json','ARCHIVE_INDEX.json','COMMIT.json','RESTORE_VERIFIED_NATIVE_TARGET.json','RECEIPT.json']:cp(bundle/name,delivery/name)
 for name in ['FINAL_REVIEW_ARCHIVE_RECEIPT.json','FINAL_SCIENCE_PUBLICATION_READBACK.json','FINAL_SCIENCE_COMMIT.json']:cp(T/'analysis'/name,delivery/name)
 report=final/'SCIENTIFIC_REPORT.md';text=report.read_text();old='''Every raw point already has a complete verified genuine164 archive and independent native restore, indexed here. This source scientific commit will also be exported with exact runtime/config/protocol evidence in a separate COPY_ONLY final review bundle. A later receipt closes that delivery step without a self-referential archive. No further scientific starts are authorized by this completed request.'''
 new=f'''Every raw point has a complete verified genuine164 archive and independent native restore. The final scientific review pack at commit{original['commit']} is also archived with exact runtime/config/protocol bytes and source-delta recovery bundles:archive SHA256{receipt['archive_sha256']},true164 root{receipt['true164_root']}. All{receipt['restored_entries']} entries were independently restored and checked on174-new ext4, then rechecked during delivery closure. The archive freezes the earlier science commit; this subsequent delivery receipt closes the chain without a self-referential archive. All sources remain SOURCE_KEEP;12/12 starts are consumed,0remain, and no further scientific starts are authorized.'''
 assert old in text;report.write_text(text.replace(old,new))
 pointer=F/'DTC_MAIN_ACTIVE_GOAL.md';txt=pointer.read_text().replace('Remaining work at this science-commit timestamp is COPY_ONLY final review recovery and publication, no simulations.','Scientific and required evidence delivery are complete:the full review/runtime bundle is genuine164 archived, independently restored and checked. Final publication readback closes delivery; no scientific or data export work remains.')
 pointer.write_text(txt)
 audit={'schema':'DTC_SHORT3_FINAL_DELIVERY_AUDIT_V1','status':'ALL_SCIENTIFIC_AND_RECOVERY_REQUIREMENTS_VERIFIED_FINAL_PUBLICATION_PENDING','request':q['request_id'],'objective_mapping':{'three_short_complete_workloads':result['selection'],'same_four_cell_design':'12fresh unique whole-input runs,sameGEMMbinary/configs','no_extra_scientific_starts':{'budget':12,'consumed':12,'remaining':0,'retries':0},'whole_input_strict':all(p['full_independent_strict_replayed'] for p in result['points']),'raw_archives_and_independent_restore':{'transactions':12,'restored_entries':result['total_verified_raw_restore_entries']},'scientific_report_and_reusable_workflow':True,'final_review_and_runtime_recovery':{'source_commit':original['commit'],'archive_sha256':receipt['archive_sha256'],'restored_entries':len(proof)},'old_GEMM_and_history':'Prior request rows/source histories unchanged;onboarding andGEMMfiles checked in complete consumer','paper_mother':'Englishv0.23 preserved,actualpackage unavailable,no manuscript promotion'},'all_original_raw_and_strict_SHA_still_frozen':True,'remaining_scientific_work':[],'remaining_data_export_work':[],'remaining_delivery_work':['Publish this delivery receipt and verify exact GitHub branch/files'],'verified_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 with (T/'analysis/FINAL_DELIVERY_REQUIREMENT_AUDIT.json').open('x') as stream:json.dump(audit,stream,indent=2);stream.write('\n')
 cp(T/'analysis/FINAL_DELIVERY_REQUIREMENT_AUDIT.json',final/'FINAL_DELIVERY_REQUIREMENT_AUDIT.json')
 subprocess.run(['git','-C',str(F),'diff','--check'],check=True)
 subprocess.run(['git','-C',str(F),'add','DTC_MAIN_ACTIVE_GOAL.md',str(D.relative_to(F))],check=True)
 subprocess.run(['git','-C',str(F),'commit','-m','Close short-workload evidence recovery and delivery'],check=True)
 commit=git('rev-parse','HEAD');out={'commit':commit,'tree':git('rev-parse','HEAD^{tree}'),'report_sha256':sha(report),'scope':'All science and recovery complete;verify final publication then closeGoal'}
 with (T/'analysis/FINAL_DELIVERY_COMMIT.json').open('x') as stream:json.dump(out,stream,indent=2);stream.write('\n')
 subprocess.run(['git','-C',str(F),'bundle','create',str(T/'analysis/short3_final_delivery.bundle'),'hrl/dtc-aefair-short3-174new-20261024-v1','^'+original['commit']],check=True)
 print(json.dumps(out,indent=2))
if __name__=='__main__':main()
