import pathlib,json,hashlib
B=pathlib.Path(__file__).resolve().parent;P=B.parent/'main/MAIN_SOURCE78_W_ONLY_MODE_CPU_QUALIFICATION_V2.json'
q=json.loads(P.read_bytes());assert q['approved_by']=='EP-MAIN' and not q['application_permission'] and not q['launch_permission']
r=dict(path=str(P),sha256=hashlib.sha256(P.read_bytes()).hexdigest(),bytes=P.stat().st_size)
for p in (B/'scientific_drafts').glob('*.json'):
 s=json.loads(p.read_bytes());s['mode_cpu_qualification_ref']=r if s['mode']=='W_ONLY'else None;s['scientific_option_contract']['CPU_mode_qualification_ref']=s['mode_cpu_qualification_ref'];p.write_text(json.dumps(s,indent=2)+'\n')
