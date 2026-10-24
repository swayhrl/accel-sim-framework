import pathlib,json,os,signal,datetime
P=pathlib.Path;T=P('/root/data/dtc_main_short3_20261024_v1');proof=json.loads((T/'control/CONTROLLER_LAUNCH_R3.json').read_text());p=P('/proc')/str(proof['pid'])
assert int((p/'stat').read_text().rsplit(')',1)[1].split()[19])==proof['start_ticks']
assert 'short3_controller_r3.py' in (p/'cmdline').read_bytes().replace(bytes([0]),b' ').decode()
assert not (T/'control/STORAGE_REVISION_METADATA_HOLD.json').exists()
fd=os.pidfd_open(proof['pid']);signal.pidfd_send_signal(fd,signal.SIGSTOP);os.close(fd)
x={'status':'ONLY_METADATA_CONTROLLER_HELD_MODELS_AND_GUARDS_CONTINUE','controller':proof,'pidfd_exact_generation':True,'user_instruction':'另外安全余量我建议不要卡在10G，可以在5G，另外如果空间不够了，你可以安全的把我们的资产迁移到164，然后删除174-new下的，164和174-new的空间可以认为是完全共享的，只是一个快些一个慢些。','scope':'Prepare lower local disk safety floor at next completed-model boundary; preserve current model and runtime bytes, current exact12start budget','utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
with (T/'control/STORAGE_REVISION_METADATA_HOLD.json').open('x') as f:json.dump(x,f,indent=2,ensure_ascii=False);f.write('\n')
print(json.dumps({'status':x['status'],'metadata_PID':proof['pid']}))
