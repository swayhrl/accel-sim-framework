"""Read-only actual P1 cost and TP validity checks; no modeled decision."""
import gzip,json,pathlib
P=pathlib.Path;GEOMETRY_SHA='e9869eddb1c5d7c497f45f4cd19e08ba3b687fbd843704d8debf09bc042147b6'
def need(x,m):
 if not x:raise ValueError(m)
def op(p):return gzip.open(p,'rt',errors='strict')if str(p).endswith('.gz')else P(p).open(errors='strict')
def tp_census(r):
 c=r['counters'];h=r['histograms'];covered=c['covered'];need(type(covered)is int and 0<=covered<2**64,'TP covereduint64');need(c['observed_heads']==covered+c['probe_skipped'],'TP observed/covered/skipped closure');need(c['ro_observed']==covered and c['ro_na']==0,'TP M1 runtimepopulation')
 totals={}
 for name,limits in [('heads_raw_reserved',[8,9]),('heads_raw_reserved_eligible',[8,9,9]),('heads_raw_reserved_reasonmask',[8,9,32]),('ways_raw_reserved_predmask',[8,9,8]),('ways_raw_reserved_class',[8,9,4]),('heads_raw_reserved_invalid',[8,9,9])]:
  total=0;seen=set()
  for a in h[name]:
   need(type(a)is list and len(a)==len(limits)+1 and all(type(v)is int and 0<=v<2**64 for v in a),'TP sparseinteger row');need(all(a[i]<bound for i,bound in enumerate(limits))and tuple(a[:-1])not in seen,'TP axes/inactivebin/duplicate');seen.add(tuple(a[:-1]));total+=a[-1]
  totals[name]=total
 need(totals['heads_raw_reserved']==totals['heads_raw_reserved_eligible']==totals['heads_raw_reserved_reasonmask']==totals['heads_raw_reserved_invalid']==covered,'TP headhist populationclosure');need(totals['ways_raw_reserved_class']==covered*8 and totals['ways_raw_reserved_predmask']<=covered*8,'TP wayexposureclosure')
 joint=0;seen=set()
 for a in r['route_joint']:
  need(type(a)is list and len(a)==10 and all(type(v)is int and v>=0 for v in a),'TP routejointinteger');need(all(a[i]<bound for i,bound in enumerate([64,18,8,9,3,3,6,2,6]))and a[5]in[1,2]and tuple(a[:-1])not in seen,'TP routejointaxes/duplicate');seen.add(tuple(a[:-1]));joint+=a[-1]
 need(joint==covered,'TP routejoint coveredclosure')
def audit(raw,s,model):
 current=None;p1={};tp=[];diag=[]
 with op(raw)as f:
  for line in f:
   if line.startswith('gpu_tot_sim_cycle = '):current=int(line.split('=')[1]);p1={}
   if line.startswith('EPL2P1V2|SET_ELIGIBILITY_QUERY|'):
    row=dict(x.split('=',1)for x in line.strip().split('|')[2:]);sid=int(row['slice']);need(current is not None and 0<=sid<64,'P1 clock/slice');need(sid not in p1 or p1[sid]==row,'P1 conflicting samecycle');p1[sid]=row
   if line.startswith('EPL2TAGPRESSUREV1|'):
    row=json.loads(line.split('|',1)[1]);need(row.get('record')!='OUTPUT_INVALID','TP OUTPUT_INVALID');need(row.get('overflow_invalid')is False and row.get('output_invalid')is False and row.get('closure_ok')is True,'TP invalid/overflow/closurefalse');need(row.get('schema_id')=='EPL2_TAGPRESSURE_GEOMETRY_V2_CANDIDATE'and row.get('schema_sha256')==GEOMETRY_SHA,'TP exact16x8 geometry schemaSHA');need(row.get('sets')==16 and row.get('assoc')==8,'TP16x8 geometry');need(row.get('T')is s['T']and row.get('M')is True,'TP formalT/M');need(row.get('ro_runtime')is True,'TP M1 runtime');tp_census(row);tp.append(row)
   if line.startswith('EPL2DETACH_DIAG_V1|'):
    row=json.loads(line.split('|',1)[1]);need(row.get('record')!='OUTPUT_INVALID','DIAG OUTPUT_INVALID');
    if row.get('record')!='SAMPLE':need(row.get('overflow_invalid')is False and row.get('output_invalid')is False and row.get('closure_ok')is True,'DIAG invalid/overflow/closurefalse')
    diag.append(row)
 need(set(p1)==set(range(64)),'exact64 final P1 cost records required')
 ro=model['mechanism_metrics']['full_mechanism_records']['readonly']
 for sid,r in p1.items():
  need(int(r['enabled'])==int(s['ordinary_ro_tag_relief'])and int(r['T'])==int(s['T']),'P1 actualmode enabled/T')
  need(r['population']=='ordinary_raw_full_frontend_head'and r['shared_with']=='RO_frontend_query'and r['physical_timing_and_PPA']=='UNKNOWN','P1 population/sharedcost/PPA')
  need(int(r['query_ports_per_slice'])==int(r['query_latency_gpu_cycles'])==1,'P1 port/latency must1')
  values=[int(r[k])for k in ['issued','paid_wait_gpu_cycles','port_wait_attempts']];need(all(v>=0 for v in values),'P1 negativecounter')
  if not s['ordinary_ro_tag_relief']or not s['T']:need(values==[0,0,0],'disabled P1 performedwork')
  resource=ro[sid if sid in ro else str(sid)]['resource']
  need(all(int(r[a])<=int(resource[b])for a,b in [('issued','query_count'),('paid_wait_gpu_cycles','query_wait_cycles'),('port_wait_attempts','query_port_wait_attempts')]),'P1 ordinarysubset exceeds sharedRO querycost')
 on=s.get('observer_profile')=='T3_DIAG_ON'
 if on:
  need(tp and diag,'T3 diagnosticON missingTP/DIAG')
  last=max(int(r['cycle'])for r in tp);slices={int(r['slice'])for r in tp if r.get('record')=='SLICE'and int(r['cycle'])==last and r.get('epoch_closed')is True};need(slices==set(range(64)),'TP final exact64slice closed census')
  need(any(r.get('record')=='GLOBAL'and r.get('slice')==64 and r.get('epoch_closed')is True and int(r['cycle'])==last for r in tp),'TP finalGLOBAL closed')
 else:need(not tp and not diag,'fourOFF diagnosticwire')
 return dict(P1_final_slices=64,P1_cost_contract='validated1port1cycle/ordinary_subset',TP_records=len(tp),diagnostic_records=len(diag),TP_profile='ON_QUALIFIED_GEOMETRY'if on else'OFF_NOT_MEASURED',actual_source_authority='Source5/banner/capsule; historical source_base_core is not currentidentity',strict_demand_unique_NEW='NOT_INSTRUMENTED',later_UID_completion_chain='NOT_MEASURED')
