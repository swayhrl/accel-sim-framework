"""Finite read-only whole-body generic-address review; no scientific launcher."""
import pathlib,json,hashlib,collections,time,os,resource,datetime,re
P=pathlib.Path;T=P('/root/data/dtc_main_v100_sweep_20261025_v1');KEY='af7320f9d9dc662971b1856cac87f29f9b8e4b2a65a7f9d4223bb7a74803fef8';OUT=T/'analysis/cutcp_generic_domain_v1';RATE=5*1024**2
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def write(p,x):tmp=P(p).with_suffix('.writing');tmp.write_text(json.dumps(x,indent=2)+chr(10));os.replace(tmp,p)
def classify(addr,shared,local):return 'SHARED' if shared<=addr<local else 'LOCAL' if local<=addr<local+16384 else 'GLOBAL'
def scan(row,ordinal,total_before,job_started):
 p=P(row['path']);before=p.stat();h=hashlib.sha256();headers={};counts=collections.Counter();widths=collections.Counter();modes=collections.Counter();issues=[];examples={};generic=0;bytes_read=0;advised=0;last_report=0;min_addr={};max_addr={};max_lines=0
 with p.open('rb') as f:
  for number,line in enumerate(f,1):
   h.update(line);bytes_read+=len(line)
   if bytes_read-last_report>=16*1024**2:
    elapsed=time.monotonic()-job_started;delay=(total_before+bytes_read)/RATE-elapsed
    if delay>0:time.sleep(delay)
    frontier=max(0,bytes_read-4*1024**2)
    try:
     if frontier>advised:os.posix_fadvise(f.fileno(),advised,frontier-advised,os.POSIX_FADV_DONTNEED);advised=frontier
    except OSError:pass
    write(OUT/'PROGRESS.json',{'state':'READ_ONLY_GENERIC_ADDRESS_REVIEW','kernel_ordinal':ordinal,'kernel_count':11,'current_member_bytes_read':bytes_read,'total_bytes_read':total_before+bytes_read,'current_generic_records':generic,'elapsed_seconds':elapsed,'source_payload_modified':False,'scientific_starts':0});last_report=bytes_read
   if line.startswith(b'-') and b' = ' in line:
    k,v=line.decode().strip().split(' = ',1);headers[k]=v;continue
   if b' LD' not in line and b' ST' not in line:continue
   tokens=line.split()
   try:
    offset=0 if row['trace_version']>=3 else 4;j=offset+3+int(tokens[offset+2]);op=tokens[j].decode();root=op.split('.')[0]
   except (ValueError,IndexError):continue
   if root not in ['LD','ST']:continue
   mask=int(tokens[offset+1],16);src=int(tokens[j+1]);width=int(tokens[j+2+src]);args=tokens[j+3+src:]
   if width==0:continue
   generic+=1;lanes=[i for i in range(32) if mask&(1<<i)];mode=int(args[0]);modes[str(mode)]+=1
   parsed=4
   for suffix in op.split('.'):
    if suffix.isdigit():parsed=int(suffix)//8;break
    if suffix.startswith('U') and suffix[1:].isdigit():parsed=int(suffix[1:])//8;break
   widths[(op,width,parsed)]+=1
   if width!=parsed:issues.append({'line':number,'reason':'GENERIC_TRACE_PARSER_WIDTH_MISMATCH','opcode':op,'trace_width':width,'parser_width':parsed})
   if not lanes:issues.append({'line':number,'reason':'ZERO_ACTIVE_GENERIC_MEMORY_RECORD'});continue
   if mode==0:addresses=[int(x,16) for x in args[1:1+len(lanes)]];assert len(addresses)==len(lanes)
   elif mode==1:
    base=int(args[1],16);stride=int(args[2]);assert -(1<<31)<=stride<(1<<31)
    if lanes!=list(range(lanes[0],lanes[-1]+1)):issues.append({'line':number,'reason':'NONCONTIGUOUS_MASK_BASE_STRIDE_OUTSIDE_FROZEN_CODEC_CONTRACT'})
    addresses=[(base+k*stride)&((1<<64)-1) for k in range(len(lanes))]
   elif mode==2:
    addresses=[int(args[1],16)]
    for d in args[2:2+len(lanes)-1]:addresses.append((addresses[-1]+int(d))&((1<<64)-1))
    assert len(addresses)==len(lanes)
   else:raise AssertionError('unsupported generic address format:'+str(mode))
   shared=int(headers.get('-shmem base_addr','0'),16);local=int(headers.get('-local mem base_addr','0'),16)
   if not (0<shared<local):issues.append({'line':number,'reason':'MISSING_OR_INVALID_ADDRESS_SPACE_BASES'});continue
   spaces=[classify(a,shared,local) for a in addresses];first=spaces[0];counts[(root,first)]+=1
   if len(set(spaces))!=1:issues.append({'line':number,'reason':'ACTIVE_LANE_ADDRESS_SPACE_MIX_NOT_REPRESENTED_BY_NATIVE_FIRST_LANE_RESOLVER','spaces':dict(collections.Counter(spaces))})
   for a,space in zip(addresses,spaces):min_addr[space]=min(a,min_addr.get(space,a));max_addr[space]=max(a,max_addr.get(space,a))
   max_lines=max(max_lines,len({a//128 for address in addresses for a in [address,address+parsed-1]}) if first in ['GLOBAL','LOCAL'] else 0)
   if (root,first) not in examples:examples[(root,first)]={'line':number,'opcode':op,'mask':hex(mask),'active_lanes':len(lanes),'native_first_lane_class':first,'all_active_lanes_same_class':len(set(spaces))==1,'record_sha256':hashlib.sha256(line).hexdigest()}
  try:os.posix_fadvise(f.fileno(),0,bytes_read,os.POSIX_FADV_DONTNEED)
  except OSError:pass
 after=p.stat();assert h.hexdigest()==row['sha256'] and before.st_size==after.st_size==bytes_read and before.st_mtime_ns==after.st_mtime_ns
 expected=row['memory_instruction_paths'].get('GENERIC_SOURCE_ADDRESS_CLASSIFICATION_REQUIRED',0);assert generic==expected
 result={'ordinal':ordinal,'path':str(p),'full_current_sha256':h.hexdigest(),'bytes_read':bytes_read,'trace_version':row['trace_version'],'kernel':row['kernel'],'headers':headers,'generic_records':generic,'generic_opcode_and_space_counts':[{'opcode':k[0],'resolved_space':k[1],'records':v} for k,v in sorted(counts.items())],'widths':[{'opcode':k[0],'trace_width':k[1],'parser_width':k[2],'records':v} for k,v in sorted(widths.items())],'address_modes':dict(modes),'address_min_max':{space:{'min':hex(min_addr[space]),'max':hex(max_addr[space])} for space in min_addr},'maximum_cacheable_generic128B_line_references':max_lines,'examples':list(examples.values()),'issues':issues,'source_modified':False,'coverage':'Every genericLD/ST record in the full SHA-rechecked original member'}
 with (OUT/('kernel_'+str(ordinal)+'.json')).open('x') as stream:json.dump(result,stream,indent=2);stream.write(chr(10))
 return result
def main():
 os.sched_setaffinity(0,{9});resource.setrlimit(resource.RLIMIT_AS,(2*1024**3,2*1024**3));OUT.mkdir(exist_ok=False)
 original=T/'qualification'/KEY/'QUALIFICATION.json';q=read(original);assert q['program']=='cutcp' and len(q['rows'])==11 and q['prior_scientific_statuses_preserved']==[]
 assert {i['reason'] for i in q['issues']}=={'GENERIC_SOURCE_ADDRESS_CLASSIFICATION_REQUIRED'}
 resolver=T/'telemetry_v2/framework/gpu-simulator/trace-driven/trace_driven.cc';core=T/'core/src/abstract_hardware_model.h';assert 'const unsigned long long LOCAL_MEM_SIZE_MAX = 1 << 14;' in core.read_text();lines=resolver.read_text().splitlines();source={'resolver_path':str(resolver),'resolver_sha256':sha(resolver),'resolver_excerpt_first_line':456,'resolver_excerpt':lines[455:493],'core_header_path':str(core),'core_header_sha256':sha(core),'LOCAL_MEM_SIZE_MAX':16384}
 with (OUT/'START.json').open('x') as f:json.dump({'pid':os.getpid(),'start_ticks':int(P('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19]),'operation':'FiniteCPU-onlyall11membersgenericdomainreview','input_digest':KEY,'original_qualification_sha256':sha(original),'rate_bytes_s':RATE,'CPU':9,'address_space_limit':2*1024**3,'scientific_starts':0},f,indent=2)
 rows=[];total=0;started=time.monotonic()
 for ordinal,row in enumerate(q['rows'],1):
  result=scan(row,ordinal,total,started);rows.append(result);total+=result['bytes_read'];print(json.dumps({'kernel_closed':ordinal,'generic_records':result['generic_records'],'issues':len(result['issues']),'total_bytes':total}),flush=True)
 issues=[dict(i,kernel=r['ordinal']) for r in rows for i in r['issues']];status='CURRENT_SOURCE_GENERIC_CONTRACT_PASS_PENDING_EXPLICIT_SCIENTIFIC_ADMISSION' if not issues else 'GENERIC_DOMAIN_HOLD_PRESERVED_AFTER_FULL_REVIEW'
 result={'schema':'DTC_CUTCP_GENERIC_DOMAIN_FULL_CURRENT_SHA_REVIEW_V1','status':status,'input_digest':KEY,'original_qualification':str(original),'original_qualification_sha256':sha(original),'source_contract':source,'members':len(rows),'full_bytes_read':total,'generic_records':sum(r['generic_records'] for r in rows),'issues':issues,'rows':rows,'all_headers_source_bases_present_and_all_active_lanes_checked':not issues,'original_HOLD_qualification_not_modified':True,'native_numerical_values':'UNPROVEN','old_scientific_HOLDs_cleared':False,'source_payload_or_model_modified':False,'scientific_starts':0,'admission_or_performance_granted_by_this_review':False,'elapsed_seconds':time.monotonic()-started,'observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 with (OUT/'RESULT.json').open('x') as f:json.dump(result,f,indent=2);f.write(chr(10))
 print(json.dumps({k:v for k,v in result.items() if k not in ['source_contract','rows']},indent=2))
if __name__=='__main__':main()
