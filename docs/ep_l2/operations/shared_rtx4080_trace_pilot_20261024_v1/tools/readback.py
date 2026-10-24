#!/usr/bin/env python3
import pathlib,json,hashlib,os,time
base=pathlib.Path('/root/share/mnt164/huangrulin/traces/rtx4080_sm89/pilot_20261024_v1')
bundle=base/'expanded/rtx4080_asset_pilot_20261024_v1'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for x in iter(lambda:f.read(1048576),b''):h.update(x)
 return h.hexdigest()
out={'status':'PASS','independent_full_readbacks':[],'namespace':'174-new shared mount','true164_root':'/home/shared/huangrulin/traces/rtx4080_sm89/pilot_20261024_v1'}
for cwd in ['/root/workspace','/root/data']:
 os.chdir(cwd)
 m=json.loads((bundle/'MANIFEST.json').read_text())
 for x in m['files']:
  p=bundle/x['path'];assert p.stat().st_size==x['bytes'] and sha(p)==x['sha256'],x['path']
 assert sha(base/'payload.tar')=='17e4fa4b946ccbd2e3472d37d821bcb5488ed939fc0e0e93cd7bf4dea94dcac3'
 out['independent_full_readbacks'].append({'cwd':os.getcwd(),'files':len(m['files']),'member_bytes':sum(x['bytes'] for x in m['files']),'archive_bytes':(base/'payload.tar').stat().st_size,'status':'PASS','unix':time.time()})
(base/'READBACK_174NEW.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out))
