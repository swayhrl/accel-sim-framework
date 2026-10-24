import pathlib,os,subprocess,time,secrets,json,hashlib,sys
R=pathlib.Path('/home/huangrulin/workspace/rtx4080_cuda_polybench_20261024_v1');D=R/'toolchains/optional_platform_v1/prefix/usr';C=R/'toolchains/modern_complete_deps_v1/prefix/usr';cwd=pathlib.Path.cwd();auth=cwd/'private_probe.Xauthority';assert not auth.exists();fd=os.open(auth,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600);os.close(fd)
num=next(n for n in range(320,420) if not pathlib.Path('/tmp/.X11-unix/X'+str(n)).exists() and not pathlib.Path('/tmp/.X'+str(n)+'-lock').exists());display=':'+str(num);cookie=secrets.token_hex(16);env=os.environ.copy();env.update(DISPLAY=display,XAUTHORITY=str(auth),VK_ICD_FILENAMES='/usr/share/vulkan/icd.d/nvidia_icd.json',VK_LAYER_PATH=str(D/'share/vulkan/explicit_layer.d'));env.pop('VK_INSTANCE_LAYERS',None);child=None
try:
 x=subprocess.run([str(D/'bin/xauth'),'-f',str(auth),'add',display,'MIT-MAGIC-COOKIE-1',cookie],env=env,capture_output=True,text=True);assert x.returncode==0,x.stderr
 with (cwd/'private_Xvfb.log').open('x') as log:
  child=subprocess.Popen([str(D/'bin/Xvfb'),display,'-screen','0','1024x768x24','-nolisten','tcp','-auth',str(auth),'-noreset'],env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT)
  for k in range(100):
   if child.poll() is not None:raise RuntimeError('PRIVATE_XVFB_EARLY_EXIT '+str(child.returncode))
   if pathlib.Path('/tmp/.X11-unix/X'+str(num)).exists():break
   time.sleep(.1)
  else:raise RuntimeError('PRIVATE_XVFB_START_TIMEOUT')
  time.sleep(.3)
  info=subprocess.run([str(D/'bin/vulkaninfo'),'--summary'],env=env,capture_output=True,text=True,timeout=60);(cwd/'vulkaninfo_summary.log').write_text(info.stdout+info.stderr);print('VULKANINFO_EXIT',info.returncode);print(info.stdout[-8000:]);assert info.returncode==0
  require='ce6cba36-415b-4e27-40e2-bded6bc1ee59';canonical=info.stdout.lower();assert 'nvidia' in canonical and '4080' in canonical and require in canonical,'NOT_EXPECTED_REAL_GPU_UUID'
  target=pathlib.Path(sys.argv[1]).resolve(); expected=sys.argv[2]
  assert (R/'modern_vulkan_finite4_v1').resolve() in target.parents
  assert hashlib.sha256(target.read_bytes()).hexdigest()==expected,'TARGET_BINARY_IDENTITY_CHANGED'
  run=subprocess.run([str(target)]+sys.argv[3:],env=env,capture_output=True,text=True,timeout=180)
  (cwd/'vulkan_application.log').write_text(run.stdout+run.stderr)
  print('VULKAN_APPLICATION_BINARY',str(target),'SHA256',expected)
  print('VULKAN_APPLICATION_EXIT',run.returncode);print(run.stdout+run.stderr)
  assert run.returncode==0 and 'EP_FINITE_FRAMES_COMPLETE 4' in run.stdout,'FINITE_REAL_GPU_VULKAN_APPLICATION_FAILED'
  print('REAL_NVIDIA_RTX4080_VULKAN_FINITE4_EXECUTION_COMPLETE_NUMERICAL_REVIEW')
finally:
 if child is not None and child.poll() is None:
  child.terminate()
  try:child.wait(timeout=10)
  except subprocess.TimeoutExpired:child.kill();child.wait()
 auth.unlink(missing_ok=True)
