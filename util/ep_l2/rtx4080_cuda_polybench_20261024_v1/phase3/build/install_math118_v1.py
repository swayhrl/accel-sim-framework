import pathlib,urllib.request,gzip,json,hashlib,subprocess
R=pathlib.Path('/home/huangrulin/workspace/rtx4080_cuda_polybench_20261024_v1');base=R/'toolchains/math_cuda118_v1';base.mkdir(exist_ok=False);prefix=base/'prefix';prefix.mkdir();url='https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/';raw=urllib.request.urlopen(url+'Packages.gz',timeout=120).read();(base/'Packages.gz').write_bytes(raw);text=gzip.decompress(raw).decode();wanted=['libcusparse-dev-11-8','libcusparse-11-8','libcusolver-dev-11-8','libcusolver-11-8','libcublas-dev-11-8','libcublas-11-8','libnpp-dev-11-8','libnpp-11-8'];allpk={}
for stanza in text.split('\n\n'):
 d={}
 for l in stanza.splitlines():
  if l and not l.startswith(' ') and ': ' in l:k,v=l.split(': ',1);d[k]=v
 if d.get('Package') in wanted:allpk.setdefault(d['Package'],[]).append(d)
recs=[]
for name in wanted:
 candidates=allpk[name];d=sorted(candidates,key=lambda x:x['Version'])[-1];p=base/pathlib.Path(d['Filename']).name;payload=urllib.request.urlopen(url+d['Filename'],timeout=180).read();assert hashlib.sha256(payload).hexdigest()==d['SHA256'];p.write_bytes(payload);subprocess.run(['dpkg-deb','-x',str(p),str(prefix)],check=True);r={'package':name,'metadata':d,'path':str(p),'sha256':d['SHA256'],'bytes':len(payload)};recs.append(r);print(name,len(payload),flush=True);(R/'manifests/PRIVATE_CUDA118_MATH_DEPENDENCIES_V1.json').write_text(json.dumps(recs,indent=2)+'\n')
