#!/usr/bin/env python3
import pathlib,subprocess,lzma,json,hashlib,random,time,shutil,fcntl,os
R=pathlib.Path('/data/c16/rtx4080_suite_fill_20261024_v1');N=R/'nas_rtx4080';root=N/'inflight'/('group_qualification_v2_'+str(int(time.time())));root.mkdir(exist_ok=False)
lock=open(R/'control/RTX4080_LOCAL_IO.lock','a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
tool=R/'control/postprocess_nas_sharded_v2.py';reference=pathlib.Path('/data/c16/ada_trace_semantics_20261024_v1/postprocess_v7.py')
receipts=[]
def raw_fixture(grid):
 header='-kernel name = GROUPING_FIXTURE\n-grid dim = (%d,%d,%d)\n-block dim = (37,1,1)\n-accelsim tracer version = 7\n\n'%grid
 keys=[(x,y,z,w) for z in range(grid[2]) for y in range(grid[1]) for x in range(grid[0]) for w in range(2)]
 random.Random(23).shuffle(keys);lines=[]
 for step in range(7):
  for x,y,z,w in keys:
   n=3+(x+3*y+6*z+w)%5
   if step>=n:continue
   mask='00000000' if step==1 else ('0000001f' if w else 'ffffffff')
   lines.append('%d %d %d %d %04x %s 0 NOP 0 0 0 opaque_typed_payload_cta_%d_%d_%d_warp%d_step%d\n'%(x,y,z,w,step*16,mask,x,y,z,w,step))
 return (header+''.join(lines)).encode()
cases=[('synthetic2d',(3,2,1)),('synthetic3d',(3,2,2)),('actual_constant65',None)]
for name,grid in cases:
 base=root/name;ref=base/'ref/traces';new=base/'new/traces';ref.mkdir(parents=True);new.mkdir(parents=True)
 raw='kernel-1-fixture.trace.xz'
 if grid:
  payload=raw_fixture(grid)
  for d in [ref,new]:
   with lzma.open(d/raw,'wb',preset=1) as f:f.write(payload)
 else:
  actual=pathlib.Path('/data/c16/ada_trace_semantics_20261024_v1/attempts/constant65_v7_final_attempt2/traces')
  src=next(actual.glob('*.trace.xz'))
  for d in [ref,new]:shutil.copy2(src,d/raw)
 for d in [ref,new]:(d/'kernelslist_ctx_fixture').write_text('MemcpyHtoD,0x1000,260\n'+raw+'\n')
 cp=subprocess.run(['python3',str(reference),str(ref)],capture_output=True,text=True);assert cp.returncode==0,cp.stderr
 work=base/'work'
 cmd=['python3',str(tool),str(new/raw),str(new/raw.replace('.trace.xz','.traceg.xz')),str(work),'--cta-span','1']
 crash=subprocess.run(cmd+['--stop-after-shards','1'],capture_output=True,text=True);assert crash.returncode==75,crash.stderr
 assert not (new/raw.replace('.trace.xz','.traceg.xz')).exists()
 resume=subprocess.run(cmd,capture_output=True,text=True);assert resume.returncode==0,resume.stderr
 grouped=new/raw.replace('.trace.xz','.traceg.xz');expected=ref/raw.replace('.trace.xz','.traceg.xz')
 with lzma.open(grouped,'rb') as f:a=f.read()
 with lzma.open(expected,'rb') as f:b=f.read()
 assert a==b,'decompressed CTA/warp byte mismatch'
 xz=subprocess.run(['xz','-dc',str(grouped)],capture_output=True);assert xz.returncode==0 and xz.stdout==b
 assert a.count(b'-kernel name = ')==1
 rec={'case':name,'grid':grid,'status':'PASS_BYTE_IDENTICAL_REFERENCE','crash_exit':75,'resume_exit':0,'python_lzma_crc_eof':True,'standard_xz_crc_eof':True,'header_instances':1,'plain_sha256':hashlib.sha256(a).hexdigest(),'plain_bytes':len(a),'raw_sha256':hashlib.sha256((new/raw).read_bytes()).hexdigest(),'group_receipt':json.loads((work/'GROUP_RECEIPT.json').read_text())}
 receipts.append(rec)
result={'status':'PASS','kind':'POSTPROCESS_QUALIFICATION_ONLY','root':str(root),'source_keep':True,'sort_order':'z,y,x,warp numeric stable; CUDA linear block index x+Nx*(y+Ny*z)','cases':receipts,'tool_sha256':hashlib.sha256(tool.read_bytes()).hexdigest(),'reference_sha256':hashlib.sha256(reference.read_bytes()).hexdigest(),'bounded_memory':'sort64MiB; singleXZ preset1 compressor+64MiB total shard buffers; per-shard counters<=CTAspan*32','scratch':'NAS-only per-shard64GiB default; raw/group/partition checkpoints on NAS, no109 expanded scratch'}
(R/'control/POSTPROCESS_NAS_V2_QUALIFICATION_RECEIPT.json').write_text(json.dumps(result,indent=2)+'\n')
(N/'receipts'/(root.name+'.json')).write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result));fcntl.flock(lock,fcntl.LOCK_UN)

