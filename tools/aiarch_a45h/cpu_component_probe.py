"""Frozen CPU-only component probe; synthetic arrays are not training states."""
import ctypes,hashlib,json,math,os,pathlib,resource,struct,sys,time
ROOT=pathlib.Path(os.environ['A45H_OUTPUT']);OLD=pathlib.Path(os.environ['A45H_OLD_READONLY'])
pre=json.loads((ROOT/'preregister.json').read_text());mode=sys.argv[1];limit=int(sys.argv[2])
assert limit in pre['design']['thread_limits'] and os.environ['OMP_THREAD_LIMIT']==str(limit)
module=OLD/'software_sources/gsscale/cpu_adam/cpu_adam.cpython-310-x86_64-linux-gnu.so'
assert hashlib.sha256(module.read_bytes()).hexdigest()==pre['identity'][str(module.relative_to(OLD))]['sha256']
import torch
import intel_extension_for_pytorch as ipex
assert torch.__version__=='2.2.0+cu121' and ipex.__version__=='2.2.0+cpu'
assert not torch.cuda.is_initialized()
def forbidden(*a,**kw):raise RuntimeError('A45H_FORBIDDEN_CUDA_INITIALIZATION')
torch.cuda._lazy_init=forbidden
torch.set_num_threads(1);torch.set_num_interop_threads(1);torch.manual_seed(42)
sys.path.insert(0,str(module.parent));import cpu_adam
assert pathlib.Path(cpu_adam.__file__)==module
lib=ctypes.CDLL(str(module));lib.omp_get_thread_limit.restype=ctypes.c_int
assert lib.omp_get_thread_limit()==limit
fp=lambda x:struct.unpack('<f',struct.pack('<f',x))[0]
records=[];numeric=[]
def tensorhash(x):return hashlib.sha256(x.numpy().tobytes()).hexdigest()
def timed(fn,reset,verify,label):
 raw=[];warm=[]
 for i in range(10):
  reset();t=time.perf_counter_ns();out=fn();dt=(time.perf_counter_ns()-t)/1e9
  verify(out)
  (warm if i<3 else raw).append(dt)
 records.append(dict(label,seconds=raw,warmup_seconds=warm))
 print(json.dumps({'done':label,'median_seconds':sorted(raw)[3]}),flush=True)
if mode=='scan':
 for n in pre['design']['scan_N']:
  gen=torch.Generator().manual_seed(42);permutation=torch.randperm(n,generator=gen)
  initial=torch.zeros(n,dtype=torch.int8);initial[::97]=15
  trigger=torch.arange(0,n,97,dtype=torch.int32)
  for fraction in pre['design']['valid_ID_fractions']:
   ids=permutation[:int(n*fraction)].sort().values.to(torch.int32).contiguous()
   expected=torch.unique(torch.cat((ids,trigger)),sorted=True)
   counter=initial.clone();expected_counter=initial+1;expected_counter[expected.long()]=0
   label={'function':'calculate_update_ids','N':n,'valid_fraction':fraction,'valid_count':ids.numel(),'update_count':expected.numel(),'limit':limit,'input_sha256':{'ids':tensorhash(ids),'counter':tensorhash(initial)}}
   def check_ids(out):
    assert out.dtype==torch.int32 and torch.equal(out,expected)
    assert torch.equal(counter,initial)
   with torch.no_grad():
    timed(lambda:cpu_adam.calculate_update_ids(ids,counter,n),lambda:counter.copy_(initial),check_ids,label)
    def check_counter(out):assert torch.equal(counter,expected_counter)
    timed(lambda:cpu_adam.update_counter(counter,expected),lambda:counter.copy_(initial),check_counter,dict(label,function='update_counter'))
   numeric.append({'N':n,'valid_fraction':fraction,'exact_ID_union':True,'exact_counter_reset':True,'update_count':expected.numel()})
  del permutation,initial,trigger,ids,expected,counter,expected_counter
elif mode=='update':
 for n,cols in pre['design']['update_shapes']:
  torch.manual_seed(42);w0=torch.randn(n,cols)*0.2;g=torch.randn_like(w0)*0.01;m0=torch.randn_like(w0)*0.001;v0=torch.rand_like(w0)*0.01+0.001
  w=w0.clone();m=m0.clone();v=v0.clone();counter=torch.zeros(n,dtype=torch.int8)
  ids=torch.arange(n,dtype=torch.int32);ids64=ids.long();output=torch.empty_like(w0)
  b1,b2,lr,eps=map(fp,[.9,.999,.001,1e-15]);step=10
  mr=b1*m0+(1-b1)*g;vr=b2*v0+(1-b2)*g*g
  def wreference(s):return w0-fp(lr/fp(1-math.pow(b1,s)))*mr/(torch.sqrt(vr)/fp(math.sqrt(fp(1-math.pow(b2,s))))+eps)
  wr=wreference(step);fr=wreference(step+1)
  fixture_hash={k:tensorhash(x) for k,x in [('w',w0),('g',g),('m',m0),('v',v0)]}
  errors={'weights':0.,'moment1':0.,'moment2':0.,'forward':0.}
  def reset():w.copy_(w0);m.copy_(m0);v.copy_(v0)
  def maxerr(x,y):
   assert torch.isfinite(x).all().item()
   e=float((x-y).abs().max());assert e<=1e-5,e
   return e
  def check_update(out):
   for key,a,b in [('weights',w,wr),('moment1',m,mr),('moment2',v,vr)]:errors[key]=max(errors[key],maxerr(a,b))
   assert torch.count_nonzero(counter).item()==0
  def check_forward(out):
   errors['forward']=max(errors['forward'],maxerr(output,fr))
   assert torch.equal(w,w0) and torch.equal(m,m0) and torch.equal(v,v0)
   assert torch.count_nonzero(counter).item()==0
  label={'N':n,'cols':cols,'U':n,'counter':0,'step':step,'limit':limit,'input_sha256':fixture_hash}
  with torch.no_grad():
   timed(lambda:cpu_adam.adam_deferred_update(w,g,m,v,ids,counter,step,lr,b1,b2,eps),reset,check_update,dict(label,function='adam_deferred_update'))
   timed(lambda:cpu_adam.adam_for_next_with_counter(w,g,m,v,ids64,output,counter,step,lr,b1,b2,eps),reset,check_forward,dict(label,function='adam_for_next_with_counter'))
  numeric.append({'N':n,'cols':cols,'max_abs_errors':errors,'forward_does_not_mutate_states':True,'all_finite':True,'fixture_sha256':fixture_hash,'weight_after_forward_reset_equals_input_sha256':tensorhash(w),'forward_output_sha256':tensorhash(output)})
  del w0,g,m0,v0,w,m,v,ids,ids64,counter,output,mr,vr,wr,fr
else:raise ValueError(mode)
assert not torch.cuda.is_initialized()
receipt={'status':'PASS','classification':'CPU_COMPONENT_NATIVE','synthetic':True,'mode':mode,'limit':limit,'torch':torch.__version__,'ipex':ipex.__version__,'cuda_initialized_before':False,'cuda_initialized_after':False,'omp_get_thread_limit':lib.omp_get_thread_limit(),'torch_threads':torch.get_num_threads(),'torch_interop_threads':torch.get_num_interop_threads(),'peak_rss_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,'records':records,'numeric':numeric}
(ROOT/f'{mode}_{limit}.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('COMPONENT_PASS',mode,limit,receipt['peak_rss_bytes'],flush=True)
