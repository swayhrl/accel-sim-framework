"""Exact Gaussian16 observed-IO/source stdout oracle; CPU evidence, not a GPU launcher."""
import pathlib,json,hashlib,struct,math,argparse
BINARY='50fad6fdc65b005af1384c83a1b825df405f7b894ed649b98ee145a0b7cd01d1'
SOURCE='8b383f5c5149cb70c84720cac80f9115fe2cfd06907e321e589250fc21a5a5a4'
def need(v,m):
 if not v:raise ValueError(m)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def f32(x):return struct.unpack('<f',struct.pack('<f',x))[0]
def capsule(root,path,count,pin):
 p=pathlib.Path(path);p=p if p.is_absolute()else root/p
 if not p.resolve().is_relative_to(root.resolve()):
  e=json.loads((root/'EXECUTION.json').read_text());remote=pathlib.Path(e['capture_root']);need(p.is_relative_to(remote),'exact captured root capsule alias');p=root/p.relative_to(remote)
 need(p.resolve().is_relative_to(root.resolve())and not p.is_symlink(),'private actual capsule path')
 raw=p.read_bytes();need(len(raw)==count and sha(p)==pin,'capsule bytes/SHA')
 x=list(struct.unpack('<'+'f'*(count//4),raw));need(all(math.isfinite(v)for v in x),'all actual floats finite');return x
def journal(path):
 rows=[l.split('\t')for l in path.read_text().splitlines()]
 need(rows and len(rows[-1])==4 and rows[-1][0]=='EOF'and sum(r[0]=='EOF'for r in rows)==1,'unique terminal IO EOF')
 need(rows[-1][1:3]==['3','2112']and int(rows[-1][3],16)>0,'EOF exact copy count/bytes/context')
 return rows[:-1],rows[-1][3]
def normalize(root):
 rows,ctx=journal(root/'traces/ada-input.tsv');result=[]
 need(len(rows)==9,'exact sync HtoD journal cardinality')
 for i,size in enumerate([1024,1024,64]):
  f,e,c=rows[i*3:i*3+3];n=str(i+1)
  need(len(f)==10 and f[:2]==['ENTRY',n]and f[2]in('cuMemcpyHtoD_v2','cuMemcpyHtoD_v2_ptds')and f[3]==ctx and int(f[4],16)==0 and int(f[5],16)>0 and int(f[6],16)>0,'exact synchronous HtoD API/context/pointers')
  need(e==['API_EXIT',n,'0']and len(c)==6 and c[:3]==['COMPLETE',n,'SYNC_API_SUCCESS_SOURCE_BYTES_FROZEN']and int(f[7])==int(c[3])==size and f[8]==c[4]and c[5]=='HOST_BYTES_EQUAL_CLOSED_CAPSULE_NOT_DEVICE_READBACK','ordered successful HtoD completion')
  result.append(dict(direction='HtoD',ordinal=i+1,context=ctx,device=f[5],bytes=size,sha256=f[8],path=f[9]))
 rows,outctx=journal(root/'traces/ada-output.tsv');need(outctx==ctx and len(rows)==6,'same context exact DtoH EOF/cardinality')
 for i,(size,inp)in enumerate(zip([1024,1024,64],result[:3])):
  e,c=rows[i*2:i*2+2];n=str(i+1)
  need(len(e)==7 and e[:2]==['ENTRY',n]and e[2]in('cuMemcpyDtoH_v2','cuMemcpyDtoH_v2_ptds')and int(e[5],16)>0,'exact synchronous DtoH API/host')
  need(len(c)==9 and c[:2]==['COMPLETE',n]and e[2:5]==c[2:5]and c[8]=='SYNC_DTOH_API_SUCCESS_ACTUAL_HOST_BYTES'and e[3]==ctx and e[4]==inp['device']and int(e[6])==int(c[5])==size,'same actual DtoH range/success/order')
  result.append(dict(direction='DtoH',ordinal=i+1,context=ctx,device=e[4],bytes=size,sha256=c[6],path=c[7]))
 alloc=[l.split('\t')for l in(root/'traces/ada-allocation.tsv').read_text().splitlines()]
 need(len(alloc)==6,'exact three allocations and frees; unknown lifecycle rejected')
 need(alloc[:3]==[['ALLOC',ctx,r['device'],str(r['bytes']),'CUDA_SUCCESS']for r in result[:3]],'actual allocations exact ordered IO ranges')
 need(alloc[3:]==[['FREE',ctx,r['device'],'CUDA_SUCCESS']for r in result[:3]],'all actual allocations released once')
 return result
def forward(a,b):
 a=list(a);b=list(b);m=[0.]*256
 for t in range(15):
  need(a[t*16+t]!=0,'reference zero pivot')
  for i in range(t+1,16):
   m[i*16+t]=a[i*16+t]/a[t*16+t]
   for j in range(t,16):a[i*16+j]-=m[i*16+t]*a[t*16+j]
   b[i]-=m[i*16+t]*b[t]
 return m,a,b
def backsub(a,b):
 x=[0.]*16
 for i in range(15,-1,-1):
  x[i]=b[i]
  for j in range(15,i,-1):x[i]=f32(x[i]-f32(a[i*16+j]*x[j]))
  need(a[i*16+i]!=0,'observed zero pivot');x[i]=f32(x[i]/a[i*16+i])
 return x
def printed(text,left,right,count):
 need(text.count(left)==1 and text.count(right)==1,'unique source output markers')
 tokens=text.split(left,1)[1].split(right,1)[0].split();need(len(tokens)==count,'full source printed array cardinality')
 v=[float(t)for t in tokens];need(all(math.isfinite(x)for x in v),'printed actual finite');return v
def validate(root):
 io=normalize(root);data=[capsule(root,r['path'],r['bytes'],r['sha256'])for r in io];mi,a,b,mo,ao,bo=data
 need(all(v==0 for v in mi)and b==[1.]*16,'actual source m-zero,b-one')
 ranges=sorted((int(r['device'],16),int(r['device'],16)+r['bytes'])for r in io[:3]);need(all(x>0 for x,y in ranges)and all(ranges[i][1]<=ranges[i+1][0]for i in range(2)),'actual distinct nonoverlapping device input ranges')
 need(len({r['context']for r in io})==1 and len({r['device']for r in io[:3]})==3,'one context distinct allocations')
 lamda=f32(-0.01);coeff=[f32(10*math.exp(f32(lamda*i)))for i in range(16)];need(all(abs(a[i*16+j]-coeff[abs(i-j)])<=2e-6 for i in range(16)for j in range(16)),'observedA source deterministic exp recipe bound; not seed inference')
 refm,refa,refb=forward(a,b)
 errors={}
 for name,got,expected in [('m',mo,refm),('a',ao,refa),('b',bo,refb)]:
  delta=max(abs(x-y)for x,y in zip(got,expected));need(all(abs(x-y)<=0.0005*max(1.,abs(y))for x,y in zip(got,expected)),'full actual GPU transition mismatch '+name);errors[name]=delta
 x=backsub(ao,bo);res=max(abs(sum(a[i*16+j]*x[j]for j in range(16))-b[i])for i in range(16));den=max(sum(abs(a[i*16+j])for j in range(16))for i in range(16))*max(map(abs,x))+max(map(abs,b));need(res/max(1.,den)<=1e-5,'independent captured-input residual')
 text=(root/'stdout.log').read_text();need('WG size of kernel 1 = 128, WG size of kernel 2= 16 X 16'in text,'exact launch macro source')
 for name,left,right,n,expected in [('m','Matrix m is:','Matrix a is:',256,mo),('a','Matrix a is:','Array b is:',256,ao),('b','Array b is:','The final solution is:',16,bo),('x','The final solution is:','Time total (including memory transfers)',16,x)]:
  observed=printed(text,left,right,n);need(observed==[float(format(v,'.2f'))for v in expected],'actual printed source array mismatch '+name)
 return dict(status='GAUSSIAN16_OBSERVED_IO_AND_SOURCE_PRINT_QA_CPU_PASS',io=io,full_GPU_output_arrays_observed=True,all16_final_solution_printed_values_observed=True,final_host_float32_array_raw_observed=False,stdout_precision_decimals=2,source_RNG='NONE; actual captured source bytes authoritative; source float exp recipe and libm identity separately bound',reference='independent double forward elimination from actual capturedA,b; all256m/a+16b checked, normalizedresidual1e-5, fixedtransitionbound5e-4; not general fp32 numerical qualification',max_transition_errors=errors,normalized_residual=res/max(1.,den),binary_sha256=BINARY,source_sha256=SOURCE,CUDA_full_state_or_timing_or_consumer_science_qualified=False)
def main():
 p=argparse.ArgumentParser();p.add_argument('--root',required=True);p.add_argument('--output',required=True);a=p.parse_args();root=pathlib.Path(a.root);out=pathlib.Path(a.output);need(not out.exists(),'new QA only');q=validate(root);out.write_text(json.dumps(q,indent=2)+'\n')
if __name__=='__main__':main()
