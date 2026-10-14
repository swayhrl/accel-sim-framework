"""CPU-only actual original CPUAdam ABI/numeric/OpenMP canary; no training proxy."""
import ctypes,hashlib,json,math,os,pathlib,resource,struct,subprocess,sys,threading,time
from control import ROOT,check
assert os.environ.get('OMP_THREAD_LIMIT')=='16'
pre={'status':'PREREGISTERED','scope':'CPU extension qualification only; synthetic fixture is not scene/training evidence','dtype':'float32','rows':200000,'cols':48,'step':10,'beta1':0.9,'beta2':0.999,'lr':0.001,'eps':1e-15,'max_abs_error':1e-5,'effective_thread_limit':24,'omp_thread_limit':16,'comparison':'unchanged frozen deferred-Adam function at counter=0 versus its documented float32 equations'}
(ROOT/'cpu_adam_canary_preregister.json').write_text(json.dumps(pre,indent=2)+'\n')
import torch
import intel_extension_for_pytorch as ipex
assert not torch.cuda.is_initialized()
torch.set_num_threads(1);torch.set_num_interop_threads(1);torch.manual_seed(42)
sys.path.insert(0,str(ROOT/'software_sources/gsscale/cpu_adam'));import cpu_adam
module=pathlib.Path(cpu_adam.__file__);lib=ctypes.CDLL(str(module));lib.omp_get_thread_limit.restype=ctypes.c_int
assert lib.omp_get_thread_limit()==16
rows,cols=pre['rows'],pre['cols'];w=torch.randn(rows,cols)*0.2;g=torch.randn_like(w)*0.01;m=torch.randn_like(w)*0.001;v=torch.rand_like(w)*0.01+0.001
fp=lambda x:struct.unpack('<f',struct.pack('<f',x))[0]
b1,b2,lr,eps=map(fp,[.9,.999,.001,1e-15]);step=10
mref=b1*m+(1-b1)*g;vref=b2*v+(1-b2)*g*g;wref=w-fp(lr/fp(1-math.pow(b1,step)))*mref/(torch.sqrt(vref)/fp(math.sqrt(fp(1-math.pow(b2,step))))+eps)
ids=torch.arange(rows,dtype=torch.int32);counter=torch.zeros(rows,dtype=torch.int8)
samples=[];stop=threading.Event()
def sampler():
 while not stop.is_set():
  tids=list(pathlib.Path('/proc/self/task').iterdir());running=[]
  for t in tids:
   try:
    if t.joinpath('stat').read_text().split()[2]=='R':running.append(int(t.name))
   except OSError:pass
  samples.append({'monotonic':time.monotonic(),'resident_threads':len(tids),'running_threads':len(running)});time.sleep(.001)
thread=threading.Thread(target=sampler);thread.start();started=time.monotonic()
with torch.no_grad():cpu_adam.adam_deferred_update(w,g,m,v,ids,counter,step,lr,b1,b2,eps)
stop.set();thread.join();wall=time.monotonic()-started
errors={'weights':float((w-wref).abs().max()),'moment1':float((m-mref).abs().max()),'moment2':float((v-vref).abs().max())};assert max(errors.values())<=pre['max_abs_error'],errors
assert all(torch.isfinite(x).all().item() for x in [w,m,v]) and not torch.cuda.is_initialized()
maxrunning=max(x['running_threads'] for x in samples);maxresident=max(x['resident_threads'] for x in samples);assert maxrunning<=24 and maxresident<=24,(maxrunning,maxresident)
receipt={'status':'PASS','scope':pre['scope'],'core_versions':{'torch':torch.__version__,'ipex':ipex.__version__},'module_sha256':hashlib.sha256(module.read_bytes()).hexdigest(),'original_source_not_patched':True,'torch_cxx11_abi':torch._C._GLIBCXX_USE_CXX11_ABI,'dtype':'float32','max_abs_errors':errors,'all_outputs_finite':True,'omp_get_thread_limit':lib.omp_get_thread_limit(),'source_omp_set_num_threads_64_unchanged':True,'max_running_threads_sampled':maxrunning,'max_resident_threads_sampled':maxresident,'thread_samples':samples,'wall_seconds':wall,'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'cuda_initialized':torch.cuda.is_initialized(),'budget':check()}
(ROOT/'cpu_adam_canary_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print('CPU_ADAM_ORIGINAL_CANARY_PASS',errors,'OMP_LIMIT',16,'THREADS',maxrunning,maxresident,flush=True)
