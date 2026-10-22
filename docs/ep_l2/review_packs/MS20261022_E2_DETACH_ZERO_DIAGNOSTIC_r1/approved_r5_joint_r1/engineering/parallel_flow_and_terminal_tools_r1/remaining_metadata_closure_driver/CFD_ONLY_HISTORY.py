"""Ready-to-root-review closure preparation; never calls central write APIs.
Default writes /tmp plans only. Root may explicitly stage metadata snapshots
AFTER real point publication/readback; it still emits an UNSIGNED closure.
"""
import argparse,hashlib,importlib.util,json,os,sys
from pathlib import Path
sys.dont_write_bytecode=True
E=Path('/workspace/worktrees/accel-sim-ep-l2-ms20261019-e-eval-v1');P=E/'docs/ep_l2/review_packs/MS20261022_E2_DETACH_ZERO_DIAGNOSTIC_r1/approved_r5_joint_r1'
EXPECTED_HELPER='e619360fd40d6dd506cca3fe2cc1414c1ad32acebcfec9451ae10ed55ee37edc'
def require(ok,m):
 if not ok:raise ValueError(m)
def save(path,data):
 path=Path(path);require(not path.exists(),'never overwrite prior closure candidate');b=(json.dumps(data,indent=2,ensure_ascii=False)+'\n').encode()
 with path.open('xb') as f:f.write(b);f.flush();os.fsync(f.fileno())
 return {'path':str(path.resolve()),'sha256':hashlib.sha256(b).hexdigest()}
def account_control(helper,path,store):
 """Account a true small control body too; no receipt selfallocation fiction."""
 p=Path(path);b=helper.body(p);r=helper.ref(p);version=store/(r['sha256']+p.suffix);target=helper.ACCOUNT/version.name
 if target.exists():
  require(helper.body(target)==b,'immutable controlbody conflict')
  if not version.exists():os.link(target,version);helper.fsync_dir(store)
 else:helper.create_immutable(version,b);os.link(version,target);helper.fsync_dir(helper.ACCOUNT)
 require((version.stat().st_dev,version.stat().st_ino)==(target.stat().st_dev,target.stat().st_ino),'control snapshot/account aliases not truehardlinks')
 return {'original_ref':r,'immutable_ref':helper.ref(version),'accounting_ref':helper.ref(target)}
def prepare(args):
 helper_path=Path(args.helper);require(hashlib.sha256(helper_path.read_bytes()).hexdigest()==EXPECTED_HELPER,'reviewed helper changed')
 sp=importlib.util.spec_from_file_location('r5_meta_closure_reviewed_helper',helper_path);h=importlib.util.module_from_spec(sp);sp.loader.exec_module(h)
 out=Path(args.out).resolve();require(out.is_relative_to(Path('/tmp')) and not out.exists(),'fresh /tmp plan directory only');out.mkdir()
 pointpath=Path(args.point).resolve();reviewpath=Path(args.review).resolve();require(pointpath.is_relative_to(P) and reviewpath.is_relative_to(P),'exact newr5 resultpublication pack only')
 point=h.read(h.ref(pointpath));rb=h.read(h.ref(args.readback));require(rb.get('verified') is True and rb.get('remote_commit')==args.publication,'real root remote verification must already exist; driver will not invent verified=true')
 require(point['attempt_id']=='E056_47abdc7f' and point['workload']=='cfd_097k' and point['status']=='CURRENT_ACCEPTED_DIAGNOSTIC_POINT','this driver is exact CFD acceptedpoint only')
 paths=[];excluded=[]
 for rel in rb['verified_paths']:
  p=(E/rel).resolve();require(p.is_relative_to(E),'verified publication path escapes originaltree')
  if p.suffix.lower() in {'.json','.csv','.md','.txt'}:paths.append(p)
  else:excluded.append({'path':rel,'scope':'nonmetadata/source artifact; root must independently review if resultmetadata is hidden here'})
 for p in (pointpath,reviewpath):require(p in paths,'published point/review absent from actualverified inventory')
 paths=list(dict.fromkeys(paths))
 req={'attempt_id':point['attempt_id'],'publication_commit':args.publication,'publication_remote_readback_ref':h.ref(args.readback),'metadata_refs':[h.ref(p) for p in paths],'point_ref':h.ref(pointpath),'independent_review_ref':point['independent_terminal_review'],'root_complete_metadata_inventory_reviewed':args.complete_inventory_confirmed}
 require(Path(req['independent_review_ref']['path']).resolve()==reviewpath and req['independent_review_ref']['sha256']==h.ref(reviewpath)['sha256'],'exact root independentreview differs')
 require(args.complete_inventory_confirmed,'root must review derived complete inventory and excluded source files')
 h.verified_publication(req)
 requestref=save(out/'CLOSURE_REQUEST.json',req)
 # Large original run_status/terminal_summary remain at their exact OUTPUT
 # locations and hashes in the acceptedpoint/review. No duplicate body copy.
 data=json.loads(h.REGISTRY.read_bytes());item=data[h.FIELD];a=next(a for a in item['attempts'] if a['attempt_id']==req['attempt_id']);accepted=item['accepted_results'][a['attempt_id']]
 require(a['state']=='COMPLETE_VALID' and a['actual_start'] is True,'central exact CFD notaccepted')
 existing=[{'path':accepted['path'],'sha256':accepted['sha256'],'already_in_original_OUTPUT':True,'duplicated_by_this_driver':False}]
 summary=Path(a['result_directory'])/'terminal_summary.json';existing.append({'path':str(summary),'bytes':summary.stat().st_size,'already_in_original_OUTPUT':True,'duplicated_by_this_driver':False,'hash_evidence':'root independentreview exactref; driver does not rehash/parse this largebody'})
 result={'schema':'E2_R5_CFD_METADATA_CLOSURE_DRIVER_PREPARATION_V1','status':'PLAN_ONLY_NO_SNAPSHOT_OR_CLOSE','request_ref':requestref,'derived_published_metadata_refs':req['metadata_refs'],'excluded_nonmetadata':excluded,'existing_complete_runtime_evidence_not_copied':existing,'central_actual_starts':item['actual_starts'],'central_controller_state':item['controller']['state'],'original_API_for_root_only':'Coordinator().close_tagpressure_metadata(final_ref)','central_mutation_by_driver':False}
 if args.root_stage_snapshot:
  store=Path(args.immutable_store).resolve();require(store.is_relative_to(P),'immutable owner store outside approvedr5pack')
  # Root must have original live resource admission for this actual metadata
  # growth; this flag is deliberate execution of snapshots, never app admission.
  require(args.root_metadata_growth_admitted,'root must confirm actual metadata growth fits original currentresource reservation')
  snap=h.snapshot_publication(req,store);snapshotref=save(out/'ACTUAL_PUBLICATION_METADATA_SNAPSHOT.json',snap)
  controls=[account_control(h,args.readback,store),account_control(h,snapshotref['path'],store),account_control(h,requestref['path'],store)]
  candidate=h.closure_candidate(req,snapshotref)
  allpaths=[r['accounting_ref']['path'] for r in snap['records']]+[r['accounting_ref']['path'] for r in controls]
  actual=h.allocated_unique(allpaths)
  candidate.update(actual_metadata_allocated_bytes=actual['allocated_bytes_unique_dev_inode'],metadata_allocation_scope='Published endpointmetadata + actualreadback + snapshotreceipt + closure-request bodies listed in accountingmeasurement. Final signedclosure and laterclose-receipt selfbytes are separately actuallyaccounted before/after originalAPI; this measuredvalue never claims unknown selfallocation.',metadata_accounting_controls=controls,metadata_accounting_measurement=actual)
  cr=save(out/'ROOT_REVIEW_REQUIRED_CLOSURE.json',candidate)
  result.update(status='ACTUAL_METADATA_SNAPSHOT_COMPLETE_UNSIGNED_CLOSURE_READY',snapshot_ref=snapshotref,unsigned_closure_ref=cr,actual_allocated_measured_bytes=actual['allocated_bytes_unique_dev_inode'],next_root_steps=['Review exact unsigned closure and fullinventory; status must remain ROOT_REVIEW_REQUIRED until root signs.','Set finalstatus E_ROOT_INDEPENDENT_POINT_AND_METADATA_CLOSED and root sign; preserve exact requiredfields, no acceptance/input/source changes.','Account final signedclosure body with account_control before calling originalAPI; actual outputgeneration stayscharged.','Original Coordinator.close_tagpressure_metadata({path,sha256}) validates/persists under original registrylock; this driver NEVER invokes it.','Publish closure/APIreceipt/STATUS and real remote-readback; account latercontrolbodies too.','Fresh originalresourcegate for DWT is still mandatory: closure does not release actualdiskspace.'])
 v=os.statvfs('/workspace');df=v.f_bavail*v.f_frsize;threshold=5*2**30+2*2**30+(384+160)*2**20
 result['next_single_endpoint_physical_illustration']={'actual_df_bytes_at_driver_read':df,'minimum_if_no_other_pending_bytes':threshold,'minimum_gap_after_CFD_closure_bytes':max(0,threshold-df),'scope':'Separate5GiB floor+2GiB active monitor+384MiB endpoint+160MiB currentmetadata. Excludes otherpending demand, generation/CPU/RAM/Share; not actualadmission PASS.'}
 save(out/'DRIVER_RESULT.json',result);return result
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--helper',default='/tmp/e2_r5_metadata_closure_helper_candidate.py');ap.add_argument('--point',required=True);ap.add_argument('--review',required=True);ap.add_argument('--readback',required=True);ap.add_argument('--publication',required=True);ap.add_argument('--out',required=True);ap.add_argument('--complete-inventory-confirmed',action='store_true');ap.add_argument('--root-stage-snapshot',action='store_true');ap.add_argument('--root-metadata-growth-admitted',action='store_true');ap.add_argument('--immutable-store',default=str(P/'results/cfd_097k/immutable_metadata_versions'))
 print(json.dumps(prepare(ap.parse_args()),indent=2))
