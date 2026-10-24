from pathlib import Path
from array import array
from collections import deque
import json,hashlib,re,gzip,struct,heapq,math,os,time
os.nice(15)
R=Path('/home/huangrulin/workspace/rtx4080_cuda_polybench_20261024_v1');P=Path('/data/c16/rtx4080_suite_fill_20261024_v1');O=R/'rodinia_cpu_reference_v1';O.mkdir(exist_ok=False);allrec=json.loads((P/'native_control/NATIVE_BATCH_rodinia51_v1.json').read_text());proofs=[]
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def f32(x):return struct.unpack('<f',struct.pack('<f',x))[0]
for rec in allrec:
 j=rec['task'];n=j['program']
 if n not in ['bfs','nn']:continue
 out=O/j['task_id'];out.mkdir(exist_ok=False);attempt=Path(rec['output']);assert rec['exit']==0;start=time.time();used=[]
 if n=='bfs':
  graph=attempt/j['argv'][1];expected=next(x for x in j['input_identity'] if Path(x['path']).name==graph.name);before=sha(graph);assert before==expected['sha256'];used=[{'path':str(graph),'sha256':before}]
  with graph.open() as f:
   lines=(l for l in f if l.strip());count=int(next(lines));offsets=array('I');lengths=array('I')
   for i in range(count):a,b=map(int,next(lines).split());offsets.append(a);lengths.append(b)
   declared_source=int(next(lines));edgecount=int(next(lines));edges=array('I')
   for i in range(edgecount):v,cost=map(int,next(lines).split());assert 0<=v<count;edges.append(v)
   assert not list(lines)
  srcfile=Path(j['sources'][0]['path']);source=srcfile.read_text();assert re.search(r'\bsource\s*=\s*0\s*;',source);root=0
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
  expected=sorted(records)[:top];text=(attempt/'stdout.log').read_text();reported=[]
  for line in text.splitlines():
   if ' --> ' in line:
    label,d=line.rsplit(' --> ',1);d=d.replace('Distance=','');reported.append((label,float(d)))
  assert len(reported)==top;wanted={label:d for d,idx,label in expected};bad=[]
  for label,d in reported:
   if label not in wanted:bad.append({'record':label,'problem':'NOT_IN_CPU_TOPK'})
   elif abs(d-wanted[label])>2e-6:bad.append({'record':label,'expected_distance':wanted[label],'reported_distance':d})
  assert len({s for s,d in reported})==top;proof={'kind':'FULL_INPUT_FLOAT32_EUCLIDEAN_TOPK_REFERENCE','records_scanned':counter,'topk':top,'latitude':lat,'longitude':lng,'all_returned_record_identities_checked':True,'distance_absolute_tolerance':2e-6,'tolerance_basis':'6decimal output rounding plus float32 subtract/square/add/sqrt rounding at distance<1; no fitted threshold','version_order_policy':'3.1 ascending output;2.0-ft heap output compared as exact topK set','expected':expected,'reported':reported,'mismatch_examples':bad,'status':'INDEPENDENT_CPU_FULL_RESULT_PASS' if not bad else 'INDEPENDENT_CPU_RESULT_MISMATCH'}
  if j['version']=='3.1' and [s for s,d in reported]!=[s for d,idx,s in expected]:proof['status']='INDEPENDENT_CPU_TOPK_ORDER_MISMATCH'
 proof.update(task_id=j['task_id'],suite_version=j['version'],program=n,native_receipt=str(attempt/'NATIVE_RECEIPT.json'),native_receipt_sha256=sha(attempt/'NATIVE_RECEIPT.json'),binary_sha256=j['binary_sha256'],input_files_used=used,read_only_existing_attempt=True,gpu_code_changed=False,gpu_rerun=False,wall_seconds=time.time()-start,unix=time.time());(out/'CPU_REFERENCE_RECEIPT.json').write_text(json.dumps(proof,indent=2)+'\n');proofs.append(proof);print(j['task_id'],proof['status'],proof.get('vertices',proof.get('records_scanned')),flush=True)
(O/'RODINIA_BFS_NN_FULL_CPU_REFERENCE_SUMMARY.json').write_text(json.dumps(proofs,indent=2)+'\n')
