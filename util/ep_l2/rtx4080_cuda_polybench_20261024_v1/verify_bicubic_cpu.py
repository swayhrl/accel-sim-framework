from pathlib import Path
import json,math,hashlib,time,os
os.nice(15)
R=Path('/home/huangrulin/workspace/rtx4080_cuda_polybench_20261024_v1');jobs=[x for x in json.loads((R/'native_control/NATIVE_BATCH_cuda104_v1.json').read_text()) if x['task']['program']=='bicubicTexture'];assert len(jobs)==5
D=Path(jobs[0]['task']['sample_path'])
def load(p):
 b=p.read_bytes();i=0;t=[]
 while len(t)<4:
  while b[i:i+1].isspace():i+=1
  if b[i:i+1]==b'#':i=b.index(b'\n',i)+1;continue
  j=i
  while not b[i:i+1].isspace():i+=1
  t.append(b[j:i])
 i+=2 if b[i:i+2]==b'\r\n' else 1
 return t,b[i:]
_,img=load(D/'data/teapot512.pgm')
def linear_axis(q):
 z=q-.5;i=math.floor(z);t=z-i;return[(min(511,max(0,i)),1-t),(min(511,max(0,i+1)),t)]
def cubic_axis(q,cat=False):
 z=q-.5;i=math.floor(z);t=z-i
 weights=[-.5*t+t*t-.5*t**3,1-2.5*t*t+1.5*t**3,.5*t+2*t*t-1.5*t**3,-.5*t*t+.5*t**3] if cat else [(1-t)**3/6,(3*t**3-6*t*t+4)/6,(-3*t**3+3*t*t+3*t+1)/6,t**3/6]
 return[(min(511,max(0,i-1+k)),w) for k,w in enumerate(weights)]
rows=[]
for x in jobs:
 mode=int(next(z.split('=')[1] for z in x['task']['argv'] if z.startswith('-mode=')));fn=next(z.split('=')[1] for z in x['task']['argv'] if z.startswith('-file='));_,actual=load(Path(x['output'])/fn);xs=[(v-256)*.125+256-27.75 for v in range(512)];ys=[(v-256)*.125+256-189 for v in range(512)]
 if mode==0:xs=[[(int(math.floor(z)),1)] for z in xs];ys=[[(int(math.floor(z)),1)] for z in ys]
 elif mode==1:xs=[linear_axis(z) for z in xs];ys=[linear_axis(z) for z in ys]
 else:xs=[cubic_axis(z,mode==4) for z in xs];ys=[cubic_axis(z,mode==4) for z in ys]
 pred=bytearray();outside=0;start=time.time()
 for yy in ys:
  for xx in xs:
   f=sum(img[iy*512+ix]*wx*wy for iy,wy in yy for ix,wx in xx);outside+=f<0 or f>255;v=max(0,int(f))&255;pred.extend([v]*3)
 diffs=[abs(i-j) for i,j in zip(pred,actual)];row={'task_id':x['task']['task_id'],'mode':mode,'math_reference':'Independent separable scalar interpolation on originaluchar image, source-affine view; nearest/linear/B-spline/Catmull-Rom; fastBicubic compared to mathematically equivalent B-spline (texture8bit fractions add bounded rounding)','epsilon':5,'tolerance_source':'bicubicTexture.cpp MAX_EPSILON_ERROR5, require EVERY channel <=5, no mismatch fraction relaxation','max_abs_error':max(diffs),'channels_over5':sum(v>5 for v in diffs),'mean_abs_error':sum(diffs)/len(diffs),'channels':len(diffs),'outside_u8_math_pixels':outside,'byte_conversion':'truncate to uint then low8 bits, negativeclamp0; Catmull overshoot cast is source-domain limitation','actual_sha256':hashlib.sha256((Path(x['output'])/fn).read_bytes()).hexdigest(),'prediction_payload_sha256':hashlib.sha256(pred).hexdigest(),'source_kernel_sha256':hashlib.sha256((D/'bicubicTexture_kernel.cuh').read_bytes()).hexdigest(),'source_host_sha256':hashlib.sha256((D/'bicubicTexture.cpp').read_bytes()).hexdigest(),'status':'INDEPENDENT_FULL_IMAGE_MATH_EPSILON_PASS' if max(diffs)<=5 else 'INDEPENDENT_FULL_IMAGE_DIFFERENCE_RETAINED','seconds':time.time()-start};rows.append(row);print(mode,row['status'],row['max_abs_error'],row['channels_over5'],outside,flush=True)
(R/'native_control/BICUBIC_ALL5_INDEPENDENT_CPU_V1.json').open('x').write(json.dumps(rows,indent=2)+'\n')
