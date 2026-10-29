"""Restore exact review patch bytes; does not apply to or modify any Source."""
import hashlib,json,pathlib,sys
p=pathlib.Path(__file__).with_name('SOURCE_CANDIDATE_PATCHES.json')
out=pathlib.Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=True)
for r in json.loads(p.read_text())['patches']:
 name=r['filename'];assert pathlib.Path(name).name==name
 b=r['patch_utf8'].encode();assert hashlib.sha256(b).hexdigest()==r['source_ref']['sha256']
 with (out/name).open('xb') as f:f.write(b)
 print(name,r['source_ref']['sha256'])
