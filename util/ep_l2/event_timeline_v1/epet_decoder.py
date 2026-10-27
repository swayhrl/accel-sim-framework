#!/usr/bin/env python3
"""Strict contract-bound EPETV1 wire component. Never grants model acceptance."""
import sys
sys.dont_write_bytecode=True
import base64,hashlib,json,pathlib,re,struct,zlib
P=pathlib.Path;U64=(1<<64)-1;U16=65535;U8=255
META=set('schema schema_sha256 record_bytes endian slices sets ways ring pre post slots state_bytes state_object_bytes aux_state_bound state_cap compressed_cap wire_cap first_core end_core l2_edges dram_edges ordinal notifications untimed_ignored unmapped quiesced new_head_seen frontend_notifications frontend_wait_notifications frontend_admit_decisions frontend_commit_events high_new full_new production_fail trigger_capacity_miss trigger_repeat critical_replaced full_trigger_not_captured production_fail_not_captured replacement_events_discarded replacement_full_new_discarded'.split())
FIELDS={'META':META,'KERNEL':set('uid start_ordinal end_ordinal start_core end_core name_length name_truncated name_hex'.split()),'SNAP':set('slot slice set ways reserved rank trigger_ordinal trigger_uid trigger_address pre post pre_lost post_complete events'.split()),'DATA':set('slot seq data'.split()),'SNAP_END':set('slot events raw_bytes compressed_bytes raw_crc32'.split()),'END':set('completed slots invalid output_overflow output_error compressed_bytes wire_bytes_before_END z_arena_peak closed'.split())}
class InvalidWire(ValueError):pass
def need(ok,msg):
 if not ok:raise InvalidWire(msg)
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def uint(s):
 need(type(s)is str and re.fullmatch('0|[1-9][0-9]*',s)is not None,'noncanonical uint');n=int(s);need(n<=U64,'uint64 overflow');return n
def frame(line):
 need(line.endswith(b'\n')and len(line)<=65536,'truncated/oversized EPET frame')
 try:parts=line[:-1].decode('ascii').split('|')
 except UnicodeDecodeError:raise InvalidWire('nonASCII wire')
 need(len(parts)>=3 and parts[0]=='EPETV1'and parts[1]in FIELDS,'unknown EPET kind');d={}
 for p in parts[2:]:
  need('='in p,'bad field');k,v=p.split('=',1);need(k not in d and v!='','duplicate/empty field');d[k]=v
 need(set(d)==FIELDS[parts[1]],'unknown/missing '+parts[1]+' fields');return parts[1],d

def decode(raw,contract_path,contract_sha,*,expected_geometry=None,synthetic=False,header_path=None,header_sha256=None,expected_kernel_catalog=None):
 need(sha(contract_path)==contract_sha,'actual contract SHA mismatch');k=json.loads(P(contract_path).read_bytes());need(k['schema']=='EP_L2_ENDPOINT_TIMELINE_V1'and k['record_bytes']==80 and k['endian']=='little','exact80-byte little-endian contract')
 if not synthetic:need(header_path is not None and header_sha256 is not None and expected_kernel_catalog is not None,'actual app component requires explicit header and ordered kernel contract')
 if header_path is not None:need(sha(header_path)==header_sha256,'actual ET header SHA mismatch')
 geometry=expected_geometry or{'slices':64,'sets':32,'ways':8};need(geometry=={'slices':64,'sets':32,'ways':8},'this Goal fixed64x32x8')
 names=k['uint64_fields']+[x[0]for x in k['tail_fields']];need(len(names)==15 and names[:9]==['ordinal','core_cycle','L2_edge','DRAM_edge','address','generation','aux','packet_or_requester_uid','parent_uid'],'record field order')
 codec=struct.Struct('<9Q2H4B');kindmap={int(n):v for n,v in k['kinds'].items()};domains={int(n):v for n,v in k['domains'].items()};meta=None;kernels=[];snaps=[];current=None;terminal=None;wire=compressed=0;digest=hashlib.sha256();seen_slots=set();event_by_ordinal={}
 for rawline in P(raw).open('rb'):
  digest.update(rawline)
  if not rawline.startswith(b'EPETV1|'):continue
  need(terminal is None,'EPET record after END');kind,d=frame(rawline)
  if kind=='META':
   need(meta is None and not kernels and not snaps,'duplicate/out-of-order META');meta={key:(value if key in('schema','schema_sha256','endian')else uint(value))for key,value in d.items()};need(meta['schema']==k['schema']and meta['schema_sha256']==contract_sha and meta['record_bytes']==80 and meta['endian']=='little','META source contract')
   need(all(meta[n]==v for n,v in geometry.items()),'actual META geometry')
   for field,limit in [('ring','slice_ring_events'),('pre','pre_events'),('post','post_events_including_trigger'),('slots','snapshot_slots'),('state_cap','state_cap_bytes'),('compressed_cap','compressed_cap_bytes'),('wire_cap','wire_cap_bytes')]:need(meta[field]==k['limits'][limit],'actual META bound '+field)
   need(meta['state_bytes']==meta['state_object_bytes']+meta['aux_state_bound']and meta['state_bytes']<=meta['state_cap'],'full observer state bound')
   need(meta['end_core']>=meta['first_core']and meta['high_new']>=meta['full_new']and meta['new_head_seen']>=meta['high_new'],'META scope/order populations')
   need(meta['frontend_notifications']==meta['frontend_wait_notifications']+meta['frontend_admit_decisions'],'frontend notification decision/wait population')
  else:
   need(meta is not None,'EPET record before META')
   if kind=='KERNEL':
    need(not snaps and current is None,'kernel catalog after snapshot');v={key:(value if key=='name_hex'else uint(value))for key,value in d.items()};need(v['uid']not in[old['uid']for old in kernels]and v['uid']!=U64 and len(kernels)<k['limits']['kernel_catalog'],'kernel UID/catalog capacity')
    need(v['name_truncated']==0 and v['name_length']<=k['limits']['kernel_name_bytes']and len(v['name_hex'])==2*v['name_length'],'kernel name complete')
    try:v['name']=bytes.fromhex(v['name_hex']).decode('utf-8','strict')
    except(ValueError,UnicodeDecodeError):raise InvalidWire('kernel name encoding')
    need(v['start_ordinal']<=v['end_ordinal']<=meta['ordinal']and meta['first_core']<=v['start_core']<=v['end_core']<=meta['end_core'],'kernel closed epoch bounds');kernels.append(v)
   elif kind=='SNAP':
    need(current is None,'interleaved snapshot');v={key:uint(value)for key,value in d.items()};need(v['slot']<meta['slots']and v['slot']not in seen_slots,'duplicate snapshot slot');seen_slots.add(v['slot']);need(v['slice']<64 and v['set']<32 and v['ways']==8,'snapshot physical set')
    need(v['pre']<=meta['pre']and 1<=v['post']<=meta['post']and v['events']==v['pre']+v['post']and v['post_complete']==int(v['post']==meta['post']),'capture event quota/censor')
    need(v['trigger_ordinal']<=meta['ordinal'],'trigger ordinal after epoch')
    if v['slot']<3:
     need(v['rank']==0 and 4<=v['reserved']<=8,'ordinary highR threshold/rank');need(not any(s['metadata']['slot']<3 and(s['metadata']['slice'],s['metadata']['set'])==(v['slice'],v['set'])for s in snaps),'ordinary capture physical-set uniqueness')
    else:need(v['rank']in(1,2)and(v['reserved']==8 or(v['rank']==2 and v['reserved']==U16)),'critical fullNEW/actualFAIL rank')
    current={'metadata':v,'z':zlib.decompressobj(),'raw':bytearray(),'compressed':0,'seq':0}
   elif kind=='DATA':
    need(current is not None and uint(d['slot'])==current['metadata']['slot']and uint(d['seq'])==current['seq'],'DATA snapshot/sequence');current['seq']+=1
    try:chunk=base64.b64decode(d['data'],validate=True)
    except ValueError:raise InvalidWire('invalid base64 DATA')
    current['compressed']+=len(chunk);need(compressed+current['compressed']<=meta['compressed_cap'],'compressed hardcap')
    maximum=current['metadata']['events']*80
    try:decoded=current['z'].decompress(chunk,maximum-len(current['raw'])+1)
    except zlib.error:raise InvalidWire('invalid zlib stream')
    current['raw'].extend(decoded);need(len(current['raw'])<=maximum and not current['z'].unconsumed_tail,'raw cap/bomb or unconsumed compressed payload')
   elif kind=='SNAP_END':
    need(current is not None,'SNAP_END without snapshot');v={key:uint(value)for key,value in d.items()};s=current['metadata'];data=bytes(current['raw']);need(v['slot']==s['slot']and v['events']==s['events']and v['raw_bytes']==len(data)==s['events']*80 and v['compressed_bytes']==current['compressed'],'closed snapshot lengths/population')
    need(current['z'].eof and not current['z'].unused_data and not current['z'].unconsumed_tail and zlib.crc32(data)==v['raw_crc32'],'snapshot zlib EOF/trailingdata/CRC')
    events=[];previous=0;clock_last={}
    for offset in range(0,len(data),80):
     row=codec.unpack_from(data,offset);e=dict(zip(names,row));need(previous<e['ordinal']<=meta['ordinal'],'ordered distinct ordinal per snapshot');previous=e['ordinal'];need(e['kind']in kindmap and e['domain']in domains,'unknown kind/domain enum')
     need(e['slice']==U16 or e['slice']<64,'event slice');need(e['set']==U16 or e['set']<32,'event set');need(e['way']==U8 or e['way']<8,'event way');need(e['sector_mask']==U8 or e['sector_mask']<=15,'event sector mask')
     need(e['core_cycle']!=U64 and meta['first_core']<=e['core_cycle']<=meta['end_core'],'timed event core bounds')
     for field in ('core_cycle','L2_edge','DRAM_edge'):
      value=e[field]
      if value!=U64:need(field not in clock_last or value>=clock_last[field],'event clock regressed');clock_last[field]=value
     need(e['L2_edge']==U64 or e['L2_edge']<meta['l2_edges'],'L2 edge bound');need(e['DRAM_edge']==U64 or e['DRAM_edge']<meta['dram_edges'],'DRAM edge bound')
     need(e['ordinal']not in event_by_ordinal or event_by_ordinal[e['ordinal']]==row,'overlapping snapshot sameordinal differs');event_by_ordinal[e['ordinal']]=row;e['kind_name']=kindmap[e['kind']];e['domain_name']=domains[e['domain']];e['generation_namespace']='UNKNOWN'if e['generation']==U64 else'LIFE_TAG_INCARNATION'if e['kind_name']=='TAG_MUTATION'else'PAYLOAD_GENERATION'if e['kind_name']in {'RO_STATE','RO_RETIRE','RO_LOWER_CREATE','RO_BIND','RO_READY','RO_DETACH','L1_SEND','L1_SEND_DENY','L2_INGRESS','MISSQ_ENQUEUE','MISSQ_DEQUEUE','MISSQ_REJECT','LOWER_ENQUEUE','LOWER_DEQUEUE','LOWER_REJECT','DRAM_DELAY_ENQUEUE','DRAM_MC_PUSH','SCHEDULER_ACCEPT','DRAM_RETURN','DRAM_COLUMN','RESPONSE_ACCEPT','ICNT_INJECT','PACKET_SPLIT','FRONTEND_COMMIT'}else'NO_DECLARED_GENERATION_NAMESPACE'
     if e['kind_name']=='RO_DETACH':e['aux_generation_namespace']='RO_TAG_BINDING_GENERATION_DISTINCT_FROM_LIFE_TAG_INCARNATION'
     events.append(e)
    trigger=events[s['pre']];need(trigger['ordinal']==s['trigger_ordinal']and trigger['packet_or_requester_uid']==s['trigger_uid']and trigger['address']==s['trigger_address'],'actual trigger event identity/index')
    need(trigger['kind_name']==('PRODUCTION_TAGFAIL'if s['rank']==2 else'PRESSURE_NEW'),'trigger event source kind');compressed+=current['compressed'];snaps.append({'metadata':s,'events':events,'closed':v});current=None
   elif kind=='END':
    terminal={key:uint(value)for key,value in d.items()};need(current is None and terminal['slots']==len(snaps),'closed snapshot cardinality');need(terminal['completed']==terminal['closed']==1 and terminal['invalid']==terminal['output_overflow']==terminal['output_error']==0,'incomplete/invalid/overflow/error terminal')
    need(terminal['compressed_bytes']==compressed and terminal['wire_bytes_before_END']==wire and terminal['z_arena_peak']<=k['limits']['zlib_arena_bytes'],'terminal compressed/wire/arena accounting')
  wire+=len(rawline)
  if meta is not None:need(wire<=meta['wire_cap'],'actual EPET wire hardcap')
 need(meta is not None and terminal is not None and current is None,'missing complete EPET terminal')
 if expected_kernel_catalog is not None:need([(v['uid'],v['name'])for v in kernels]==[(v['uid'],v['name'])for v in expected_kernel_catalog],'exact ordered actual kernel catalog')
 return {'status':'VALIDATED_EPET_WIRE_COMPONENT_ONLY_NOT_APPLICATION_ACCEPTED','raw_sha256':digest.hexdigest(),'contract_sha256':contract_sha,'header_sha256_external':header_sha256,'geometry':geometry,'synthetic_fixture':synthetic,'meta':meta,'kernels':kernels,'snapshots':snaps,'terminal':terminal,'wire_bytes':wire,'unique_selected_event_ordinals':len(event_by_ordinal),'scope':'bounded selected timed endpoint windows; not fulltrace/event/cycle coverage or causal ancestry','source_binary_or_input_qualification_granted':False,'scientific_acceptance_granted':False}
