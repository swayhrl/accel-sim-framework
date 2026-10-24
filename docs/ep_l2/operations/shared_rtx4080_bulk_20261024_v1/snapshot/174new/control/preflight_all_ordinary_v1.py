#!/usr/bin/env python3
import pathlib,json,subprocess,hashlib,time,os,re
R=pathlib.Path('/data/c16/rtx4080_suite_fill_20261024_v1');C=R/'control';W=R/'preflight_maps_v1';W.mkdir(exist_ok=True)
alljobs=[json.loads(p.read_text()) for p in (C/'capture_jobs').glob('*.json')];unique={j['task']['binary_sha256']:j['task'] for j in alljobs};rows=[];deadline=time.time()+7200
identity={'pid':os.getpid(),'start_ticks':pathlib.Path('/proc/self/stat').read_text().split(') ',1)[1].split()[19],'deadline_unix':deadline,'no_gpu_execution':True,'max_workers':1};(C/'CPU_PREFLIGHT_IDENTITY_V1.json').write_text(json.dumps(identity,indent=2)+'\n')
for digest,t in unique.items():
 if time.time()>deadline:break
 out=W/digest;status='PENDING';bad=[];start=time.time()
 try:
  if not out.exists():
   p=subprocess.run(['nice','-n','15','python3',str(C/'make_semantic_map_v2.py'),t['argv'][0],str(out)],capture_output=True,text=True,timeout=300)
   (W/(digest+'.log')).write_text(p.stdout+p.stderr)
   assert p.returncode==0,'MAP_PREFLIGHT_HOLD'
  m=json.loads((out/'manifest.json').read_text());assert m['binary_sha256']==digest
  for ins in m['instructions']:
   tok=ins['sass'].split();op=tok[1] if tok[0].startswith('@') else tok[0]
   if op.startswith(('CALL','RET','JMX','BRX','LDGSTS','CPASYNC','TEX','TLD','SULD','SUST','SUATOM','UTMA','WGMMA','WARPSYNC','BAR.WARP')):bad.append({'function':ins['function'],'pc':ins['pc'],'sass':ins['sass']})
  status='SPECIAL_STATIC_DOMAIN' if bad else 'STATIC_EMBEDDED_ORDINARY_PREFLIGHT_PASS_NOT_RUNTIME_QUALIFICATION'
 except Exception as e:status='MAP_PREFLIGHT_HOLD';error=repr(e)
 rows.append({'binary_sha256':digest,'binary':t['argv'][0],'program':t['program'],'status':status,'unsupported_sites':bad,'map_path':str(out),'elapsed_s':time.time()-start,'error':locals().get('error') if status=='MAP_PREFLIGHT_HOLD' else None})
 tmp=C/'CPU_PREFLIGHT_ALL_ORDINARY_V1.tmp';tmp.write_text(json.dumps({'identity':identity,'updated_unix':time.time(),'unique_total':len(unique),'complete':len(rows)==len(unique),'rows':rows},indent=2)+'\n');os.replace(tmp,C/'CPU_PREFLIGHT_ALL_ORDINARY_V1.json')
print('complete',len(rows),'of',len(unique))
