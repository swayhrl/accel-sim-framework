"""Bounded native maps observer. Sampling plus explicit stopped checkpoints, not
a claim that every transient DSO or short-lived descendant has been observed."""
import hashlib,json,os,pathlib,time
P=pathlib.Path
def digest(p):
 h=hashlib.sha256()
 with P(p).open('rb') as f:
  for block in iter(lambda:f.read(2**20),b''):h.update(block)
 return h.hexdigest()
def stat(pid):
 text=(P('/proc')/str(pid)/'stat').read_text(); cols=text.split(') ',1)[1].split()
 return {'pid':pid,'start_ticks':int(cols[19]),'state':cols[0]}
class MapsObserver:
 def __init__(self,primary,pins,out):
  self.primary=primary;self.pins=pins;self.out=P(out);self.out.mkdir(exist_ok=False)
  self.primary_identity=stat(primary);self.identities={};self.union={};self.seen_maps={};self.sample_count=0;self.checkpoints=[]
 def sample(self,label='PERIODIC'):
  pending=[self.primary]; visited=set();now=time.monotonic()
  while pending:
   pid=pending.pop()
   if pid in visited:continue
   visited.add(pid)
   try:
    before=stat(pid)
    if pid==self.primary and before['start_ticks']!=self.primary_identity['start_ticks']:raise RuntimeError('primary PID reused')
    key=str(pid)+':'+str(before['start_ticks'])
    old=self.identities.setdefault(key,before)
    maps=(P('/proc')/str(pid)/'maps').read_text()
    children=(P('/proc')/str(pid)/'task'/str(pid)/'children').read_text()
    after=stat(pid)
    if before['start_ticks']!=after['start_ticks']:raise RuntimeError('PID reuse across maps read')
   except FileNotFoundError:
    self._append({'monotonic':now,'pid':pid,'label':label,'status':'EXIT_RACE'})
    continue
   pending.extend(int(x) for x in children.split())
   paths=set()
   for line in maps.splitlines():
    cells=line.split(None,5)
    if len(cells)<6 or not cells[5].startswith('/'):continue
    path=cells[5].replace('\\040',' ')
    if path.endswith(' (deleted)'):raise RuntimeError('deleted mapped file '+path)
    if path not in self.pins:raise RuntimeError('unfrozen mapped dependency '+path)
    paths.add(path)
    if path not in self.union or label!='PERIODIC':
     actual=digest(path)
     if actual!=self.pins[path]:raise RuntimeError('mapped dependency hash drift '+path)
     self.union.setdefault(path,{'sha256':actual,'first_monotonic':now,'first_pid':pid,'first_start_ticks':before['start_ticks']})
   mh=hashlib.sha256(maps.encode()).hexdigest();changed=self.seen_maps.get(key)!=mh
   sample={'monotonic':now,'pid':pid,'start_ticks':before['start_ticks'],'state':before['state'],'label':label,'maps_sha256':mh,'mapped_files':len(paths),'primary':pid==self.primary}
   if changed or label!='PERIODIC':
    rel='maps_%06d_pid%d_%s.txt'%(self.sample_count,pid,label)
    (self.out/rel).write_text(maps);sample['saved_maps']=rel
   self.seen_maps[key]=mh;self._append(sample);self.sample_count+=1
   if pid==self.primary and label!='PERIODIC':
    self.checkpoints.append(dict(sample,paths=sorted(paths)))
  self._save_union()
 def _append(self,row):
  with (self.out/'SAMPLES.jsonl').open('a') as f:f.write(json.dumps(row,sort_keys=True)+'\n');f.flush()
 def _save_union(self):
  payload={'scope':'Primary plus descendants present at samples; explicit stopped primary FIRST_ISSUE and TERMINAL checkpoints. Sampling cannot exclude transient unsampled DSO/processes.','primary_identity':self.primary_identity,'sample_count':self.sample_count,'identities':self.identities,'mapped_dependency_union':self.union,'checkpoints':self.checkpoints}
  dest=self.out/'UNION.json';temp=self.out/'UNION.tmp';temp.write_text(json.dumps(payload,indent=2)+'\n');os.replace(temp,dest)
 def require_terminal(self):
  labels=[x['label']for x in self.checkpoints]
  if labels!=['FIRST_ISSUE','TERMINAL']:raise RuntimeError('missing/reordered explicit issue/terminal maps '+repr(labels))
  if any(x['state'] not in ('T','t')for x in self.checkpoints):raise RuntimeError('checkpoint not stopped')
  return {'sample_count':self.sample_count,'union_paths':len(self.union),'checkpoint_labels':labels,'primary_identity':self.primary_identity,'scope':'SAMPLED_WITH_TWO_EXPLICIT_HOST_STOPS_NOT_ALL_TRANSIENT_DEPENDENCIES'}
