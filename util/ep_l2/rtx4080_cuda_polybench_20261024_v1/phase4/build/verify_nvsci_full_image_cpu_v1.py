from pathlib import Path
import json,sys,math,hashlib,gzip,time,os,collections
os.nice(15)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ppm(p):
 b=p.read_bytes();i=0;t=[]
 while len(t)<4:
  while b[i:i+1].isspace():i+=1
  if b[i:i+1]==b'#':i=b.index(b'\n',i)+1;continue
  j=i
  while b[i:i+1] and not b[i:i+1].isspace():i+=1
  t.append(b[j:i])
 i+=2 if b[i:i+2]==b'\r\n' else 1
 assert t[0]==b'P6' and t[3]==b'255';w,h=map(int,t[1:3]);data=b[i:];assert len(data)==w*h*3
 return w,h,data
# Acceptance fixed before reading observed output: every output RGB channel <=4.
# At 1024^2 theta=.5, two 8-bit fractional interpolation axes contribute <2 byte
# error, channel normalization/truncation <1 and grayscale truncation <1.
# Float coordinate rounding is below one byte additional error margin in this bound.
def run(taskpath,runtime,out):
 out.mkdir(exist_ok=False);task=json.loads(taskpath.read_text());task=task[0] if isinstance(task,list) else task;assert task['program']=='cudaNvSci'
 for x in task['source_files']:assert sha(Path(x['path']))==x['sha256'],'source changed'
 f=task['input_files'][0];p=runtime/Path(f['path']).name;assert sha(p)==f['sha256'],'runtime input bytes changed'
 w,h,img=ppm(p);assert (w,h)==(1024,1024),'frozen default profile only'
 actual=runtime/(p.stem+'_out.ppm');aw,ah,a=ppm(actual);assert (aw,ah)==(w,h)
 co=math.cos(.5);si=math.sin(.5);prediction=bytearray();hist=collections.Counter();unequal_rgb=0;start=time.time()
 for y in range(h):
  v=y-h/2
  for x in range(w):
   u=x-w/2;tx=u*co-v*si+w/2-.5;ty=v*co+u*si+h/2-.5;ix=math.floor(tx);iy=math.floor(ty);fx=tx-ix;fy=ty-iy
   indices=[((iy%h)*w+ix%w)*3,((iy%h)*w+(ix+1)%w)*3,(((iy+1)%h)*w+ix%w)*3,(((iy+1)%h)*w+(ix+1)%w)*3];weights=[(1-fx)*(1-fy),fx*(1-fy),(1-fx)*fy,fx*fy]
   rgb=[max(0,min(255,int(sum(img[i+c]*v for i,v in zip(indices,weights))))) for c in range(3)];gray=int(rgb[0]*.3+rgb[1]*.59+rgb[2]*.11);prediction.extend([gray]*3);offset=(y*w+x)*3
   unequal_rgb+=len(set(a[offset:offset+3]))!=1
   hist.update(abs(a[offset+c]-gray) for c in range(3))
 maxerror=max(hist);bad=sum(v for k,v in hist.items() if k>4);status='INDEPENDENT_FULL_1024_SQUARED_TEXTURE_ROTATE_GRAYSCALE_EPSILON4_PASS' if bad==0 and unequal_rgb==0 else 'INDEPENDENT_FULL_IMAGE_DIFFERENCE_RETAINED'
 with gzip.open(out/'CPU_REFERENCE_RGB.bin.gz','wb',compresslevel=1) as g:g.write(prediction)
 report={'status':status,'task_id':task['task_id'],'task_manifest_sha256':sha(taskpath),'runtime':str(runtime),'source_files':task['source_files'],'input_sha256':sha(p),'actual_output_sha256':sha(actual),'prediction_payload_sha256':hashlib.sha256(prediction).hexdigest(),'checker_sha256':sha(Path(__file__)),'width':w,'height':h,'checked_pixels':w*h,'checked_channels':len(a),'max_abs_channel_error':maxerror,'channels_over_fixed4':bad,'non_grayscale_pixels':unequal_rgb,'abs_error_histogram':dict(sorted(hist.items())),'all_pixels_required':True,'mismatch_fraction_relaxation':False,'tolerance_fixed_before_observation':4,'math_reference':'Independent scalar bilinear wrap texture lookup with half-texel centers after theta0.5 normalized rotation, uchar channel truncation, then double 0.3/0.59/0.11 grayscale truncation; original shape1024^2','texture_fraction_reference':'https://docs.nvidia.com/cuda/archive/12.9.1/cuda-c-programming-guide/index.html#linear-filtering','tolerance_basis':'Two 8-fractional-bit texture axes (<2 byte interpolation perturbation), uchar and grayscale truncation margins; every RGB channel <=4; float coordinate error at theta.5 size1024 is small compared with byte margin. This is bounded image agreement, not bit-exact texture implementation or trace producer qualification.','GPU_calls':False,'source_and_runtime_read_only':True,'elapsed_cpu_s':time.time()-start}
 (out/'PROOF.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report));return 0 if status.endswith('_PASS') else 2
if __name__=='__main__':
 try:sys.exit(run(Path(sys.argv[1]),Path(sys.argv[2]),Path(sys.argv[3])))
 except Exception as e:print(json.dumps({'status':'REJECTED','error':repr(e)}));sys.exit(2)
