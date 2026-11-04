from pathlib import Path
import json,hashlib,sys,importlib.util,types,os,copy,datetime
sys.dont_write_bytecode=True
A=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_stage_iia_remaining48_execution_20261104_v1');O=A/'agents/C_execution_qualification_v1';src=A/'agents/A_resource_config_v1/stage2_resources.py';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();rd=lambda p:json.loads(Path(p).read_text());assert sha(src)=='fe4eabca1ce52ac8649051ad201f62cd87211f29aaaad79bc75d4504c66b6def';sp=importlib.util.spec_from_file_location('C_new48_resource_closed_only',src);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);peer=m._peer();b=peer.resources({'request':peer.ORIG,'cohort':'C_CLOSED_METADATA_READONLY'},False);reg,ep=peer.authority();actual=m._closed_known_metadata(peer,reg,b);released={k:v for k,v in actual['proofs'].items()if v['released_future_metadata_bytes']};assert actual['released_future_metadata_bytes']==3*2**30 and len(released)==3 and sum(len(v['points'])for v in released.values())==18
checks=[];request=next(iter(released));F=O/'CPU_CLOSED_METADATA_FIXTURES';F.mkdir(exist_ok=True);pid=os.getpid();ticks=int(Path('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19]);
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,sort_keys=True)+'\n')
def case(name,change=None,writes=None,wbytes=2**30,unknown=False,cache_mutation=False):
 root=F/name;c='CPU_ONLY_NOT_A_SCIENTIFIC_COHORT';uuid='CPU_ONLY_NO_MODEL';out=root/'DTC/run/results'/uuid;ip=root/'control/qualification_ledger'/(c+'.INTENT.json');done={'uuid':uuid,'launcher_wait_returncode':0,'stop_reason':None};write(ip,{'uuid':uuid});write(ip.with_name(c+'.DONE.json'),done);write(out/'NATIVE_EXIT.json',done);write(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json',{'pid':999999999,'start_ticks':1});write(root/'control'/(c+'_ARCHIVE_RECEIPT.json'),{'cohort':c,'status':'ARCHIVE_VERIFIED_AND_RESTORE_VERIFIED_NATIVE_TARGET','source_disposition':'SOURCE_KEEP'});row={'uuid':uuid,'intent_sha256':sha(ip),'execution_receipt':done};q={'state':'CLOSED','remaining':0,'budget':1,'consumed':{c:row},'reserved_write_bytes':2**30};claims={};p=types.SimpleNamespace(ROOTS={}if unknown else{request:root},archived=peer.archived,rss=peer.rss);args={'q':q,'claims':claims,'root':root,'out':out,'c':c,'ip':ip,'row':row}
 if change:change(args)
 if cache_mutation:
  first=m._closed_metadata_scope(p,request,root,q,claims,wbytes,[]);assert first['released_future_metadata_bytes']==2**30
  write(root/'control'/(c+'_ARCHIVE_RECEIPT.json'),{'cohort':c,'status':'NOT_ARCHIVED','source_disposition':'SOURCE_KEEP'})
 v=m._closed_metadata_scope(p,request,root,q,claims,wbytes,[]if writes is None else writes);want=2**30 if name=='complete_exact_closed'else 0;checks.append({'check':name,'PASS':v['released_future_metadata_bytes']==want,'released':v['released_future_metadata_bytes'],'reasons':v['reasons']})
case('complete_exact_closed')
case('state_RUNNING',lambda a:a['q'].update(state='RUNNING'))
case('remaining_positive',lambda a:a['q'].update(remaining=1))
case('budget_not_consumed',lambda a:a['q'].update(budget=2))
case('unspent_claim',lambda a:a['claims'].update(UNSPENT={'anything':1}))
case('nonempty_write_entries',writes=[{'future':1}])
case('not_exact1G',wbytes=2*2**30)
case('unknown_scope',unknown=True)
case('missing_INTENT',lambda a:a['ip'].unlink())
case('missing_DONE',lambda a:a['ip'].with_name(a['c']+'.DONE.json').unlink())
case('EXIT_mismatch',lambda a:write(a['out']/'NATIVE_EXIT.json',{'uuid':'DIFFERENT'}))
case('intent_pin_mismatch',lambda a:a['row'].update(intent_sha256='0'*64))
case('missing_pidmap',lambda a:(a['out']/'NATIVE_SIMULATOR_PID_AND_MAPS.json').unlink())
case('live_pid_generation',lambda a:write(a['out']/'NATIVE_SIMULATOR_PID_AND_MAPS.json',{'pid':pid,'start_ticks':ticks}))
case('changed_receipt_invalidates_cached_positive',cache_mutation=True)
assert all(x['PASS']for x in checks)
res={'schema':'C_NEW48_PRIVATE_CLOSED_METADATA_INDEPENDENT_REVIEW_V1','UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'production_source_sha256':sha(src),'decision':'PASS_PRIVATE_FORECAST_ACCOUNTING_ONLY_NOT_OLD_BUDGET_MUTATION','actual_three_closed_scopes':actual,'actual_scope_count_released':len(released),'actual_archived_nonlive_points':18,'actual_released_future_metadata_bytes':3*2**30,'independent_production_helper_fixture_checks':checks,'all_checks_PASS':True,'notes':['Only3known exactclosed scopes release futuremetadata;allactualdfbytes/oldq/source remain untouched.','Actual certificate rereads q/claims,hashes5closurefiles perpoint,uses immutable-row/fingerprint-cache for exactarchivejoin and rereads PIDgeneration/liveness.','R20pinned base validates knownwritebounds before this privateprojection; unknownforeignEP and allfailedjoins keep conservative accounting.','No actualprepare/run/register/owner callback invoked; CPUfixtures in thisCdirectory are explicitly non-scientific.']};(O/'CLOSED_METADATA_RESOURCE_REVIEW.json').write_text(json.dumps(res,indent=2)+'\n');print(json.dumps({'all_PASS':True,'CPUchecks':len(checks),'actualreleasedGiB':3,'scopes':list(released),'sha256':sha(O/'CLOSED_METADATA_RESOURCE_REVIEW.json')}))

