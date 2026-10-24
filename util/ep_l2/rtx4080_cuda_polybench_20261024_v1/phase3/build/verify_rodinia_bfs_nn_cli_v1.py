from pathlib import Path
from array import array
from collections import deque
import json,hashlib,re,gzip,struct,heapq,math,os,time,argparse,sys,traceback
# Host-only checker. It never runs a CUDA executable or changes source/runtime.
p=argparse.ArgumentParser(description='Full Rodinia BFS/NN CPU oracle for frozen task JSON and completed native/capture runtime directory')
p.add_argument('task_json');p.add_argument('runtime_directory');p.add_argument('--out',required=True,help='ABSENT proof output directory');p.add_argument('--stdout',default=None,help='Captured stdout path; defaults runtime/stdout.log')
a=p.parse_args();task_path=Path(a.task_json);j=json.loads(task_path.read_text());j=j.get('task',j);n=j['program'];assert n in ['bfs','nn'];attempt=Path(a.runtime_directory);out=Path(a.out);out.mkdir(exist_ok=False);stdout=Path(a.stdout) if a.stdout else attempt/'stdout.log';start=time.time();used=[]
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def f32(x):return struct.unpack('<f',struct.pack('<f',x))[0]
def int_tokens(f):
 carry=b''
 while True:
  b=f.read(1024*1024)
  if not b:break
  joined=carry+b;parts=joined.split();carry=b''
  if joined and not joined[-1:].isspace():carry=parts.pop()
  for p in parts:yield int(p)
 if carry:yield int(carry)

try:
 if n=='bfs':
  graph=attempt/j['argv'][1];expected=next(x for x in j['input_identity'] if Path(x['path']).name==graph.name);before=sha(graph);assert before==expected['sha256'];used=[{'path':str(graph),'sha256':before}]
  with graph.open('rb') as f:
   tokens=int_tokens(f);count=next(tokens);offsets=array('I');lengths=array('I')
   for i in range(count):a=next(tokens);b=next(tokens);offsets.append(a);lengths.append(b)
   declared_source=next(tokens);edgecount=next(tokens);edges=array('I')
   for i in range(edgecount):v=next(tokens);cost=next(tokens);assert 0<=v<count;edges.append(v)
   assert next(tokens,None) is None
  srcfile=Path(j['sources'][0]['path']);assert sha(srcfile)==j['sources'][0]['sha256'];source=srcfile.read_text();assert re.search(r'\bsource\s*=\s*0\s*;',source);root=0
  distance=array('i',[-1])*count;distance[root]=0;queue=deque([root]);visited=0
  while queue:
   u=queue.popleft();visited+=1;begin=offsets[u];end=begin+lengths[u];assert end<=len(edges)
   for k in range(begin,end):
    v=edges[k]
    if distance[v]<0:distance[v]=distance[u]+1;queue.append(v)
  result=attempt/'result.txt';bad=[];rows=0
  with result.open() as f:
   for i,line in enumerate(f):
    index,value=line.strip().split(') cost:');assert int(index)==i;got=int(value)
    if got!=distance[i] and len(bad)<8:bad.append({'vertex':i,'expected':distance[i],'actual':got})
    rows+=1
  assert rows==count;payload=distance.tobytes();(out/'CPU_DISTANCE_I32LE.bin.gz').write_bytes(gzip.compress(payload,mtime=0));proof={'kind':'FULL_INTEGER_DIRECTED_CSR_BFS_REFERENCE','vertices':count,'edges':edgecount,'declared_source':declared_source,'effective_source':root,'source_override_basis':str(srcfile),'source_sha256':sha(srcfile),'checked_all_vertices':rows,'reachable_vertices':visited,'max_distance':max(distance),'mismatch_examples':bad,'reference_i32le_sha256':hashlib.sha256(payload).hexdigest(),'gpu_output_sha256':sha(result),'status':'INDEPENDENT_CPU_FULL_RESULT_PASS' if not bad else 'INDEPENDENT_CPU_RESULT_MISMATCH'};assert sha(graph)==before
 else:
  lat=float(j['argv'][j['argv'].index('-lat')+1]) if '-lat' in j['argv'] else float(j['argv'][3]);lng=float(j['argv'][j['argv'].index('-lng')+1]) if '-lng' in j['argv'] else float(j['argv'][4]);top=int(j['argv'][j['argv'].index('-r')+1]) if '-r' in j['argv'] else int(j['argv'][2]);lat=f32(lat);lng=f32(lng);flist=attempt/j['argv'][1];used.append({'path':str(flist),'sha256':sha(flist)});records=[];counter=0
  for filename in flist.read_text().split():
   db=attempt/filename;used.append({'path':str(db),'sha256':sha(db)})
   with db.open() as f:
    for line in f:
     line=line.rstrip('\r\n');assert len(line)==48,(len(line),str(db));a=f32(float(line[28:33]));b=f32(float(line[33:38]));dx=f32(a-lat);dy=f32(b-lng);d=f32(math.sqrt(f32(f32(dx*dx)+f32(dy*dy))));records.append((d,counter,line));counter+=1
  expected=sorted(records)[:top];text=stdout.read_text();reported=[]
  for line in text.splitlines():
   if ' --> ' in line:
    label,d=line.rsplit(' --> ',1);d=d.replace('Distance=','');reported.append((label,float(d)))
  assert len(reported)==top;wanted={label:d for d,idx,label in expected};bad=[]
  for label,d in reported:
   if label not in wanted:bad.append({'record':label,'problem':'NOT_IN_CPU_TOPK'})
   elif abs(d-wanted[label])>2e-6:bad.append({'record':label,'expected_distance':wanted[label],'reported_distance':d})
  assert len({s for s,d in reported})==top;proof={'kind':'FULL_INPUT_FLOAT32_EUCLIDEAN_TOPK_REFERENCE','records_scanned':counter,'topk':top,'latitude':lat,'longitude':lng,'all_returned_record_identities_checked':True,'distance_absolute_tolerance':2e-6,'tolerance_basis':'6decimal output rounding plus float32 subtract/square/add/sqrt rounding at distance<1; no fitted threshold','version_order_policy':'3.1 ascending output;2.0-ft heap output compared as exact topK set','expected':expected,'reported':reported,'mismatch_examples':bad,'status':'INDEPENDENT_CPU_FULL_RESULT_PASS' if not bad else 'INDEPENDENT_CPU_RESULT_MISMATCH'}
  if j['version']=='3.1' and [s for s,d in reported]!=[s for d,idx,s in expected]:proof['status']='INDEPENDENT_CPU_TOPK_ORDER_MISMATCH'

 expected_inputs={Path(x['path']).name:x['sha256'] for x in j['input_identity']}
 for u in used:
  name=Path(u['path']).name
  if name not in expected_inputs or expected_inputs[name]!=u['sha256']:
   raise ValueError('Input identity mismatch or absent SHA in frozen task: '+name)
 proof.update(task_id=j['task_id'],suite_version=j['version'],program=n,task_json_sha256=sha(task_path),runtime_directory=str(attempt),stdout_sha256=sha(stdout),binary_sha256=j['binary_sha256'],input_files_used=used,read_only_existing_runtime=True,gpu_code_changed=False,gpu_rerun=False,wall_seconds=time.time()-start,unix=time.time())
 (out/'CPU_REFERENCE_RECEIPT.json').write_text(json.dumps(proof,indent=2)+'\n')
 print(json.dumps({'task_id':j['task_id'],'status':proof['status'],'proof':str(out/'CPU_REFERENCE_RECEIPT.json')}))
 sys.exit(0 if proof['status']=='INDEPENDENT_CPU_FULL_RESULT_PASS' else 2)
except Exception as error:
 proof={'task_id':j.get('task_id'),'status':'CPU_REFERENCE_VALIDATION_ERROR','error_type':type(error).__name__,'error':str(error),'task_json_sha256':sha(task_path),'runtime_directory':str(attempt),'read_only_existing_runtime':True,'gpu_rerun':False}
 (out/'CPU_REFERENCE_RECEIPT.json').write_text(json.dumps(proof,indent=2)+'\n');traceback.print_exc();sys.exit(2)
