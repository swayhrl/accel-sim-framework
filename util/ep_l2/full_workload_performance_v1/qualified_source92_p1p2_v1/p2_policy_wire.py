"""Strict bounded Source92 P1/P2 policy wire. No acceptance or source authority."""
import gzip,hashlib,json,re
from pathlib import Path as P
U64=1<<64
POLICY_FIELDS={'slice','bank_ops','same_slot_services_per_CORE_tick','retained_native_identity','caller_ports_unchanged','hardware_P2_throughput_eligible','same_slot_denials'}
TRACKED={'EPL2MSV1|LOCAL_DIAGNOSTIC':'LOCAL','EPL2MSV1|OBSERVER':'OBSERVER','EPL2SERVICEV1|P2_POLICY':'P2'}
def need(x,msg):
 if not x:raise ValueError(msg)
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def opened(raw):
 p=P(getattr(raw,'p',raw));return gzip.open(p,'rb')if p.suffix=='.gz'else p.open('rb')
def fields(line):
 parts=line.strip().split('|');out={}
 for v in parts[2:]:
  need('='in v,'policy malformed field');k,v=v.split('=',1);need(k not in out,'policy duplicate field')
  if re.fullmatch(r'\d+',v):value=int(v);need(value<U64,'policy uint64 overflow');out[k]=value
  else:out[k]=v
 return out
def check_policy_rows(rows,ops,nslices):
 need(type(ops)is int and ops in(1,2)and type(nslices)is int and 0<nslices<=64,'qualified P1/P2 scope')
 expected={(kind,sid)for kind in('LOCAL','OBSERVER')for sid in range(nslices)}
 if ops==2:expected|={('P2',sid)for sid in range(nslices)}
 need(set(rows)==expected,'missing/unexpected exact physical policy scope')
 for sid in range(nslices):
  local=rows['LOCAL',sid];observe=rows['OBSERVER',sid]
  need(observe['enabled']==1 and'measurement'not in observe,'formal MS observer1 required')
  need(local['copy_free']==local['l2_data_free']==0,'normal paid service only')
  need(local['hardware_P1_throughput_eligible']==int(ops==1),'P1 eligibility must match actual bank capacity')
  need(all(local['exempt_'+key]==0 for key in('response','fill','lower_wb','frontend','copy_read','copy_write')),'no physical service exemption')
  if ops==2:
   row=rows['P2',sid];need(set(row)==POLICY_FIELDS,'P2 policy schema changed')
   expected_row=dict(slice=sid,bank_ops=2,same_slot_services_per_CORE_tick=1,retained_native_identity=1,caller_ports_unchanged=1,hardware_P2_throughput_eligible=1)
   need(all(row[k]==v for k,v in expected_row.items()),'P2 same-slot/identity/caller policy changed')
   need(type(row['same_slot_denials'])is int and row['same_slot_denials']>=0,'P2 denial attempt count invalid')
 return True

def scan_policy(raw,ops,nslices=64,synthetic=False):
 """Applications require all64 owners at every complete native clock frame."""
 need(type(synthetic)is bool,'explicit synthetic flag')
 need(synthetic or nslices==64,'application exact64slice scope required')
 rows={};clock=None;records=duplicates=frames=raw_lines=raw_bytes=clock_markers=distinct_clocks=0
 rh=hashlib.sha256();wh=hashlib.sha256();chain=hashlib.sha256();previous_denials={};kinds={'LOCAL':0,'OBSERVER':0,'P2':0};first=None;last=None
 def close():
  nonlocal frames,first,last
  check_policy_rows(rows,ops,nslices)
  if ops==2:
   for sid in range(nslices):
    value=rows['P2',sid]['same_slot_denials']
    need(value>=previous_denials.get(sid,0),'P2 cumulative denial counter regressed')
    previous_denials[sid]=value
  frames+=1;first=clock if first is None else first;last=clock
  chain.update(canonical(dict(frame_ordinal=frames,CORE_cycle=clock,rows=[[k,sid,rows[k,sid]]for k,sid in sorted(rows)]))+b'\n')
 with opened(raw)as f:
  for wire in f:
   raw_lines+=1;raw_bytes+=len(wire);rh.update(wire);line=wire.decode('utf-8')
   m=re.fullmatch(r'gpu_tot_sim_cycle\s*=\s*(\d+)\s*',line)
   if m:
    value=int(m[1]);need(value>0 and(clock is None or value>=clock),'policy native clock invalid/regressed');clock_markers+=1
    # Each producer printStats marker denotes a complete physical snapshot,
    # even when no CORE time elapsed since its predecessor. Never let a
    # later same-clock snapshot fill a deleted earlier owner population.
    if clock is not None:close();rows={}
    if clock is None or clock!=value:distinct_clocks+=1
    clock=value
   prefix='|'.join(line.split('|')[:2])
   if re.match(r'^EPL2SERVICEV[0-9]+\|P2_',line):need(prefix=='EPL2SERVICEV1|P2_POLICY','unknown P2 policy version/kind')
   if prefix not in TRACKED:continue
   need(clock is not None,'policy record lacks native clock');row=fields(line);sid=row.get('slice')
   need(type(sid)is int and 0<=sid<nslices,'policy physicalslice bound')
   key=(TRACKED[prefix],sid);need(key not in rows or rows[key]==row,'conflicting policy records in same CORE clock')
   duplicates+=int(key in rows);rows[key]=row;records+=1;kinds[key[0]]+=1;wh.update(wire)
 need(clock is not None,'policy native clock missing');close()
 return dict(schema='EP_SOURCE92_P1P2_POLICY_WIRE_CENSUS_V1',status='POLICY_COMPONENT_VALIDATED_NOT_APPLICATION_ACCEPTED',bank_ops=ops,slices=nslices,synthetic_component=synthetic,validated_native_snapshot_occurrences=frames,validated_distinct_CORE_clock_frames=distinct_clocks,native_clock_markers=clock_markers,snapshot_population_contract='EACH_NATIVE_PRINTSTATS_OCCURRENCE_INCLUDING_REPEATED_CORE_CLOCK_REQUIRES_ALL_PHYSICAL_OWNERS',first_CORE_cycle=first,final_CORE_cycle=last,raw_lines=raw_lines,raw_logical_bytes=raw_bytes,raw_logical_sha256=rh.hexdigest(),tracked_policy_records=records,identical_duplicate_policy_records=duplicates,record_populations=kinds,wire_sha256=wh.hexdigest(),ordered_frame_chain_sha256=chain.hexdigest(),final_P2_policy_rows={str(s):rows['P2',s]for s in range(nslices)}if ops==2 else'NOT_APPLICABLE_P1_NO_P2_ROWS',P2_denial_unit='REFUSAL_ATTEMPTS_INCLUDING_RETRIES_NOT_CYCLES',max_retained_policy_rows=nslices*(3 if ops==2 else 2),records_discarded_or_filled_with_zero=0,science_granted=False)

def check_cpu_component(raw,ops,nslices=1,synthetic=False):
 """Actual CPU ft_print lacks application clock/catalog: never app validation."""
 need(synthetic is True,'CPU component entry requires explicit synthetic=True')
 rows={};structure={};summary={};census=0
 with opened(raw)as f:
  for wire in f:
   line=wire.decode('utf-8');prefix='|'.join(line.split('|')[:2])
   if re.match(r'^EPL2SERVICEV[0-9]+\|P2_',line):need(prefix=='EPL2SERVICEV1|P2_POLICY','unknown component P2 version/kind')
   if prefix in TRACKED:
    row=fields(line);key=(TRACKED[prefix],row['slice']);need(key not in rows or rows[key]==row,'component duplicate conflict');rows[key]=row;census+=1
   elif prefix.startswith('EPL2STRUCTV1|'):
    row=fields(line);key=(prefix.split('|')[1],row['slice']);need(key not in structure or structure[key]==row,'component structure conflict');structure[key]=row
   elif prefix=='EPL2FTV1|SUMMARY':
    row=fields(line);summary[row['slice']]=row
 check_policy_rows(rows,ops,nslices)
 need(set(structure)=={(k,s)for k in('CONFIG','BANK_PEAK','WB_QUOTA')for s in range(nslices)}and set(summary)==set(range(nslices)),'component actual getter scope')
 for sid in range(nslices):
  c=structure['CONFIG',sid];b=structure['BANK_PEAK',sid];q=structure['WB_QUOTA',sid];s=summary[sid]
  need(c==dict(slice=sid,static_s64=0,physical_slots=1168,resident_nominal=1024,bypass_capacity=128,wb_begin=1152,static_wb_capacity=16,legacy_wbuf=16,bank_count=4,bank_ops_per_physical_cycle=ops,copy_latch_bytes=128),'CPU actual physical getters mismatch')
  need(b['ops_per_physical_cycle']==ops and all(0<=b['bank'+str(i)]<=ops for i in range(4)),'CPU actual bank peak exceeds budget')
  need(q['cap']==q['reserved']==q['live']==0,'CPU WB quota not drained')
  need(s['physical_slots']==1168 and s['role_free']+s['role_resident']+s['role_bypass']+s['wb_slots']==1168,'CPU actual payload role conservation')
  need(s['wb_created']==s['wb_completed']==s['wb_lower_accept']and s['ownership_consistent']==1 and not any(s[k]for k in('wb_live','wb_slots','reserved','read_refs')),'CPU actual WB/ownership/drain')
 return dict(status='ACTUAL_CPU_PRINT_COMPONENT_VALIDATED_NOT_APPLICATION',synthetic_component=True,scope_slices=nslices,bank_ops=ops,policy_rows={f'{k}:{s}':v for(k,s),v in rows.items()},actual_structure={f'{k}:{s}':v for(k,s),v in structure.items()},actual_summary=summary,tracked_policy_records=census,application_clock_catalog_or_scope_inferred=False,science_granted=False)


