#!/usr/bin/env python3
"""Strict streaming EPL2LIFEV1 analysis; never grants scientific acceptance."""
import sys
sys.dont_write_bytecode = True
import argparse,array,csv,hashlib,json,pathlib,re
P=pathlib.Path
HERE=P(__file__).resolve().parent
U64=(1<<64)-1
class InvalidWire(ValueError):pass
def need(ok,why):
 if not ok:raise InvalidWire(why)
def uint(text):
 need(re.fullmatch(r'0|[1-9][0-9]*',text) is not None,'noncanonical uint '+str(text)[:50])
 n=int(text);need(n<=U64,'uint64 overflow');return n
def vec(text,n):
 p=text.split(',');need(len(p)==n,'array cardinality mismatch');return [uint(x) for x in p]
def record(line,k):
 need(line.endswith(b'\n') and len(line)<=6144,'truncated/oversized lifetime record')
 try:p=line[:-1].decode('ascii').split('|')
 except UnicodeDecodeError:raise InvalidWire('non-ASCII lifetime record')
 need(len(p)>=3 and p[0]=='EPL2LIFEV1','bad record prefix')
 kind=p[1];need(kind in k['record_fields'],'unknown record kind '+kind);d={}
 for token in p[2:]:
  need(token.count('=')==1,'bad key=value');name,value=token.split('=',1)
  need(name not in d and value!='','duplicate/empty field');d[name]=value
 need(set(d)==set(k['record_fields'][kind]),'unknown/missing '+kind+' fields')
 return kind,d
def histogram(h,count,total,maximum,end):
 need(sum(h)==count,'histogram population mismatch')
 need(maximum<=end,'maximum exceeds observed epoch')
 if not count:
  need(total==maximum==0,'empty histogram has lifetime');return
 top=max(i for i,n in enumerate(h) if n)
 need(min(maximum.bit_length(),32)==top,'histogram maximum bucket mismatch')
 low=sum(n*(0 if i==0 else 1<<(i-1)) for i,n in enumerate(h))
 high=sum(n*min(end,0 if i==0 else ((1<<i)-1 if i<32 else U64)) for i,n in enumerate(h))
 need(low<=total<=high and maximum<=total<=count*maximum,'histogram lifetime sum bounds')
class Slice:
 def __init__(self,nstage):
  self.end=0;self.last_width=None;self.pending=None;self.nwindows=0;self.meta=None;self.sets=set();self.stage=None;self.ended=False
  self.incarnations=set();self.examples=0;self.ordinal=0;self.stage_sum=[0]*nstage;self.first_gpu=None;self.last_gpu=None
  self.ro_admit=self.ro_retire=self.ro_time=self.ro_phase=self.ro_ready=0
class Parser:
 def __init__(self,k,sf,wf,nslices):
  self.k=k;self.N=nslices;self.S=k['sets'];self.A=k['ways'];self.C=k['counters'];self.WC=k['window_counters'];self.ST=k['stages']
  self.ci={x:i for i,x in enumerate(self.C)};self.wi={x:i for i,x in enumerate(self.WC)}
  self.slice=[Slice(len(self.ST)) for _ in range(nslices)];self.stride=self.A+1+len(self.WC)
  self.sums=array.array('Q',[0])*(nslices*self.S*self.stride)
  self.initial=array.array('B',[0])*(nslices*self.S);self.final=array.array('B',[0])*(nslices*self.S)
  self.inc_fields=k['incarnation_stats']+[f'head_reserved_R{i}' for i in range(17)]+[f'unique_reserved_R{i}' for i in range(17)]
  self.inc=array.array('Q',[0])*(nslices*self.S*len(self.inc_fields))
  self.join_fields=['NEW_HEAD','NEW_UNIQUE','INC_END','REQUESTER','MERGE','ALLOC','LEFT','EVENT_PEAK','NEW_WITH_PENDING','NEW_PENDING_SECTORS_SUM']+[f'NEW_AT_{i}' for i in [2,3,4,8,12,15,16]]
  self.joins=array.array('Q',[0])*(nslices*self.S*len(self.join_fields))
  self.set_fields=['slice','set','begin','end','unit','coverage']+[f'area_R{i}' for i in range(self.A+1)]+self.C
  self.set_fields += [f'new_hist_b{i}' for i in range(k['bins'])]+[f're_hist_b{i}' for i in range(k['bins'])]
  self.set_fields += ['pending_sectors_end','structural_eligible_end','weighted_R_area','end_reserved','mean_reserved','censoring_present']+self.inc_fields
  self.window_fields=['slice','set','begin','end','unit','begin_gpu','end_gpu','gpu_unit','stage_scope','stage_context_repeated','reserved_begin_pre_boundary','reserved_end_pre_boundary','carry_origin']
  self.window_fields += [f'area_R{i}' for i in range(self.A+1)]+self.WC+['stage_'+x for x in self.ST]
  self.sw=csv.writer(sf,lineterminator='\n');self.ww=csv.writer(wf,lineterminator='\n');self.sw.writerow(self.set_fields);self.ww.writerow(self.window_fields)
  self.counts={};self.wire_bytes=0;self.state_sizes=[];self.nsets=self.nwindows=0
 def consume(self,kind,d,nbytes):
  self.counts[kind]=self.counts.get(kind,0)+1;sid=uint(d['slice']);need(sid<self.N,'slice outside expected domain');s=self.slice[sid]
  need(not s.ended,'record after slice END')
  if 'invalid' in d:need(uint(d['invalid'])==0,'observer invalid flag')
  if kind=='WINDOW_SET':
   need(s.meta is None,'window after META');si=uint(d['set']);b=uint(d['begin']);e=uint(d['end'])
   need(si<self.S and b==s.end and 0<e-b<=self.k['window'],'bad window range')
   if s.pending is None:
    need(s.last_width is None or s.last_width==self.k['window'],'nonterminal window is not full width')
    s.pending={'begin':b,'end':e,'rows':{}}
   q=s.pending;need((b,e)==(q['begin'],q['end']) and si not in q['rows'],'duplicate/interleaved set window')
   a=vec(d['area'],self.A+1);c=vec(d['c'],len(self.WC));need(sum(a)==e-b,'window area partition fails')
   cv=dict(zip(self.WC,c));need(cv['NEW_UNIQUE']<=cv['NEW_HEAD'] and cv['RAW_FAIL_HEAD']<=cv['NEW_HEAD'],'window requester populations contradict')
   for n in ['NEW_WITH_PENDING','NEW_WITH_ELIGIBLE']:need(cv[n]<=cv['NEW_UNIQUE'],'window joint count exceeds unique newTag')
   q['rows'][si]=(a,c);base=(sid*self.S+si)*self.stride
   for i,v in enumerate(a+c):need(self.sums[base+i]<=U64-v,'window sum overflow');self.sums[base+i]+=v
  elif kind=='WINDOW_STAGE':
   need(s.meta is None and s.pending is not None,'stage without pending window');b=uint(d['begin']);e=uint(d['end']);q=s.pending
   need((b,e)==(q['begin'],q['end']) and len(q['rows'])==self.S,'incomplete set-window population')
   c=vec(d['c'],len(self.ST));need(sum(row[1][self.wi['RO_READY_ADD']] for row in q['rows'].values())==c[self.ST.index('RO_READY_EVENT')],'window RO ready-sector/event mismatch');bg=uint(d['begin_gpu']);eg=uint(d['end_gpu']);need(eg>=bg,'backward physical GPU window')
   if s.first_gpu is None:s.first_gpu=bg
   if s.last_gpu is not None:need(bg==s.last_gpu,'physical GPU window discontinuity')
   s.last_gpu=eg
   for i,v in enumerate(c):need(s.stage_sum[i]<=U64-v,'stage sum overflow');s.stage_sum[i]+=v
   for si in range(self.S):
    a,w=q['rows'][si];self.ww.writerow([sid,si,b,e,self.k['unit'],bg,eg,self.k['gpu_unit'],'slice_window',1,'','','']+a+w+c);self.nwindows+=1
   s.end=e;s.last_width=e-b;s.nwindows+=1;s.pending=None
  elif kind=='META':
   need(s.meta is None and s.pending is None,'duplicate META/unclosed window');m={k:(v if k in ['unit','gpu_unit','bin32','scope'] else uint(v)) for k,v in d.items()}
   for key,value in [('sets',self.S),('ways',self.A),('sectors',4),('window',self.k['window']),('bins',self.k['bins']),('begin',0),('closed',1),('unit',self.k['unit']),('gpu_unit',self.k['gpu_unit']),('bin32','ge2pow31'),('scope',self.k['scope'])]:need(m[key]==value,'META mismatch '+key)
   need(m['end']==s.end and s.end>0,'META terminal/window mismatch')
   need(s.nwindows==(s.end+self.k['window']-1)//self.k['window'],'wrong number of windows')
   need(s.first_gpu==m['begin_gpu'] and s.last_gpu==m['end_gpu'],'META physical anchors mismatch')
   need(0<m['state_bytes']<self.k['state_limit'],'invalid state size');self.state_sizes.append(m['state_bytes']);s.meta=m
  elif kind=='SET':
   need(s.meta is not None and s.stage is None,'SET requires META before STAGE');si=uint(d['set']);need(si<self.S and si not in s.sets,'bad/duplicate SET')
   a=vec(d['area'],self.A+1);c=vec(d['c'],len(self.C));nh=vec(d['new_hist'],self.k['bins']);rh=vec(d['re_hist'],self.k['bins']);v=dict(zip(self.C,c));e=s.end
   pending=uint(d['pending']);eligible=uint(d['eligible']);need(sum(a)==e,'summary area partition fails');weighted=sum(i*x for i,x in enumerate(a));need(weighted<=U64,'weighted area overflow')
   need(weighted==sum(v[n] for n in ['SUM_NEW','SUM_RE','SUM_LEFT','SUM_RIGHT']),'censor duration conservation fails')
   need(v['LEFT']+v['ENTER']>=v['EXIT'],'reservation balance underflow');rend=v['LEFT']+v['ENTER']-v['EXIT']
   need(rend==v['RIGHT'] and rend<=self.A and v['LEFT']<=self.A,'end occupancy population fails')
   self.initial[sid*self.S+si]=v['LEFT'];self.final[sid*self.S+si]=rend
   need(v['EXIT']==v['CLOSED_NEW']+v['CLOSED_RE']+v['CLOSED_LEFT'],'EXIT closed populations mismatch')
   need(v['REENTER']<=v['ENTER'] and v['CLOSED_RE']<=v['REENTER'] and v['CLOSED_NEW']<=v['ENTER']-v['REENTER'] and v['CLOSED_LEFT']<=v['LEFT'],'episode classification imbalance')
   need(rend<=pending<=4*rend and eligible<=self.A,'terminal pending/eligible bounds')
   need(v['TICK_PEAK']<=v['EVENT_PEAK']<=self.A,'invalid peaks')
   need(max(i for i,n in enumerate(a) if n)<=v['EVENT_PEAK'],'area occupancy exceeds event peak')
   need(v['NEW_UNIQUE']<=v['NEW_HEAD'] and v['RAW_FAIL_HEAD']<=v['NEW_HEAD'] and v['MERGE']<=v['REQUESTER'],'requester populations contradict')
   need(sum(v[n] for n in self.C if n.startswith('NEW_AT_'))<=v['NEW_UNIQUE'],'newTag threshold count overcount')
   for n in ['NEW_WITH_PENDING','NEW_WITH_ELIGIBLE']:need(v[n]<=v['NEW_UNIQUE'],'joint count exceeds unique newTag')
   histogram(nh,v['CLOSED_NEW'],v['SUM_NEW'],v['MAX_NEW'],e);histogram(rh,v['CLOSED_RE'],v['SUM_RE'],v['MAX_RE'],e)
   need(v['MAX_LEFT']<=e and v['MAX_LEFT']<=v['SUM_LEFT']<=v['CLOSED_LEFT']*v['MAX_LEFT'],'left-censor sum/max bounds')
   need(v['WAIT_COUNT']<=v['NEW_UNIQUE'] and v['WAIT_COUNT']<=v['NEW_COMMIT'],'wait completion population exceeds new offers/commits')
   need(v['WAIT_MAX']<=e and v['WAIT_MAX']<=v['WAIT_SUM']<=v['WAIT_COUNT']*v['WAIT_MAX'],'wait sum/max bounds')
   joinbase=(sid*self.S+si)*len(self.join_fields)
   for i,name in enumerate(self.join_fields):self.joins[joinbase+i]=v[name]
   base=(sid*self.S+si)*self.stride;need(list(self.sums[base:base+self.A+1])==a,'window/summary area mismatch')
   for wn,cn in self.k['window_mapping'].items():need(self.sums[base+self.A+1+self.wi[wn]]==v[cn],'window/summary '+wn+' mismatch')
   need(v['RO_INITIAL_READY']<=4*v['RO_ADMIT'],'initial resident-ready bits exceed RO birth population')
   s.ro_ready+=v['RO_READY_ADD'];s.ro_admit+=v['RO_ADMIT'];s.ro_retire+=v['RO_RETIRE'];s.ro_time+=v['RO_TIME'];s.ro_phase+=v['RO_LOWER_TIME']+v['RO_RESPONSE_ONLY_TIME']
   self.sw.writerow([sid,si,0,e,self.k['unit'],'complete_timed_epoch']+a+c+nh+rh+[pending,eligible,weighted,rend,weighted/e,int(bool(v['LEFT'] or v['RIGHT']))]+['']*len(self.inc_fields));self.nsets+=1;s.sets.add(si)
  elif kind=='INCARNATION':
   need(s.meta is not None and len(s.sets)==self.S and s.stage is None,'INCARNATION requires all SET before STAGE')
   si=uint(d['set']);need(si<self.S and si not in s.incarnations,'duplicate/bad INCARNATION set')
   stats=vec(d['stats'],16);heads=vec(d['head_reserved'],17);unique=vec(d['unique_reserved'],17)
   base=(sid*self.S+si)*len(self.join_fields);v={name:self.joins[base+i] for i,name in enumerate(self.join_fields)}
   need(sum(heads)==v['NEW_HEAD'] and sum(unique)==v['NEW_UNIQUE'],'reserved joint populations mismatch')
   need(all(u<=h for u,h in zip(unique,heads)),'unique reserved joint exceeds head exposure')
   for i in [2,3,4,8,12,15,16]:need(unique[i]==v[f'NEW_AT_{i}'],'NEW_AT joint mismatch')
   need(sum(unique[1:])==v['NEW_WITH_PENDING'],'newTag pending incidence differs from reserved joint')
   weighted=sum(i*n for i,n in enumerate(unique));need(weighted<=v['NEW_PENDING_SECTORS_SUM']<=4*weighted,'newTag pending-sector sum bounds')
   need(max([i for i,n in enumerate(heads) if n]+[0])<=v['EVENT_PEAK'],'joint pressure exceeds observed event peak')
   for b in [0,8]:
    count,carry,requests,rmax,merges,mmax,sectors,smax=stats[b:b+8]
    need(carry<=count,'incarnation carry exceeds population')
    need((count>0 or not any(stats[b+1:b+8])),'empty incarnation population has statistics')
    need(rmax<=requests<=count*rmax and mmax<=merges<=count*mmax,'incarnation sum/max bounds')
    need(smax<=4 and smax<=sectors<=count*smax,'incarnation requested-sector bounds')
    need(merges<=requests and mmax<=rmax,'incarnation merges exceed requesters')
   need(stats[0]==v['INC_END'] and stats[8]<=self.A,'incarnation closed/right population mismatch')
   need(stats[0]-stats[1]+stats[8]-stats[9]==v['ALLOC'],'timed incarnation allocation balance fails')
   need(v['LEFT']<=stats[1]+stats[9]<=self.A,'carry incarnation population invalid')
   need(stats[2]+stats[10]==v['REQUESTER'] and stats[4]+stats[12]==v['MERGE'],'incarnation observed requester/merge totals mismatch')
   base=(sid*self.S+si)*len(self.inc_fields)
   for i,value in enumerate(stats+heads+unique):self.inc[base+i]=value
   s.incarnations.add(si)
  elif kind=='STAGE':
   need(s.meta is not None and len(s.sets)==self.S and len(s.incarnations)==self.S and s.stage is None,'STAGE ordering/population');c=vec(d['c'],len(self.ST));need(c==s.stage_sum,'stage-window summary mismatch');need(c[self.ST.index('RO_READY_EVENT')]==s.ro_ready,'RO ready-sector/stage mismatch')
   right=uint(d['ro_right_count']);rtime=uint(d['ro_right_time']);need(s.ro_admit==s.ro_retire+right,'RO population balance fails');need(s.ro_phase<=s.ro_time+rtime,'RO phase exposure exceeds total lifetime');s.stage=c
  elif kind=='CASE':
   need(s.stage is not None and s.examples<8,'CASE ordering/bound');v={k:uint(v) for k,v in d.items()}
   need(v['tick']<=s.end and v['index']<self.S*self.A and v['old']<=15 and v['new']<=15 and v['reason']<10,'CASE enum/index/time')
   need(s.meta['begin_gpu']<=v['gpu']<=s.meta['end_gpu'],'CASE physical GPU time outside epoch')
   need(v['ordinal']>s.ordinal,'CASE ordering');s.ordinal=v['ordinal'];s.examples+=1
  elif kind=='END':
   need(s.meta is not None and s.stage is not None and s.pending is None,'END before complete slice')
   need(uint(d['closed'])==1 and uint(d['output_overflow'])==0 and uint(d['output_error'])==0,'END closed/overflow/IO error')
   need(uint(d['global_output_bytes'])==self.wire_bytes,'global output byte counter mismatch');s.ended=True
  self.wire_bytes+=nbytes;need(self.wire_bytes<=self.k['output_limit'],'wire exceeds output cap')
 def finish(self):
  need(all(s.ended for s in self.slice),'missing terminal slice END');need(self.nsets==self.N*self.S,'SET population mismatch');need(len(set(self.state_sizes))==1,'state layout differs')
  need(sum(self.state_sizes)+(2<<20)<self.k['state_limit'],'observer fixed memory exceeds budget')
  return {'parser_status':'VALID_OBSERVER_WIRE_ONLY','scientific_acceptance_granted':False,'slices':self.N,'sets_per_slice':self.S,'summary_rows':self.nsets,'window_rows':self.nwindows,'wire_bytes':self.wire_bytes,'frame_counts':self.counts,'typed_array_bytes':sum(len(a)*a.itemsize for a in [self.sums,self.inc,self.joins,self.initial,self.final]),'declared_observer_state_bytes':sum(self.state_sizes),'stage_join_scope':'same_slice_same_window_time_correlation_no_request_ancestry'}
def analyze(raw,outdir,contract_path=HERE/'wire_contract.json',expected_slices=64,synthetic=False):
 cp=P(contract_path);k=json.loads(cp.read_bytes());snapshot=cp.parent/k['header_snapshot'];need(hashlib.sha256(snapshot.read_bytes()).hexdigest()==k['header_sha256'],'contract/header SHA mismatch')
 need(expected_slices==k['slices'] or synthetic,'smaller slice domain requires explicit synthetic mode')
 out=P(outdir);need(not out.exists(),'output directory must be fresh');out.mkdir(parents=True)
 sp=out/'PER_SET_RESERVATION_SUMMARY.csv.partial';wp=out/'PER_SET_TEMPORAL_WINDOWS.csv.partial';digest=hashlib.sha256()
 with sp.open('w',newline='') as sf,wp.open('w',newline='') as wf,P(raw).open('rb') as stream:
  p=Parser(k,sf,wf,expected_slices)
  for number,line in enumerate(stream,1):
   digest.update(line)
   if line.startswith(b'EPL2LIFEV1|'):
    try:kind,d=record(line,k);p.consume(kind,d,len(line))
    except InvalidWire as error:raise InvalidWire(f'line{number}: {error}') from error
  result=p.finish()
 need(sp.stat().st_size+wp.stat().st_size<=16<<20,'CSV byte bound exceeded')
 result.update(parser_sha256=hashlib.sha256(P(__file__).read_bytes()).hexdigest(),raw_sha256=digest.hexdigest(),header_sha256=k['header_sha256'],contract_sha256=hashlib.sha256(cp.read_bytes()).hexdigest(),synthetic_fixture=synthetic)
 # Finalize carry columns from epoch LEFT + each actual window transition count.
 # This second pass reads our bounded CSV spool, never the bulk/raw input again.
 current=array.array('i',p.initial)
 carried=out/'PER_SET_TEMPORAL_WINDOWS.csv.carried.partial'
 with wp.open(newline='') as source,carried.open('w',newline='') as target:
  reader=csv.DictReader(source);writer=csv.DictWriter(target,fieldnames=p.window_fields,lineterminator='\n');writer.writeheader()
  for row in reader:
   slot=int(row['slice'])*p.S+int(row['set']);before=current[slot];after=before+int(row['ENTER'])-int(row['EXIT'])
   need(0<=before<=p.A and 0<=after<=p.A,'window carry outside associativity')
   row.update(reserved_begin_pre_boundary=before,reserved_end_pre_boundary=after,carry_origin='epoch_LEFT_plus_observed_transitions')
   writer.writerow(row);current[slot]=after
 need(list(current)==list(p.final),'window carries do not reach summary RIGHT')
 need(sp.stat().st_size+carried.stat().st_size<=16<<20,'final CSV byte bound exceeded')
 joined=out/'PER_SET_RESERVATION_SUMMARY.csv.joined.partial'
 with sp.open(newline='') as source,joined.open('w',newline='') as target:
  reader=csv.DictReader(source);writer=csv.DictWriter(target,fieldnames=p.set_fields,lineterminator='\n');writer.writeheader()
  for row in reader:
   base=(int(row['slice'])*p.S+int(row['set']))*len(p.inc_fields)
   for i,name in enumerate(p.inc_fields):row[name]=p.inc[base+i]
   writer.writerow(row)
 need(joined.stat().st_size+carried.stat().st_size<=16<<20,'final joined CSV bound exceeded')
 joined.rename(sp.with_suffix(''));carried.rename(wp.with_suffix(''))
 # Keep the .partial spool as clearly non-authoritative engineering evidence.
 result['window_carry_semantics']='pre-boundary state; events belong to [begin,end)'
 result['temporal_lifetime_scope']='total R overlap only; per-kind per-window overlap not emitted'
 result['stage_units']=k['stage_units'];result['stage_unit_boundary']=k['stage_unit_boundary']
 result['counter_semantics']={'NEW_CAN_DETACH_SUM':'structural eligibility count sum, not production can_detach consultations','WAIT_SUM':'completed newTag requester wait, assigned to completion window; not wall stall cycles','INCARNATION':'Tag owner incarnation, observed requester/merge/sector touches only; not DRAM packet savings','RO_INITIAL_READY':'resident-ready bits at RO birth; excludes lower return and post-birth RO_READY_ADD/RO_READY_EVENT'}
 (out/'OBSERVER_WIRE_VALIDATION.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
 (out/'CSV_SCHEMAS.json').write_text(json.dumps({'summary':p.set_fields,'windows':p.window_fields,'provenance':'OBSERVER_WIRE_VALIDATION.json','stage_context_dedup_key':['slice','begin','end'],'rows_not_independent_samples':True,'stage_units':k['stage_units'],'stage_unit_boundary':k['stage_unit_boundary']},indent=2)+'\n')
 return result
if __name__=='__main__':
 a=argparse.ArgumentParser(description=__doc__);a.add_argument('--raw',required=True);a.add_argument('--out-dir',required=True);a.add_argument('--contract',default=str(HERE/'wire_contract.json'));a.add_argument('--expected-slices',type=int,default=64);a.add_argument('--synthetic',action='store_true');z=a.parse_args()
 try:print(json.dumps(analyze(z.raw,z.out_dir,z.contract,z.expected_slices,z.synthetic),sort_keys=True,indent=2))
 except (InvalidWire,OSError,ValueError,KeyError) as error:print(json.dumps({'parser_status':'REJECTED','reason':str(error),'scientific_acceptance_granted':False}),file=sys.stderr);sys.exit(2)
