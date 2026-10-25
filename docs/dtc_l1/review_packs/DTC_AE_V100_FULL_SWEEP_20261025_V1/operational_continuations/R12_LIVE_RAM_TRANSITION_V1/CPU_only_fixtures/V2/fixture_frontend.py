import pathlib,json,sys,os,time,threading,subprocess,socket,hashlib,marshal,importlib.util
P=pathlib.Path;R=P(sys.argv[1]);ver=sys.argv[2];patch=sys.argv[3];invalid=sys.argv[4]=='invalid'
spec=importlib.util.spec_from_file_location('_fixture_identity_only',patch);payload=importlib.util.module_from_spec(spec);spec.loader.exec_module(payload)
def gen(pid):return int((P('/proc')/str(pid)/'stat').read_text().rsplit(')',1)[1].split()[19])
sock=socket.socket(socket.AF_UNIX,socket.SOCK_DGRAM);sock.bind(str(R/'model.sock'));sock.settimeout(.2)
modelsource="import socket,sys,time; s=socket.socket(socket.AF_UNIX,socket.SOCK_DGRAM); p=sys.argv[1]; i=0\nwhile True:\n print(i,flush=True);s.sendto(str(i).encode(),p);i+=1;time.sleep(.01)\n"
model=subprocess.Popen([sys.executable,'-u','-c',modelsource,str(R/'model.sock')],stdout=subprocess.PIPE,text=True,stderr=(R/'model.stderr').open('w'))
pipe=[];uds=[];stop=False
def readpipe():
 for line in model.stdout:pipe.append(int(line))
def readuds():
 while not stop:
  try:uds.append(int(sock.recv(100)))
  except socket.timeout:pass
threading.Thread(target=readpipe,daemon=True).start();threading.Thread(target=readuds,daemon=True).start()
tools=R/'tools';tools.mkdir();host=tools/('fixture_host_'+ver+'.py');host.write_text('def resources(spec,fresh_source=False):\n return '+repr({'physical_RAM_pass':False,'disk_pass':True,'telemetry_pass':True,'hard_RSS_cap_bytes':16*1024**3,'fixture_version':ver})+'\n')
native=tools/'sweep_native_cap1m.py';native.write_text('''def run_native(cohort):
 ident='cpu-uuid';out=R/'DTC/run/results'/ident;observations=[{'pid':model.pid,'start_ticks':gen(model.pid)}];frame_identity=id(sys._getframe());before=None;deadline=time.monotonic()+12
 while time.monotonic()<deadline:
  value=resources({},False)
  if (R/'FINISH').exists():
   result={'frame_identity_before':frame_identity,'frame_identity_after':id(sys._getframe()),'model_pid':model.pid,'model_start_ticks':gen(model.pid),'model_alive':model.poll() is None,'pipe':pipe[:],'uds':uds[:],'value':value,'before_sequence':before,'after_sequence':len(pipe),'main_thread':threading.current_thread() is threading.main_thread()};(R/'CHILD_RESULT.json').write_text(json.dumps(result));return
  if before is None and (R/'INJECT_NOW').exists():
   before=len(pipe);(R/'DEBUG_IDENTITY.json').write_text(json.dumps(payload.code_identity(resources)))
  time.sleep(.005)
''')
ns={'__file__':str(native),'R':R,'model':model,'gen':gen,'sys':sys,'time':time,'pipe':pipe,'uds':uds,'json':json,'threading':threading,'hashlib':hashlib,'marshal':marshal,'payload':payload}
exec(compile(host.read_text(),str(host),'exec'),ns)
ns['read_current_authority']=lambda: (json.loads((R/'PROFILE.json').read_text()),None)
exec(compile(native.read_text(),str(native),'exec'),ns)
f=ns['resources'];identity=payload.code_identity(f)
ready={'pid':os.getpid(),'start_ticks':gen(os.getpid()),'model_pid':model.pid,'model_start_ticks':gen(model.pid),'native_source':str(native),'native_sha':hashlib.sha256(native.read_bytes()).hexdigest(),'host_source':str(host),'host_sha':hashlib.sha256(host.read_bytes()).hexdigest(),'resource_code_identity':identity};(R/'READY.json').write_text(json.dumps(ready))
globals().update(ns)
try:ns['run_native']('CPU_FIXTURE')
finally:
 stop=True
 if model.poll() is None:model.terminate();model.wait(timeout=3)
