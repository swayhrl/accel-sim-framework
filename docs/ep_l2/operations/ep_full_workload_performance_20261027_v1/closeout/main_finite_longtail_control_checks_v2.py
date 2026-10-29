import copy,csv,hashlib,importlib.util,io,json,os,pathlib,tempfile,uuid
P=pathlib.Path
src=P('/mnt/d/repo/.codex_ep_finite_background_closeout_v1.py')
s=importlib.util.spec_from_file_location('candidate',src);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
checks=[]
def check(label,fn):
 fn();checks.append(label)
def rejects(fn):
 try:fn()
 except (ValueError,FileNotFoundError):return
 raise AssertionError('Expected closed refusal')
def write(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x))
root=P('/mnt/d/repo/.ep_tail_controller_checks_20261029_v1');root.mkdir(exist_ok=True)
with tempfile.TemporaryDirectory(prefix='owned_',dir=root) as tmp:
 m.J=P(tmp);m.CONTROL=m.J/'control/bg';m.CONFIG=m.CONTROL/'CONFIG.json'
 members=[{'cohort':c,'program':c,'mode':mode,'spec_ref':{'path':str(m.J/c),'sha256':c}} for c,mode in [('A','S'),('B','F'),('C','F')]]
 q={'admitted_specs':{c['cohort']:c['cohort'] for c in members},'remaining':0,'consumed':{c['cohort']:{'state':'CONSUMED_BEFORE_FORK','done_ref':None} for c in members}}
 m.CFG={'longtail':members,'admitted_specs_digest':m.digest(q['admitted_specs'])};write(m.CONFIG,m.CFG)
 class Base:
  GOAL='TEST'
  @staticmethod
  def authority():return {'registered_future_requests':{'TEST':q}},{}
  @staticmethod
  def exact(ref):return {'cycles':100,'instructions':300,'CTA':2,'kernel_count':1,'hardware_drained':True}
  @staticmethod
  def csv_rows(data):return list(csv.DictReader(io.StringIO(data.decode())))
 m.BASE=Base
 check('exact original scope admitted',lambda: m.scoped_request())
 old=q['admitted_specs']['A'];q['admitted_specs']['A']='drift'
 check('new or mutated scientific scope rejected',lambda:rejects(m.scoped_request));q['admitted_specs']['A']=old
 q['remaining']=1;check('new scientific start population rejected',lambda:rejects(m.scoped_request));q['remaining']=0
 before=m.state_fingerprint(q);q['consumed']['A']['done_ref']={'path':'doneA','sha256':'new'}
 check('natural DONE transition detected',lambda: (_ for _ in ()).throw(AssertionError()) if before==m.state_fingerprint(q) else None)
 def files():return {'MATCHED_PERFORMANCE.csv':b'program,S_cohort,F_cohort,S_cycles,F_cycles,speedup_S_over_treatment\nA,A,B,100,100,1\n'}
 status={'terminal_counts':{'CONSUMED_BEFORE_FORK':3},'fully_closed_accepted':0,'all_accepted_profile_pairs':0}
 f=files();x=m.tail_snapshot(q,status,f)
 assert all(r['cycles'] is None for r in x['longtail']) and not x['all3_terminal'];checks.append('pending measurements not imputed')
 assert 'closeout/FINAL_BACKGROUND_COMPLETION.md' not in f;checks.append('DONE without scientific closure not final')
 for c,r in q['consumed'].items():r.update(state='CLOSED_ACCEPTED',done_ref={'path':'done'+c,'sha256':c},accepted_point_ref={'path':'point'+c,'sha256':c},archive_receipt_ref={'path':'archive'+c,'sha256':c})
 status.update(terminal_counts={'CLOSED_ACCEPTED':3},fully_closed_accepted=3,all_accepted_profile_pairs=1)
 f=files();x=m.tail_snapshot(q,status,f)
 assert x['all3_terminal'] and len(x['newly_available_matched_pairs'])==1 and 'closeout/FINAL_BACKGROUND_COMPLETION.md'in f;checks.append('accepted completed applications yield final exact table')
 q['consumed']['C']['state']='PARSE_HOLD';f=files();x=m.tail_snapshot(q,status,f)
 assert x['all3_terminal'] and x['longtail'][2]['cycles'] is None;checks.append('terminal parse HOLD preserved without performance value')
 q['consumed']['C']['state']='CLOSED_UNACCEPTED';f=files();x=m.tail_snapshot(q,status,f)
 assert x['all3_terminal'] and x['longtail'][2]['cycles'] is None;checks.append('technical negative preserved without performance value')
 # Analysis freshness must include exact closed point identity, not just count.
 a={'endpoints':[{'cohort':c,'state':r['state'],'spec_ref':{'sha256':c},'point_ref':r.get('accepted_point_ref'),'done_ref':r.get('done_ref'),'archive_ref':r.get('archive_receipt_ref')} for c,r in q['consumed'].items()],'join_holds':[],'live_pair_exclusions':[]}
 ap=m.J/'agent_b/results_analysis_20261028_v1/analysis.json';write(ap,a)
 cp=ap.parent/'CURRENT.json';write(cp,{'files':[{'publish_name':'RESULTS_ANALYSIS_CURRENT.json',**m.ref(ap)}]})
 # actual small-file SHA helper is used; fake Base.exact above only belongs to rendered accepted points.
 assert m.analysis_matches(q);checks.append('matching sealed analysis accepted')
 q['consumed']['A']['accepted_point_ref']={'path':'different','sha256':'different'}
 assert not m.analysis_matches(q);checks.append('same counts with changed point cannot reuse stale analysis')
 out=m.J/'closeout/closed.md';out.parent.mkdir();out.write_text('closed evidence\n')
 mp=m.J/'control/FOREGROUND_PUBLICATION_MANIFEST.json'
 manifest={'schema':'EP_MAIN_FOREGROUND_CLOSEOUT_FILES_V1','goal':'TEST','files':[{'publish_name':'closeout/REPORT.md',**m.ref(out)}]};write(mp,manifest)
 assert m.extra_publication_files()['closeout/REPORT.md']==out.read_bytes();checks.append('curated closed source publication SHA pass')
 out.write_text('changed\n');check('changed publication source SHA refused',lambda:rejects(m.extra_publication_files))
 manifest['files'][0]=dict(m.ref(out),publish_name='closeout/../ESCAPE.md');write(mp,manifest)
 check('publication path traversal rejected',lambda:rejects(m.extra_publication_files))
 outside=m.J/'outside.md';outside.write_text('outside');manifest['files'][0]=dict(m.ref(outside),publish_name='closeout/ESCAPE.md');write(mp,manifest)
 check('source outside Main closeout root rejected',lambda:rejects(m.extra_publication_files))
 ticks=int((P('/proc')/str(os.getpid())/'stat').read_text().rsplit(')',1)[1].split()[19])
 assert m.process_alive(os.getpid(),ticks) and not m.process_alive(os.getpid(),ticks+1);checks.append('controller PID generation verified')
 result={'status':'PURE_CONTROL_PLANE_CHECKS_PASS','checks':checks,'count':len(checks),'controller_ref':m.ref(src),'new_models':0,'registry_writes':0,'Git_operations':0}
 p=root/('RESULT_'+str(uuid.uuid4())+'.json')
 with p.open('x') as f:json.dump(result,f,sort_keys=True,indent=2)
 print(json.dumps({'result_path':str(p),**result}))
