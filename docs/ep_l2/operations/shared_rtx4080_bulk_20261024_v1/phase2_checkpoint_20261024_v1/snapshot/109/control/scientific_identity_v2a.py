import json,hashlib
from scientific_identity_v2 import identity as base_identity,physical
def identity(t):
 o=base_identity(t)
 if t.get('source_archive_sha256'):o['source_archive_sha256']=t['source_archive_sha256']
 return o
def key(t):return hashlib.sha256(json.dumps(identity(t),sort_keys=True,separators=(',',':')).encode()).hexdigest()
