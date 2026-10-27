"""Only shared address scanner. No simulator, controller, lease or config APIs."""
import pathlib,json,os,resource,time,hashlib,collections,math,sys
P=pathlib.Path
R=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_p42_parallel_mechanism_review_v1')
O=R/'shared_address_index';O.mkdir(parents=True,exist_ok=True)
os.nice(19);resource.setrlimit(resource.RLIMIT_AS,(1024**3,1024**3))
start=time.monotonic();read_total=0;CAP=1024**3;DEADLINE=900;RATE=8*1024**2;MAX_LINES=600000
meta=json.loads((R/'agents/B/METADATA.json').read_text());source=P('/root/data/dtc_main_v100_sweep_20261025_v1/tools/original_body_audit.py')
source_sha=hashlib.sha256(source.read_bytes()).hexdigest()
self_sha=hashlib.sha256(P(__file__).read_bytes()).hexdigest()
rows=[]
def save(name,data):
 p=O/name; tmp=p.with_suffix('.writing');tmp.write_text(json.dumps(data,indent=2)+'\n');os.replace(tmp,p)
def index(state):
 save('INDEX.json',{'schema':'DTC_SINGLE_SHARED_ADDRESS_INDEX_V1','state':state,'producer_sha256':self_sha,'qualified_decoder_source':str(source),'qualified_decoder_sha256':source_sha,'decoder_provenance':'Address modes 0/1/2 and width parsing copied verbatim in semantics from qualified original_body_audit.py audit(), lines 32-68; no guessed address columns.','contract':{'single_process':True,'nice':os.getpriority(os.PRIO_PROCESS,0),'RLIMIT_AS_bytes':1024**3,'total_trace_bytes_limit':CAP,'wall_limit_seconds':DEADLINE,'read_rate_limit_bytes_s':RATE,'max_tracked_global_lines':MAX_LINES},'observed':{'total_trace_bytes_read':read_total,'wall_seconds':time.monotonic()-start,'max_RSS_KiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss},'limitations':['Serialized trace order is not simulated cross-SM execution time.','Per-warp line-event reuse interval is not stack reuse distance.','Repeated static lines are not duplicate outstanding simulator requests.','Prefix address uniqueness only describes scanned prefix.','No simulator timestamp burst analysis or L2 replacement sequence exists here.'],'rows':rows})
jobs=[('ATAX',1,128*1024**2),('MVT',1,128*1024**2),('BICG',2,128*1024**2),('2DCONV',1,16*1024**2),('3MM',1,16*1024**2),('GEMM',1,16*1024**2)]
index('SCANNING')
for program,ordinal,bytecap in jobs:
 if time.monotonic()-start>=DEADLINE or read_total>=CAP:break
 m=next(x for x in meta['rows'] if x['program']==program);q=m['qualification']['rows'][ordinal-1];p=P(q['path']);size=p.stat().st_size;before=p.stat()
 counts={};last={};reuse=collections.Counter();lanestrides=collections.Counter();linehist=collections.Counter();warp_unique={};recordsha=hashlib.sha256();header={};ctas=set();warps=set();finishedwarps=set();version=0;coord=None;warp=None;declared=None;seen=0;lastop=None
 nbytes=0;records=0;globalloads=0;lineevents=0;laneaccess=0;lo=None;hi=None;warp_event=0;overflow=False;previousline=None;transitions=collections.Counter();eof=False;stop='BYTE_PREFIX_CAP';minimum_scan=time.monotonic()
 with p.open('rb',buffering=1024**2) as f:
  while True:
   if read_total>=CAP:stop='TOTAL_BYTE_CAP';break
   if nbytes>=bytecap:break
   if time.monotonic()-start>=DEADLINE:stop='TOTAL_WALL_CAP';break
   line=f.readline(1024**2)
   if not line:eof=True;stop='EOF';break
   assert len(line)<1024**2,'oversize trace line'
   recordsha.update(line);nbytes+=len(line);read_total+=len(line)
   if nbytes%(1024**2)<len(line):
    delay=read_total/RATE-(time.monotonic()-start)
    if delay>0:time.sleep(min(delay,1))
   if line.startswith(b'-') and b' = ' in line:
    k,v=line.decode().strip().split(' = ',1);header[k]=v
    if k=='-accelsim tracer version':version=int(v)
   elif line.startswith(b'thread block = '):coord=tuple(map(int,line.split(b' = ')[1].split(b',')));ctas.add(coord)
   elif line.startswith(b'warp = '):
    if declared is not None:
     assert seen==declared and lastop==b'EXIT';finishedwarps.add((coord,warp))
    warp=int(line.split(b' = ')[1]);warps.add((coord,warp));last={};warp_event=0;previousline=None
   elif line.startswith(b'insts = '):declared=int(line.split(b' = ')[1]);seen=0
   elif declared is not None and line[:1] in b'0123456789abcdef' and line.strip():
    t=line.split();offset=0 if version>=3 else 4
    if offset:assert tuple(map(int,t[:3]))==coord and int(t[3])==warp
    mask=int(t[offset+1],16);dest=int(t[offset+2]);j=offset+3+dest;op=t[j];src=int(t[j+1]);width=int(t[j+2+src]);root=op.split(b'.')[0];seen+=1;records+=1;lastop=root
    if not width or root!=b'LDG':continue
    tokens=op.split(b'.')
    if (b'STRONG' in tokens and b'GPU' in tokens) or b'BYPASS' in tokens:continue
    parsed_width=4
    for token in tokens:
     if token.isdigit():parsed_width=int(token)//8;break
     if token.startswith(b'U') and token[1:].isdigit():parsed_width=int(token[1:])//8;break
    a=t[j+3+src:];mode=int(a[0]);count=mask.bit_count();addresses=[]
    if mode==0:
     addresses=[int(s,16) for s in a[1:1+count]];assert len(addresses)==count
    elif mode==1:
     base=int(a[1],16);stride=int(a[2]);addresses=[base+i*stride for i in range(count)];lanes=[i for i in range(32) if mask&(1<<i)]
     assert not lanes or lanes==list(range(lanes[0],lanes[-1]+1))
    elif mode==2:
     if count:
      addresses=[int(a[1],16)]
      for delta in a[2:2+count-1]:addresses.append(addresses[-1]+int(delta))
      assert len(addresses)==count
    else:raise AssertionError(('unsupported address mode',mode))
    globalloads+=1;laneaccess+=count
    if addresses:
     al=min(addresses);ah=max(addresses)+parsed_width-1;lo=al if lo is None else min(lo,al);hi=ah if hi is None else max(hi,ah)
     for aa,bb in zip(addresses,addresses[1:]):lanestrides[bb-aa]+=1
    lines=sorted({base//128 for addr in addresses for base in [addr,addr+parsed_width-1]});linehist[len(lines)]+=1
    for ln in lines:
     lineevents+=1;warp_event+=1
     if ln in counts:counts[ln]+=1
     elif len(counts)<MAX_LINES:counts[ln]=1
     else:overflow=True
     prev=last.get(ln)
     if prev is not None:reuse[int(math.log2(max(1,warp_event-prev)))]+=1
     last[ln]=warp_event
     if previousline is not None:transitions[abs(ln-previousline)%32]+=1
     previousline=ln
 if eof:
  assert seen==declared and lastop==b'EXIT';finishedwarps.add((coord,warp));assert recordsha.hexdigest()==q['sha256']
 after=p.stat();assert (before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns)
 result={'program':program,'input_digest':m['input_digest'],'kernel_ordinal':ordinal,'kernel':q['kernel'],'trace_path':str(p),'qualified_full_trace_sha256':q['sha256'],'trace_file_size_bytes':size,'prefix_sha256':recordsha.hexdigest(),'full_SHA_reverified':eof,'scanned_bytes':nbytes,'coverage':'FULL_DECLARED_KERNEL' if eof else 'PREFIX_ONLY','stop_reason':stop,'warp_instruction_records_scanned':records,'global_load_warp_records_scanned':globalloads,'active_lane_global_load_accesses':laneaccess,'global_load_128B_line_events':lineevents,'distinct_128B_lines':len(counts),'distinct_exact_for_scanned_range':not overflow,'line_revisit_factor':lineevents/len(counts) if counts and not overflow else None,'line_repeat_events_scanned_range':lineevents-len(counts) if not overflow else None,'unique_lines_seen_at_least_twice':sum(v>=2 for v in counts.values()),'min_global_load_address':hex(lo) if lo is not None else None,'max_global_load_address_inclusive':hex(hi) if hi is not None else None,'address_span_bytes':hi-lo+1 if lo is not None else None,'distinct_lines_per_global_load_warp_record_histogram':dict(linehist),'adjacent_active_lane_address_delta_bytes_histogram':dict(lanestrides.most_common(32)),'per_warp_reuse_interval_log2_line_events_histogram':dict(sorted(reuse.items())),'per_warp_reuse_interval_definition':'event_index_current - event_index_previous, counting distinct128B lines per global-load warp instruction in source serialized warp order. Not stack distance.','cta_coordinates_seen':[list(x) for x in sorted(ctas)],'warp_count_seen':len(warps),'warps_complete':len(finishedwarps),'qualified_total_ctas':q['complete_ctas'],'qualified_total_warps':q['complete_warps'],'max_RSS_KiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'scan_seconds':time.monotonic()-minimum_scan,'decoder_original_source_sha256':source_sha,'producer_sha256':self_sha}
 save(program+'_K'+str(ordinal)+'.json',result);rows.append({k:result[k] for k in ['program','input_digest','kernel_ordinal','kernel','coverage','scanned_bytes','distinct_128B_lines','line_revisit_factor','full_SHA_reverified']});index('SCANNING')
 print(json.dumps(rows[-1]),flush=True)
index('COMPLETE_BOUNDED_READONLY_SCAN')
