import pathlib,os,shutil,hashlib,json,subprocess,shlex,csv
root=pathlib.Path(os.environ['TASK_DATA']);pack=pathlib.Path('docs/ai_workload_research/review_packs/AI_ARCH_A16_NEQUIP_GREEN_CONTEXT_109_CANARY_V1');j=json.loads((root/'ARCHIVE_PLAN.json').read_text());dest=j['destination'];close=root/'closeout';close.mkdir(exist_ok=True)
shutil.copytree(pack,close/'review_pack',dirs_exist_ok=True)
for p in [pathlib.Path('tools/ai_workload_research/a16_greencontext_canary/publish_archive.py'),root/'verify_node164.py',root/'PUBLISH_ARCHIVE.log',root/'NODE164_READBACK_RECEIPT.json']:
 shutil.copy2(p,close/p.name)
rows=[]
for p in sorted(close.rglob('*')):
 if p.is_file():rows.append({'asset':p.relative_to(close).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(close/'MANIFEST.json').write_text(json.dumps(rows,indent=2)+'\n',encoding='utf-8');manifest_sha=hashlib.sha256((close/'MANIFEST.json').read_bytes()).hexdigest()
subprocess.run(['ssh','-o','BatchMode=yes','hrl174new','test ! -e '+shlex.quote(dest+'/closeout')],check=True)
subprocess.run(['scp','-r',str(close),'hrl174new:'+dest+'/'],check=True)
program="""import pathlib,sys,hashlib,json
p=pathlib.Path(sys.argv[1]);manifest=p/'MANIFEST.json';assert hashlib.sha256(manifest.read_bytes()).hexdigest()==sys.argv[2];rows=json.loads(manifest.read_text())
for r in rows:
 f=p/r['asset'];assert f.stat().st_size==r['bytes'];assert hashlib.sha256(f.read_bytes()).hexdigest()==r['sha256'],r['asset']
print(json.dumps({'status':'NODE164_CLOSEOUT_READBACK_PASS','directory':str(p),'manifest_sha256':sys.argv[2],'items':len(rows),'bytes':sum(r['bytes'] for r in rows),'verified_files':rows}))
"""
cmd='python3 -c '+shlex.quote(program)+' '+shlex.quote(dest+'/closeout')+' '+manifest_sha;r=subprocess.run(['ssh','-o','BatchMode=yes','hrl174new',cmd],check=True,text=True,capture_output=True);receipt=json.loads(r.stdout);(root/'NODE164_CLOSEOUT_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8');(pack/'NODE164_CLOSEOUT_PUBLICATION.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
with (pack/'RAW_INDEX.tsv').open('a',encoding='utf-8',newline='') as f:
 w=csv.writer(f,delimiter='\t',lineterminator='\n')
 for r in rows:w.writerow(['closeout/'+r['asset'],r['bytes'],r['sha256'],dest+'/closeout/'+r['asset'],'PRE_PUBLICATION_CLOSEOUT_SNAPSHOT'])
 w.writerow(['closeout/MANIFEST.json',(close/'MANIFEST.json').stat().st_size,manifest_sha,dest+'/closeout/MANIFEST.json','CLOSEOUT_MANIFEST'])
print(json.dumps({k:v for k,v in receipt.items() if k!='verified_files'},indent=2))
