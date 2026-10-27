import pathlib,sys,os,time,subprocess,signal,json
root=pathlib.Path(sys.argv[1]);kind=sys.argv[2]
if kind=='child':
 signal.signal(signal.SIGTERM,lambda a,b:None)
 subprocess.Popen([sys.executable,'-B',__file__,str(root),'grand'],start_new_session=True)
 time.sleep(20)
elif kind=='grand':
 signal.signal(signal.SIGTERM,lambda a,b:None);time.sleep(20)
else:
 p=subprocess.Popen([sys.executable,'-B',__file__,str(root),'child'],start_new_session=True)
 (root/'FAKE_DESCENDANTS_STARTED.json').write_text(json.dumps(dict(parent=os.getpid(),child=p.pid)))
 p.wait()
