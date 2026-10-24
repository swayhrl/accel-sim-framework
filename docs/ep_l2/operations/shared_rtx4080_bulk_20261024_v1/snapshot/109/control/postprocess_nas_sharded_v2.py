#!/usr/bin/env python3
"""Bounded-memory stable grouping; compressed CTA shards and all scratch live on NAS."""
import argparse,pathlib,lzma,os,re,json,hashlib,subprocess,collections,shutil,time
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def save(p,o):
 tmp=p.with_name(p.name+'.tmp')
 with tmp.open('w') as f:json.dump(o,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
 os.replace(tmp,p)
def crc(p):
 n=0
 with lzma.open(p,'rb') as f:
  for b in iter(lambda:f.read(1048576),b''):n+=len(b)
 return n
def compress(p,body):
 with p.open('xb') as raw:
  with lzma.LZMAFile(raw,'w',preset=1) as out:out.write(body)
  raw.flush();os.fsync(raw.fileno())
def group(source,dest,work,span,budget,stop_after):
 work.mkdir(parents=True,exist_ok=True);checkpoint=work/'CHECKPOINT.json';source_sha=sha(source)
 state=json.loads(checkpoint.read_text()) if checkpoint.exists() else {'source':str(source),'source_sha256':source_sha,'span':span,'groups':{},'partition_complete':False}
 assert state['source_sha256']==source_sha and state['span']==span,'source/partition identity changed'
 if not state['partition_complete']:
  assert not list(work.glob('partition-*.xz')),'incomplete partition retained; use a fresh work attempt'
  buffers={};buffer_bytes=0;header=[];grid=None;total=0;expanded=0;peak_buffer_bytes=0;flushes=0
  def flush_one(index):
   nonlocal buffer_bytes,flushes
   buf=buffers.pop(index);buffer_bytes-=len(buf)
   packed=lzma.compress(buf,preset=1)
   with (work/('partition-%08d.xz'%index)).open('ab') as raw:raw.write(packed)
   flushes+=1
  with lzma.open(source,'rt') as inp:
   for line in inp:
    if not re.match(r'^\d+ \d+ \d+ \d+ ',line):
     assert not total,'header after records';header.append(line)
     m=re.match(r'-grid dim = \(\s*(\d+),\s*(\d+),\s*(\d+)\s*\)',line)
     if m:grid=tuple(map(int,m.groups()))
     continue
    assert grid
    fields=line.split(maxsplit=4);x,y,z,warp=map(int,fields[:4]);assert x<grid[0] and y<grid[1] and z<grid[2] and 0<=warp<32
    index=((z*grid[1]+y)*grid[0]+x)//span
    b=line.encode();buffers.setdefault(index,bytearray()).extend(b);buffer_bytes+=len(b);peak_buffer_bytes=max(peak_buffer_bytes,buffer_bytes);total+=1;expanded+=len(b)
    if len(buffers[index])>=2*1024**2:flush_one(index)
    while buffer_bytes>=64*1024**2:flush_one(max(buffers,key=lambda i:len(buffers[i])))
    if total%65536==0:assert shutil.disk_usage(work).free>=10*1024**3,'NAS reserve'
  for index in list(buffers):flush_one(index)
  for file in work.glob('partition-*.xz'):
   with file.open('rb') as f:os.fsync(f.fileno())
  assert total and any('-accelsim tracer version = 7' in x for x in header)
  state.update(partition_buffer_bound_bytes=64*1024**2,partition_peak_buffer_bytes=peak_buffer_bytes,partition_compressors_max=1,partition_flushes=flushes,partition_complete=True,header=header,grid=grid,records=total,raw_expanded_body_bytes=expanded,partition_members=[{'name':p.name,'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(work.glob('partition-*.xz'))])
  save(checkpoint,state)
 else:
  for x in state['partition_members']:
   p=work/x['name'];assert p.stat().st_size==x['bytes'] and sha(p)==x['sha256']
 for part in sorted(work.glob('partition-*.xz')):
  index=int(part.stem.split('-')[1]);frame=work/('group-%08d.xz'%index);key=str(index)
  if key in state['groups']:
   q=state['groups'][key];assert frame.stat().st_size==q['bytes'] and sha(frame)==q['sha256'] and crc(frame)==q['expanded_bytes'];continue
  if frame.exists():
   quarantine=frame.with_name(frame.name+'.unsealed-recovery-'+str(time.time_ns()));frame.rename(quarantine)
  scratch=work/('sort-%08d'%index)
  if scratch.exists():
   assert work.resolve() in scratch.resolve().parents
   scratch.rename(scratch.with_name(scratch.name+'.unsealed-recovery-'+str(time.time_ns())))
  scratch.mkdir(exist_ok=False);ordered=scratch/'ordered';counts=collections.Counter();records=0;expanded=0
  cmd=['/usr/bin/sort','-s','--parallel=1','-S64M','-T',str(scratch),'-k3,3n','-k2,2n','-k1,1n','-k4,4n','-o',str(ordered)]
  with (scratch/'sort.log').open('xb') as log:
   sort=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log,env={'PATH':'/usr/bin:/bin','LC_ALL':'C'})
   try:
    with lzma.open(part,'rt') as inp:
     for line in inp:
      fields=line.split(maxsplit=4);k=tuple(map(int,fields[:4]));counts[k]+=1;records+=1;expanded+=len(line.encode())
      assert expanded*3<budget,'per-shard expanded scratch bound'
      sort.stdin.write(line.encode())
    sort.stdin.close();assert sort.wait()==0
   except BaseException:
    sort.terminate();sort.wait();raise
  assert len(counts)<=span*32,'more than32warps/CTA'
  with frame.open('xb') as raw:
   with lzma.LZMAFile(raw,'w',preset=1) as compressed:
    def write(s):compressed.write(s.encode())
    previous_cta=None;previous_warp=None
    with ordered.open() as seq:
     for line in seq:
      fields=line.split(maxsplit=4);cta=tuple(map(int,fields[:3]));warp=int(fields[3])
      if cta!=previous_cta:
       if previous_cta is not None:write('\n#END_TB\n')
       write('\n#BEGIN_TB\nthread block = %d,%d,%d\n'%cta);previous_cta=cta;previous_warp=None
      if warp!=previous_warp:write('\nwarp = %d\ninsts = %d\n'%(warp,counts[(*cta,warp)]));previous_warp=warp
      write(fields[4])
    write('\n#END_TB\n')
   raw.flush();os.fsync(raw.fileno())
  q={'bytes':frame.stat().st_size,'sha256':sha(frame),'expanded_bytes':crc(frame),'records':records,'warps':len(counts),'ctas':len(set(x[:3] for x in counts)),'max_counter_keys':len(counts),'sort_cmd':cmd,'source_partition_sha256':sha(part),'closed_reopened_crc':True}
  state['groups'][key]=q;save(checkpoint,state)
  # Only our derived uncompressed scratch is removed after frame close/CRC/SHA.
  resolved=scratch.resolve();assert work.resolve() in resolved.parents
  shutil.rmtree(resolved)
  if stop_after and len(state['groups'])>=stop_after:raise SystemExit(75)
 header=work/'header.xz'
 if not header.exists():compress(header,(''.join(state['header'])+'\n').encode())
 if dest.exists():
  receipt=work/'GROUP_RECEIPT.json'
  if receipt.exists():
   q=json.loads(receipt.read_text());assert q['grouped_sha256']==sha(dest) and q['expanded_bytes']==crc(dest);return q
  dest.rename(dest.with_name(dest.name+'.unsealed-recovery-'+str(time.time_ns())))
 with dest.open('xb') as out:
  for p in [header]+[work/('group-%08d.xz'%int(k)) for k in sorted(state['groups'],key=int)]:
   with p.open('rb') as inp:
    for b in iter(lambda:inp.read(1048576),b''):out.write(b)
  out.flush();os.fsync(out.fileno())
 expanded=crc(dest);assert sum(q['records'] for q in state['groups'].values())==state['records']
 rec={'status':'GROUPED_ALL_SHARDS_CRC_PASS','source':str(source),'source_sha256':source_sha,'grouped':str(dest),'grouped_sha256':sha(dest),'grouped_bytes':dest.stat().st_size,'expanded_bytes':expanded,'records':state['records'],'ctas':sum(q['ctas'] for q in state['groups'].values()),'warps':sum(q['warps'] for q in state['groups'].values()),'shards':len(state['groups']),'cta_span':span,'sort_memory_bytes':64*1024**2,'partition_compressors_max':1,'partition_buffer_bound_bytes':64*1024**2,'per_shard_scratch_budget':budget,'source_keep':True,'closed_reopened_full_xz_crc':True}
 save(work/'GROUP_RECEIPT.json',rec);return rec
def main():
 p=argparse.ArgumentParser();p.add_argument('source');p.add_argument('dest');p.add_argument('work');p.add_argument('--cta-span',type=int,default=64);p.add_argument('--scratch-budget',type=int,default=64*1024**3);p.add_argument('--stop-after-shards',type=int,default=0);a=p.parse_args()
 print(json.dumps(group(pathlib.Path(a.source),pathlib.Path(a.dest),pathlib.Path(a.work),a.cta_span,a.scratch_budget,a.stop_after_shards)))
if __name__=='__main__':main()

