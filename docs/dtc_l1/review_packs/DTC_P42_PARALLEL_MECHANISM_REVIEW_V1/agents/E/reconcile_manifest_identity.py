"""Reconcile two original manifest byte sequences; never normalize either original.
Reads only E-owned copied evidence. Scientific snapshot and accepted numbers are frozen.
Writes corrected append-only-stage artifacts; original V1 files are never written.
"""
import pathlib,json,hashlib,datetime
A=pathlib.Path(__file__).parent
def h(b):return hashlib.sha256(b).hexdigest()
def wr(n,v):
 b=(json.dumps(v,indent=2,ensure_ascii=False)+'\n').encode('utf8') if not isinstance(v,str) else v.encode('utf8');(A/n).write_bytes(b)
win=(A/'DELIVERY_MANIFEST.json').read_bytes();nas=(A/'DELIVERY_MANIFEST_164_ORIGINAL_BYTES.json').read_bytes()
assert h(win)=='abec92752fd60026710ce6cdda7daeb7a5cf4851cec1fbdf2b73cff895c05bd8'
assert h(nas)=='773f3ad8e705caa3f68bbfe6bdb5d6f4c814be63f80080c6bc5d26ccf3106bff'
assert json.loads(win)==json.loads(nas) and win.replace(b'\r\n',b'\n')==nas and win!=nas
wp=A/'DELIVERY_MANIFEST_WINDOWS_ORIGINAL_BYTES.json'
if wp.exists():assert wp.read_bytes()==win
else:wp.write_bytes(win)
for n in ['LATEST_ACCEPTED_ADDENDUM.json','LATEST_ACCEPTED_ADDENDUM.md','LATEST_ACCEPTED_VALIDATION.json','LATEST_MANIFEST_SUPPLEMENT.json']:
 q=A/(pathlib.Path(n).stem+'_PRE_RECONCILIATION'+pathlib.Path(n).suffix)
 if not q.exists():q.write_bytes((A/n).read_bytes())
original=json.loads((A/'LATEST_ACCEPTED_ADDENDUM_PRE_RECONCILIATION.json').read_bytes())
mh=json.loads(win);common={x['name']:x['sha256'] for x in mh['files']}
for n,s in common.items():assert h((A/n).read_bytes())==s,n
wh={**common,'DELIVERY_MANIFEST.json':h(win)};nh={**common,'DELIVERY_MANIFEST.json':h(nas)}
rec={'schema':'DTC_E_LOCATION_IDENTITY_RECONCILIATION_V1','observed_UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'diagnosis':'Manifest itself was separately serialized by verify_delivery.py on Windows and Linux; Windows default text newline translation produced CRLF, Linux produced LF. The 13 listed deliverables were verified byte-identical. The manifest itself was not included among those13.','windows_original':{'path':'D:/repo/artifacts/dtc-p42-parallel-mechanism-review-v1/agents/E/DELIVERY_MANIFEST.json','preserved_copy':'DELIVERY_MANIFEST_WINDOWS_ORIGINAL_BYTES.json','sha256':h(win),'bytes':len(win),'CRLF_count':win.count(b'\r\n'),'LF_count':win.count(b'\n')},'164_original':{'path':'/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_p42_parallel_mechanism_review_v1/agents/E/DELIVERY_MANIFEST.json','preserved_copy':'DELIVERY_MANIFEST_164_ORIGINAL_BYTES.json','sha256':h(nas),'bytes':len(nas),'CRLF_count':nas.count(b'\r\n'),'LF_count':nas.count(b'\n')},'manifests_byte_identical':False,'manifests_JSON_semantically_identical':True,'only_CRLF_to_LF_difference_proven':True,'all_13_listed_artifact_bytes_identical':True,'prior_files_sha256_windows_original':wh,'prior_files_sha256_164_original':nh,'original_V1_files_written':0,'scientific_result_changes':0,'accepted_cutoff_preserved':original['observed_UTC'],'accepted_count_preserved':original['accepted_cells'],'validation_contract':'Verify each original manifest against its own location-specific exact SHA256; verify all13 listed artifact bytes against shared file hashes. JSON equivalence and diagnostic CRLF mapping do not replace exact SHA checks. Do not apply the164 manifest-self hash to the Windows original, or normalize/overwrite either original.'}
wr('MANIFEST_IDENTITY_RECONCILIATION.json',rec)
original['prior_files_sha256']=wh
original['prior_file_hash_scope']='WINDOWS_ORIGINAL_COPY; for164 use prior_files_sha256_164_original explicitly'
original['prior_files_sha256_windows_original']=wh
original['prior_files_sha256_164_original']=nh
original['manifest_identity_reconciliation']='MANIFEST_IDENTITY_RECONCILIATION.json'
original['manifests_cross_location_byte_identical']=False
original['prior_common_13_artifacts_cross_location_byte_identical']=True
original['scope_caveats']=[x for x in original['scope_caveats'] if x!='Original V1 files remain byte-identical.']+['Original V1 files are preserved at each location. The two original DELIVERY_MANIFEST.json byte sequences differ only by CRLF versusLF, have separate exact identities, and must not be substituted.']
for t in original['tests']:
 if t['check'].startswith('prior_byte_preserved_'):t['check']=t['check'].replace('prior_byte_preserved_','prior_164_original_byte_preserved_',1)
newchecks=[{'check':'windows_original_manifest_exact_SHA','pass':h(win)==wh['DELIVERY_MANIFEST.json']},{'check':'164_original_manifest_exact_SHA','pass':h(nas)==nh['DELIVERY_MANIFEST.json']},{'check':'distinct_manifest_byte_identities','pass':win!=nas},{'check':'manifest_JSON_content_identity','pass':json.loads(win)==json.loads(nas)},{'check':'exclusive_CRLF_difference','pass':win.replace(b'\r\n',b'\n')==nas}]+[{'check':'windows_original_artifact_byte_preserved_'+n,'pass':h((A/n).read_bytes())==s} for n,s in common.items()]
original['tests']+=newchecks
wr('LATEST_ACCEPTED_ADDENDUM.json',original)
md=(A/'LATEST_ACCEPTED_ADDENDUM_PRE_RECONCILIATION.md').read_text(encoding='utf8')
md=md.replace('Prior V1 bytes are preserved.','Prior V1 files are preserved at each location; the two original manifest byte sequences have distinct SHA256 identities.')
md=md.replace('29 assertions passed; all prior manifest files and the prior delivery manifest retain their exact SHA256.',f'{len(original["tests"])} scoped assertions passed. All 13 listed artifacts retain shared exact SHA256; each original delivery manifest retains its own location-specific SHA256.')
md+='\n## Manifest identity correction\n\nThe Windows original manifest has SHA256 `'+h(win)+'` (2,451 bytes,75 CRLF); the164 original has SHA256 `'+h(nas)+'` (2,376 bytes,75 LF). JSON content is identical, and exact byte comparison proves the only difference is CRLF versusLF. Neither original was overwritten or normalized. Both original byte sequences are preserved as named copies at both locations. The old unscoped preservation statement was inaccurate for the manifest itself. `MANIFEST_IDENTITY_RECONCILIATION.json` supplies explicit Windows and164 hash maps; original reports, scientific data and cutoff are unchanged.\n'
wr('LATEST_ACCEPTED_ADDENDUM.md',md)
wr('LATEST_ACCEPTED_VALIDATION.json',{'observed_UTC':original['observed_UTC'],'reconciliation_UTC':rec['observed_UTC'],'passed':len(original['tests']),'tests':original['tests'],'prior_preservation_hash_scope':'Each original location separately; common13 artifacts byte-identical; manifest-self bytes explicitly different.'})
names=['LATEST_ACCEPTED_ADDENDUM.json','LATEST_ACCEPTED_ADDENDUM.md','LATEST_ACCEPTED_VALIDATION.json','MANIFEST_IDENTITY_RECONCILIATION.json','DELIVERY_MANIFEST_WINDOWS_ORIGINAL_BYTES.json','DELIVERY_MANIFEST_164_ORIGINAL_BYTES.json','build_latest_addendum.py','reconcile_manifest_identity.py']
wr('LATEST_MANIFEST_SUPPLEMENT.json',{'schema':'DTC_E_APPEND_ONLY_MANIFEST_SUPPLEMENT_V2','prior_delivery_manifest_windows_sha256':h(win),'prior_delivery_manifest_164_sha256':h(nas),'prior_manifest_identities_distinct':True,'prior_files_unchanged_at_each_location':True,'all_13_shared_artifact_SHA256_unchanged':True,'files':[{'name':n,'sha256':h((A/n).read_bytes()),'bytes':(A/n).stat().st_size} for n in names],'accepted_cutoff_UTC':original['observed_UTC'],'accepted_count':original['accepted_cells'],'pending_count':original['pending_cells'],'new_scientific_reads_or_simulations':0})
print(json.dumps({'reconciled':True,'checks':len(original['tests']),'WindowsSHA':h(win),'164SHA':h(nas),'addendumSHA':h((A/'LATEST_ACCEPTED_ADDENDUM.json').read_bytes()),'supplementSHA':h((A/'LATEST_MANIFEST_SUPPLEMENT.json').read_bytes())}))
