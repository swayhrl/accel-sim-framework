import json, hashlib
from pathlib import Path
def sha256(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1<<20),b''): h.update(b)
 return h.hexdigest()
def load_index(root):
 root=Path(root); index=json.loads((root/'model.safetensors.index.json').read_text()); return index['weight_map']
def layer_plan(layout_tsv, layer):
 import csv
 with open(layout_tsv) as f:return [r for r in csv.DictReader(f,delimiter='\t') if r['layer_id']==str(layer)]
