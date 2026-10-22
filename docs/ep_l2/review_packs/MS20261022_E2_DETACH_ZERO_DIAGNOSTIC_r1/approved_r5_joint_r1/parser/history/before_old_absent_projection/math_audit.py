"""Pure source-design arithmetic over decoded r5 scopes; no wire guesses or I/O."""
from collections import defaultdict
U64=(1<<64)-1
DIMS={
 'heads_raw_reserved':(8,17),
 'heads_raw_reserved_eligible':(8,17,17),
 'heads_raw_reserved_reasonmask':(8,17,32),
 'ways_raw_reserved_predmask':(8,17,8),
 'ways_raw_reserved_class':(8,17,4),
 'heads_raw_reserved_invalid':(8,17,17),
 'head_route_joint':(64,18,8,17,3,3,6,2,6),
}
class AuditError(ValueError):pass
def require(ok,message):
 if not ok:raise AuditError(message)
def uint(x,label,maximum=U64):
 require(type(x) is int and 0<=x<=maximum,'invalid integer '+label);return x
def total(values,label):
 n=sum(values);require(n<=U64,'overflow '+label);return n
def sparse(rows,dimensions,label):
 require(isinstance(rows,list),'missing sparse rows '+label);out={}
 for row in rows:
  require(isinstance(row,list) and len(row)==len(dimensions)+1,'bad tuple '+label)
  key=tuple(uint(x,label+' coordinate',d-1) for x,d in zip(row,dimensions));v=uint(row[-1],label+' value')
  require(v>0,'explicit nonpositive sparse value '+label);require(key not in out,'duplicate sparse key '+label);out[key]=v
 return out

def audit_math(record,old212=None):
 """Validate explicit canonical scope. Raises AuditError; never grants acceptance.
 Wire adapter must first validate source/schema/lifecycle/memberships/cap receipts.
 Histograms use explicit empty lists for source-emitted zero. Missing is not NA0.
 """
 require(isinstance(record,dict),'scope is not object')
 for name in ['covered','absent','ro_observed','ro_na'] :uint(record[name],name)
 skips=record['skipped'];require(isinstance(skips,list) and len(skips)==4,'skipped4 required')
 for i,n in enumerate(skips):uint(n,'skipped'+str(i))
 for b in ['T','M','ro_runtime']:require(type(record[b]) is bool,'invalid boolean '+b)
 require(record.get('invalid') is False,'source invalid not false')
 hists={n:sparse(record['histograms'][n],dims,n) for n,dims in DIMS.items()}
 H,E,R,P,C,I,J=(hists[n] for n in DIMS)
 require(len(J)<=65536,'source sparse joint row capacity')
 covered=record['covered'];require(total(H.values(),'covered histogram')==covered,'head coverage partition')
 require(total([record['ro_observed'],record['ro_na']],'RO presence')==covered,'RO observed NA partition')
 require(record['ro_observed']==(covered if record['ro_runtime'] else 0),'runtime population mismatch')
 require(record['ro_na']==(0 if record['ro_runtime'] else covered),'runtime NA mismatch')
 require(total(E.values(),'eligibleheads')==record['ro_observed'],'eligible head partition')
 require(total(R.values(),'reasonheads')==record['ro_observed'],'reason head partition')
 require(total(I.values(),'invalidheads')==covered,'invalid-way head partition')
 require(covered<=U64//16,'overflow covered*16')
 require(total(C.values(),'wayclasses')==16*covered,'head way population')
 require(total(J.values(),'routeheads')==covered,'route head partition')
 covered_members=record.get('members');require(isinstance(covered_members,list),'explicit scope members required')
 members=set()
 for x in covered_members:
  require(isinstance(x,list) and len(x)==2,'bad member');pair=(uint(x[0],'member slice',63),uint(x[1],'member phase',17));require(pair not in members,'duplicate member');members.add(pair)
 require(members,'empty scope population')
 jp=defaultdict(int);jq=defaultdict(int);jreq=[0,0,0]
 for key,n in J.items():
  sid,phase,raw,r,req,elig,route,admit,early=key
  require((sid,phase) in members,'joint tuple outside declared scope')
  require((req==2)==(not record['ro_runtime']),'joint requester runtime NA')
  require((elig==0)==(not record['ro_runtime']),'joint eligibility NA')
  jp[(raw,r)]+=n;jq[(raw,r,elig)]+=n;jreq[req]+=n
 for raw in range(8):
  for r in range(17):
   k=(raw,r);nh=H.get(k,0)
   if raw==3:require(r==16 or nh==0,'raw FAIL requires r16')
   if raw==2:require(r<16 or nh==0,'raw MISS cannot r16')
   es={e:E.get((raw,r,e),0) for e in range(17)}
   rs={m:R.get((raw,r,m),0) for m in range(32)}
   ps={m:P.get((raw,r,m),0) for m in range(8)}
   cs={c:C.get((raw,r,c),0) for c in range(4)}
   ins={i:I.get((raw,r,i),0) for i in range(17)}
   require(sum(ins.values())==nh,'invalid head raw/r projection')
   require(sum(cs.values())==16*nh,'way raw/r population')
   require(cs[0]==r*nh,'reserved weighted head projection')
   require(sum(i*n for i,n in ins.items())==cs[1],'invalid weighted head projection')
   require(cs[1]+cs[2]+cs[3]==(16-r)*nh,'nonreserved weighted head projection')
   live=sum(ps.values());require(live<=16*nh,'liveway population exceeds ways')
   expected=nh if record['ro_runtime'] else 0
   require(sum(es.values())==sum(rs.values())==expected,'RO raw/r population projection')
   if not record['ro_runtime']:require(live==0,'runtimeoff predicate is NA')
   require(sum(e*n for e,n in es.items())==ps[5],'weighted eligible predicate projection')
   eligible_heads=sum(n for e,n in es.items() if e>0)
   require(sum(n for mask,n in rs.items() if mask&1)==eligible_heads,'reason eligible presence joint')
   if record['ro_runtime']:
    reason_way_counts={2:sum(n for mask,n in ps.items() if not mask&1),4:sum(n for mask,n in ps.items() if mask&2),8:sum(n for mask,n in ps.items() if not mask&4),16:16*nh-live}
    for bit,ways in reason_way_counts.items():
     heads=sum(n for mask,n in rs.items() if mask&bit)
     require(heads<=ways<=16*heads,'reason presence and way population bound')
     require(heads<=nh,'reason heads exceed heads')
   require(jp[k]==nh,'route raw/r projection')
   if record['ro_runtime']:
    require(jq[(raw,r,1)]==es[0] and jq[(raw,r,2)]==eligible_heads,'route exact eligible presence projection')
   else:require(jq[(raw,r,0)]==nh,'route NA population')
 if old212 is not None:
  require(isinstance(old212,dict),'old212 scope missing')
  names=('raw_hit','raw_hit_reserved','raw_miss','raw_reservation_fail','raw_sector_miss','raw_mshr_hit','raw_write_allocated','raw_unknown')
  require(uint(old212['observed_heads'],'old observed')==covered+sum(skips),'old/new observed head partition')
  require(uint(old212['probe_skipped'],'old skipped')==sum(skips),'old/new skipped partition')
  for i,n in enumerate(('skip_tvd','skip_ideal','skip_disabled','skip_other')):require(uint(old212[n],'old '+n)==skips[i],'old/new skip reason '+n)
  for raw,n in enumerate(names):require(uint(old212[n],'old '+n)==sum(v for (rr,_),v in H.items() if rr==raw),'old/new raw '+n)
  for i,n in enumerate(('requester_ro_candidate','requester_nonro','requester_ro_runtime_off')):require(uint(old212[n],'old '+n)==jreq[i],'old/new requester '+n)
 return {'status':'MATH_VALID_NOT_QUALIFICATION','covered':covered,'skipped':sum(skips),'observed_heads':covered+sum(skips),'live_way_observations':sum(P.values()),'structural_eligible_way_observations':sum(v for (raw,r,p),v in P.items() if p==5),'operational_eligible_state':'T_ENABLED' if record['T'] else 'NA_T_DISABLED','runtime_RO_state':'OBSERVED' if record['ro_runtime'] else 'NA_RUNTIME_OFF','route_tuple_count':len(J)}
