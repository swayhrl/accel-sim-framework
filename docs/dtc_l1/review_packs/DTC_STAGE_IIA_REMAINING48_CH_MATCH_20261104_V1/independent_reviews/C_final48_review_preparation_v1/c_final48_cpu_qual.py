from pathlib import Path
import importlib.util,sys,json,copy,hashlib,io,tarfile,os,gzip,datetime,subprocess
sys.dont_write_bytecode=True
A=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_stage_iia_remaining48_execution_20261104_v1');P=A/'agents/C_final48_review_preparation_v1';s=importlib.util.spec_from_file_location('C_final48_prepared',P/'final48_readonly_audit.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);F=P/'CPU_FIXTURES';F.mkdir(exist_ok=True);checks=[]
def ck(name,b):checks.append({'check':name,'PASS':bool(b)});assert b,name

def reject(name,fn):
 try:fn()
 except (AssertionError,OSError,tarfile.TarError):ck(name,True);return
 raise AssertionError(name)
points=[{'cohort':'CPU_ONLY_'+str(i)}for i in range(48)];q={'budget':48,'remaining':0,'admitted_specs':{p['cohort']:'CPU_ONLY'for p in points},'consumed':{p['cohort']:{'uuid':'CPU_ONLY_UUID_'+str(i),'charged':1,'execution_receipt':{'CPU_ONLY':True}}for i,p in enumerate(points)}};states={p['cohort']:m.PASS for p in points};g=m.eligibility(points,q,states,[]);ck('Allterminalmetadata onlyreadyforaudit notscientificPASS',g['ready_for_expensive_final_audit']and not g['scientific_acceptance_granted_by_gate'])
for label,mutation in [('remaining',lambda q:q.update(remaining=1)),('wrongbudget',lambda q:q.update(budget=49)),('noDONE',lambda q:q['consumed'][points[0]['cohort']].pop('execution_receipt')),('duplicateUUID',lambda q:q['consumed'][points[0]['cohort']].update(uuid='CPU_ONLY_UUID_1')),('extraGrant',lambda q:q['admitted_specs'].update(UNAUTHORIZED='CPU_ONLY'))]:
 bad=copy.deepcopy(q);mutation(bad);ck(label+' blocksfinalgate',not m.eligibility(points,bad,states,[])['ready_for_expensive_final_audit'])
missing=dict(states);missing.pop(points[0]['cohort']);ck('Missingresult blocksfinalgate',not m.eligibility(points,q,missing,[])['ready_for_expensive_final_audit']);ck('Livegeneration blocksfinalgate',not m.eligibility(points,q,states,[points[0]['cohort']])['ready_for_expensive_final_audit']);hold=dict(states);hold[points[0]['cohort']]='ENGINEERING_HOLD';ck('EngineeringHOLD notforgedterminalnegative',not m.eligibility(points,q,hold,[])['ready_for_expensive_final_audit']);neg=dict(states);neg[points[0]['cohort']]=m.NEGATIVE;g=m.eligibility(points,q,neg,[]);ck('Preservednegative notaccepted andcanrequestfullreview',g['ready_for_expensive_final_audit']and g['accepted']==47 and g['archived_negative']==1)
for name in ['/outside','../outside','a/../../outside']:reject('Unsafe typedpath '+name,lambda name=name:m.relative(name))
for optional in [False,True]:
 root=F/('shape22'if optional else'shape21');source=root/'source';restore=root/'restore';archive=root/'archive';(archive/'chunks').mkdir(parents=True,exist_ok=True);source.mkdir(exist_ok=True);restore.mkdir(exist_ok=True);entries=[];proof=[]
 for name in ['.','cache','checkpoint_files','tmp']:
  (source/name).mkdir(exist_ok=True);(restore/name).mkdir(exist_ok=True);entries.append({'path':name,'type':'directory'});proof.append({'path':name,'type':'directory'})
 for name in ['file_'+str(i)+'.txt'for i in range(16)]+(['OBSERVER_PROC_EXIT_RACE_EVENTS.jsonl']if optional else[]):
  b=('CPU_ONLY_NON_SCIENTIFIC '+name).encode();(source/name).write_bytes(b);(restore/name).write_bytes(b);h=hashlib.sha256(b).hexdigest();entries.append({'path':name,'type':'file','size':len(b),'sha256':h});proof.append({'path':name,'type':'file','sha256':h})
 for r in [source,restore]:
  p=r/'counter.link'
  if not p.is_symlink():p.symlink_to('file_0.txt')
 entries.append({'path':'counter.link','type':'symlink','target':'file_0.txt'});proof.append({'path':'counter.link','type':'symlink','target':'file_0.txt'});manifest={'entries':entries};r=m.typed_tree(source,restore,manifest,{'rows':proof});ck('Actualtypedshape '+str(21+optional)+' nothardcoded',r['entry_count']==21+optional and r['type_counts']['file']==16+optional)
 data=io.BytesIO()
 with tarfile.open(fileobj=data,mode='w')as t:
  for entry in entries:
   info=tarfile.TarInfo(entry['path'])
   if entry['type']=='directory':info.type=tarfile.DIRTYPE;t.addfile(info)
   elif entry['type']=='symlink':info.type=tarfile.SYMTYPE;info.linkname=entry['target'];t.addfile(info)
   else:b=(source/entry['path']).read_bytes();info.size=len(b);t.addfile(info,io.BytesIO(b))
 blob=data.getvalue();chunks=[]
 for i,offset in enumerate(range(0,len(blob),4096)):
  part=blob[offset:offset+4096];name=str(i)+'.part';(archive/'chunks'/name).write_bytes(part);chunks.append({'name':name,'offset':offset,'size':len(part),'sha256':hashlib.sha256(part).hexdigest()})
 index={'chunks':chunks,'archive_sha256':hashlib.sha256(blob).hexdigest(),'archive_bytes':len(blob)};r=m.archive_stream(archive,manifest,index);ck('AllTAR members andmultiple chunkboundaries '+str(21+optional),r['tar_member_count']==21+optional and len(r['chunks'])==len(chunks))
 (restore/'file_0.txt').write_text('CORRUPTED_CPU_FIXTURE');reject('RestoredfileSHA drift '+str(optional),lambda:m.typed_tree(source,restore,manifest,{'rows':proof}));(restore/'file_0.txt').write_bytes((source/'file_0.txt').read_bytes());part=archive/'chunks'/chunks[0]['name'];b=part.read_bytes();part.write_bytes(bytes([b[0]^1])+b[1:]);reject('Corruptarchive chunk '+str(optional),lambda:m.archive_stream(archive,manifest,index))
# Actualgate execution is deliberatelymetadata-only; it must not certifyfinal.
out=P/('ACTUAL_PENDING_GATE_'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'));subprocess.run([sys.executable,'-B',str(P/'final48_readonly_audit.py'),'--mode','gate','--output-dir',str(out)],check=True,capture_output=True,text=True);gate=json.loads((out/'STATUS.json').read_text());ck('Actualgate nofinalclaim andnolive raw',gate['final_review_complete']is False and gate['live_raw_read']is False)
ck('OnlyC-owned freshoutput scope allowed',m.output_allowed(P/'runs/future')and m.output_allowed(A/'agents/C_final48_independent_audits_v1/future'))
ck('Outputdotdot escape blocked',not m.output_allowed(P/'../OUTSIDE'))
ck('Otheragent outputscope blocked',not m.output_allowed(A/'agents/B_runtime_analysis_v1/future'))
report={'schema':'C_FINAL48_AUDIT_PREPARATION_CPU_QUALIFICATION_V1','UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'PASS_PREPARATION_ONLY_NOT_FINAL48','checks':checks,'validator_sha256':m.sha(P/'final48_readonly_audit.py'),'privatefixtures':'ExplicitCPU_ONLY no scientific raw/results/identities fabricated','actualgate_status':gate,'actual_model_or_owner_or_Git_actions':0};(P/'CPU_QUALIFICATION.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'status':report['status'],'checks':len(checks),'sha256':m.sha(P/'CPU_QUALIFICATION.json')}))
