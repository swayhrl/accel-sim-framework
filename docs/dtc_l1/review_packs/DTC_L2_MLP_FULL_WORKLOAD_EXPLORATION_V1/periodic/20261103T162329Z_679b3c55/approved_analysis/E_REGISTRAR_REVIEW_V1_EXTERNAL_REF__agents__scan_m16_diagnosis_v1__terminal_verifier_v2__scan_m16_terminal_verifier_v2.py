"""Read-only V2 verifier for one preserved V1 engineering-negative bundle.

Only the SSHFS virtual inode of the eight added context entries may vary.
Original native evidence, archive, selectors, certificate and restore stay exact.
"""
import sys
sys.dont_write_bytecode=True
import pathlib,hashlib,json,stat,importlib.util,datetime,argparse
P=pathlib.Path
A=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1')
OLD_SOURCE=A/'agents/scan_m16_diagnosis_v1/terminal_impl_v1/scan_m16_engineering_negative_v1.py'
OLD_SHA='08aecd21ba2dbea0656bd8e390acad09f4276954b2d1bc7dcbaec9593c74c013'
EXPECTED_BUNDLE=A/'engineering_negative_evidence_v1/E2-DTCL2MLP-6df3a84b612086e8-DH-M16-V1/1e968456ccefd837eacee605d7ffacc712860114e8a7fea17b4633b25cecbf5f'
PROD=EXPECTED_BUNDLE.parent
SEALED={
 'SOURCE_MANIFEST.json':'53f568eb41910b6ec83785ca9e3b4446381d3d9ac09ffe3207df3e1d49aa344d',
 'ENGINEERING_TERMINAL_NEGATIVE.json':'37842f4191c6a0f293a01d22834c28794c3e23a477b1d657976d01bdb055c9e7',
 'ENGINEERING_ARCHIVE_RECEIPT.json':'e37ac3aa36c238da9b3e1cea3ed7b04e321d6e35265f640342e426d5f5e401a9',
 'ARCHIVE_INDEX.json':'210ae564a3e4d2d00766922a62bc777ea0b0062ed58aafe85fca118ab33658d6',
 'COMMIT.json':'c5d998617d11e00e8700f67f38d313a4adbb1bad5176c1d2f7f81b6806ca7295'}
CONTEXT='_ENGINEERING_CONTEXT'
CONTEXT_FILES={'CANONICAL_SPEC.json','DISPATCH_BINDING.json','ENGINEERING_GUARD.json','FRONTEND_FAILURE.json','IMPLEMENTATION.py','INTENT.json','PINNED_SOURCES.json'}
POLICY=dict(schema='EXACT_TRUE164_ADDED_CONTEXT_VIRTUAL_INODE_V2',scope='only original eight added context entries on exact preserved true164 bundle',allowed_variable_fields=['inode'],native_original_fields='ALL_STRICT',all_other_transport_fields='ALL_STRICT_INCLUDING_DEV_CTIME_NLINK_ALLOCATED_UID_GID_MODE_SIZE_MTIME_TYPE_PATH_SHA',archive_and_certificate='ORIGINAL_BYTES_AND_SELECTORS_UNCHANGED')
def need(v,why):
 if not v:raise RuntimeError('HOLD: '+why)
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def old_module():
 need(sha(OLD_SOURCE)==OLD_SHA,'original producer source drift')
 s=importlib.util.spec_from_file_location('preserved_scan_m16_producer_v1_for_v2',OLD_SOURCE);o=importlib.util.module_from_spec(s);s.loader.exec_module(o);return o
def compare_context_transport(original,current,canon):
 """Pure strict comparison; never rewrites either manifest or selector."""
 need(set(original)==set(current),'manifest top-level key drift')
 for k in original:
  if k not in ['entries','selector_sha256']:need(original[k]==current[k],'nontransport manifest drift '+k)
 need(original['selector_sha256']==hashlib.sha256(canon(original['entries'])).hexdigest(),'old selector invalid')
 need(current['selector_sha256']==hashlib.sha256(canon(current['entries'])).hexdigest(),'current observed selector invalid')
 before=original['entries'];after=current['entries'];need(len(before)==len(after),'manifest member count drift')
 allowed={CONTEXT}|{CONTEXT+'/'+p for p in CONTEXT_FILES};seen=set();reports=[]
 for old,new in zip(before,after):
  path=old['path'];need(path==new['path'],'manifest path/order drift')
  if path in allowed:
   seen.add(path);need(old['type']==('directory'if path==CONTEXT else'file'),'context type identity')
   a=dict(old);b=dict(new);oi=a.pop('inode');ni=b.pop('inode');need(a==b,'context logical identity drift '+path)
   reports.append(dict(path=path,old_archived_transport_inode=oi,current_transport_inode=ni,changed=oi!=ni,all_other_fields_exact=True,content_sha256=old.get('sha256'),native_original=False))
  else:need(old==new,'native original full lstat/SHA identity drift '+path)
 need(seen==allowed,'exact original eight context members required')
 return dict(policy=POLICY,entries=reports,changed_count=sum(x['changed']for x in reports),original_selector_sha256=original['selector_sha256'],current_observation_selector_sha256=current['selector_sha256'],original_manifest_not_modified=True)
def verified_original_seals(bundle):
 for name,pin in SEALED.items():
  p=bundle/name;need(stat.S_ISREG(p.lstat().st_mode)and sha(p)==pin,'preserved original seal drift '+name)
 return dict(SEALED)
def verify_bundle(bundle,expected_self_sha,already_locked=False):
 need(expected_self_sha and sha(__file__)==expected_self_sha,'reviewed V2 self source SHA')
 o=old_module();ctx=o.context();bundle=P(bundle);o.no_symlink_parents(bundle)
 need(bundle==EXPECTED_BUNDLE and bundle.parent==o.PROD,'exact preserved bundle only')
 seals=verified_original_seals(bundle);m=o.read(bundle/'SOURCE_MANIFEST.json')
 need(m['schema']==o.SCHEMA and m['cohort']==o.C and m['uuid']==o.U and m['request']==o.REQ,'old manifest identity')
 need(m['pins']==ctx['pins']and m['txid']==bundle.name,'old source pins/tx')
 tx=o.digest(o.canon(dict(cohort=o.C,uuid=o.U,original_selector_sha256=o.digest(o.canon(m['original_entries'])),pins=ctx['pins'])))
 need(m['txid']==tx,'exact deterministic old tx')
 context_root=bundle/'context';o.no_symlink_parents(context_root);need(context_root==P(m['context_source_root']),'exact true164 context path')
 # o.context()/identity() freshly verifies the exact true164 source and native boot/ns.
 observed=o.build_manifest(ctx,m['original_entries'],context_root,m['txid'])
 transport=compare_context_transport(m,observed,o.canon)
 need(m['original_selector_sha256']==o.digest(o.canon(m['original_entries'])),'native original selector')
 o.source_check(m,ctx);need(o.gzip_evidence(o.OUT)==o.read(bundle/'GZIP_CRC_PROOF.json'),'original all-gzip CRC')
 b,f,v=o.libraries();index=f.verify_archive(bundle,m);receipt=o.read(bundle/'ENGINEERING_ARCHIVE_RECEIPT.json');cert=o.read(bundle/'ENGINEERING_TERMINAL_NEGATIVE.json');initial=o.read(bundle/'DEPARTURE_PROOF.json')
 o.validate_certificate(cert,m,index,receipt,initial)
 need(cert['intent_sha256']==ctx['row']['intent_sha256']and cert['canonical_spec_sha256']==ctx['pins'][str(o.R/'control/specs'/(o.C+'.json'))]['sha256']and cert['source_pins_sha256']==o.digest(o.canon(ctx['pins']))and cert['original_native_execution_receipt_created']is False,'original exact certificate source binding')
 for name in ['SOURCE_MANIFEST.json','ARCHIVE_INDEX.json','COMMIT.json','ENGINEERING_ARCHIVE_RECEIPT.json','ENGINEERING_TERMINAL_NEGATIVE.json','DEPARTURE_PROOF.json','GZIP_CRC_PROOF.json']:
  need(stat.S_ISREG((bundle/name).lstat().st_mode),'nonregular original control evidence')
 need(receipt['true164_root']==str(bundle)and receipt['true164_source']=='admin-wcx@10.208.130.164:/home/shared'and receipt['native_device']==2128 and receipt['all_entries_sha_verified']is True,'old archive location claims')
 nr=P(receipt['native_restore_proof_path']);need(nr.parent==bundle and stat.S_ISREG(nr.lstat().st_mode)and sha(nr)==receipt['native_restore_proof_sha256'],'preserved native restore proof')
 nd=o.read(nr);dst=P(receipt['native_restore']);o.no_symlink_parents(dst)
 need(dst.parent==o.RESTORE and nd['destination']==str(dst)and nd['txid']==m['txid']and dst.stat().st_dev==2128,'exact native2128 restore')
 actual=f.check_native(dst,m);need(actual==nd['proof'],'all native restore identity/metadata exact')
 need(o.gzip_evidence(dst)==o.read(bundle/'GZIP_CRC_PROOF.json'),'restored all-gzip CRC')
 fresh=o.departures(m['original_entries']);o.source_check(m,ctx)
 o.identity();verified_original_seals(bundle);need(sha(OLD_SOURCE)==OLD_SHA and sha(__file__)==expected_self_sha,'end-of-verify source drift')
 final_transport=compare_context_transport(m,o.build_manifest(ctx,m['original_entries'],context_root,m['txid']),o.canon)
 return dict(status='VERIFIED_TYPED_ENGINEERING_NEGATIVE_UNACCEPTED',cohort=o.C,uuid=o.U,certificate=str(bundle/'ENGINEERING_TERMINAL_NEGATIVE.json'),certificate_sha256=sha(bundle/'ENGINEERING_TERMINAL_NEGATIVE.json'),archive_manifest_sha256=sha(bundle/'SOURCE_MANIFEST.json'),actual_archive_sha256=index['archive_sha256'],native_restore=str(dst),native_restore_entries=len(actual),verified_future_model_growth_bytes=0,accepted_cycles=None,performance_accepted=False,fresh_departure_proof=fresh,original_spent_starts=1,refunds=0,DONE_or_EXIT_or_registry_writes=0,source_disposition='SOURCE_KEEP',original_native_execution_receipt_present=False,
  verifier_schema='SCAN_M16_ENGINEERING_NEGATIVE_VERIFIER_V2',verifier_source_path=str(P(__file__).resolve()),verifier_source_sha256=expected_self_sha,original_producer_source_path=str(OLD_SOURCE),original_producer_source_sha256=OLD_SHA,original_v1_verifier_pass_claimed=False,verification_policy=POLICY,transport_identity_observations_before=transport,transport_identity_observations_after=final_transport,preserved_original_seals=seals,original_manifest_selector_sha256=m['selector_sha256'],production_writes=0,models_started=0,signals=0)
def verify_certificate(certificate_path,expected_self_sha):
 p=P(certificate_path);need(p.name=='ENGINEERING_TERMINAL_NEGATIVE.json','exact certificate basename');return verify_bundle(p.parent,expected_self_sha)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--bundle',default=str(EXPECTED_BUNDLE));p.add_argument('--expected-self-sha',required=True);a=p.parse_args()
 try:print(json.dumps(verify_bundle(a.bundle,a.expected_self_sha),indent=2,sort_keys=True))
 except Exception as e:print(json.dumps(dict(status='HOLD',reason=repr(e),models_started=0,signals=0,authority_writes=0)),file=sys.stderr);sys.exit(2)
