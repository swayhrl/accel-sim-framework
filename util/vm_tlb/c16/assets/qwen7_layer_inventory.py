#!/usr/bin/env python3
"""CPU-only safetensors metadata inventory and fail-closed layer resolver."""
from __future__ import annotations
import argparse,csv,hashlib,json,os,re,struct,sys,tempfile,unittest
from collections import defaultdict
from pathlib import Path
LAYER=re.compile(r"^model\.layers\.(\d+)\.(.+)$")
DTYPE_BYTES={"BOOL":1,"U8":1,"I8":1,"U16":2,"I16":2,"F16":2,"BF16":2,"F32":4,"U32":4,"I32":4,"F64":8,"U64":8,"I64":8,"F8_E4M3FN":1,"F8_E5M2":1}
class InventoryError(RuntimeError): pass
def no_duplicates(pairs):
 out={}
 for k,v in pairs:
  if k in out: raise InventoryError("duplicate JSON key: "+k)
  out[k]=v
 return out
def read_json(path):
 with open(path,encoding="utf-8") as f:return json.load(f,object_pairs_hook=no_duplicates)
def sha256(path):
 h=hashlib.sha256()
 with open(path,"rb") as f:
  for block in iter(lambda:f.read(1048576),b""):h.update(block)
 return h.hexdigest()
def safetensors_header(path):
 """Read only 8-byte length plus JSON header, never tensor payload data."""
 with open(path,"rb") as f:
  raw=f.read(8)
  if len(raw)!=8:raise InventoryError(f"short safetensors length prefix: {path}")
  length=struct.unpack("<Q",raw)[0]
  if length==0 or length>os.fstat(f.fileno()).st_size-8:raise InventoryError(f"invalid safetensors header length: {path}")
  return json.loads(f.read(length),object_pairs_hook=no_duplicates)
def tensor_role(name):
 hit=LAYER.match(name)
 if hit:
  layer,rest=int(hit.group(1)),hit.group(2)
  role="attention" if rest.startswith("self_attn.") else "MLP" if rest.startswith("mlp.") else "norm-other"
  return f"decoder layer {layer} {role}",layer,role,rest
 if name.startswith("model.embed_tokens."):return "embeddings",None,"embeddings",name
 if name.startswith("model.norm."):return "final norm",None,"final_norm",name
 if name.startswith("lm_head."):return "lm_head/output",None,"lm_head",name
 return "other",None,"other",name
def index_weight_map(index_path):
 weights=read_json(index_path).get("weight_map")
 if not isinstance(weights,dict) or not weights:raise InventoryError("missing/non-object weight_map")
 if any(not isinstance(k,str) or not isinstance(v,str) for k,v in weights.items()):raise InventoryError("non-string tensor/shard mapping")
 return weights
def inventory(model_dir):
 model_dir=Path(model_dir); mapping=index_weight_map(model_dir/"model.safetensors.index.json"); headers={};rows=[]
 for name,shard in sorted(mapping.items()):
  path=model_dir/shard
  if not path.is_file():raise InventoryError(f"missing indexed shard: {shard}")
  if shard not in headers:headers[shard]=safetensors_header(path)
  header=headers[shard];meta=header.get(name)
  if not isinstance(meta,dict):raise InventoryError(f"missing mapped tensor in safetensors header: {name}")
  dtype,shape,offsets=meta.get("dtype"),meta.get("shape"),meta.get("data_offsets")
  if dtype not in DTYPE_BYTES or not isinstance(shape,list) or not isinstance(offsets,list) or len(offsets)!=2:raise InventoryError(f"malformed tensor header metadata: {name}")
  numel=1
  for dim in shape:
   if not isinstance(dim,int) or dim<0:raise InventoryError(f"invalid shape: {name}")
   numel*=dim
  exact_bytes=offsets[1]-offsets[0]
  if exact_bytes<0 or exact_bytes!=numel*DTYPE_BYTES[dtype]:raise InventoryError(f"dtype/shape/offset byte mismatch: {name}")
  logical,layer,role,submodule=tensor_role(name)
  rows.append({"tensor_name":name,"logical_group":logical,"decoder_layer_id":"" if layer is None else layer,"submodule_role":role+(":"+submodule if layer is not None else ""),"source_shard":shard,"dtype":dtype,"shape":"x".join(map(str,shape)),"numel":numel,"exact_tensor_bytes":exact_bytes})
 return rows
FIELDS=["tensor_name","logical_group","decoder_layer_id","submodule_role","source_shard","source_shard_sha256_or_receipt_identity","dtype","shape","numel","exact_tensor_bytes"]
def write_tsv(path,fields,rows):
 with open(path,"w",newline="",encoding="utf-8") as f:
  w=csv.DictWriter(f,fieldnames=fields,delimiter="\t",lineterminator="\n",extrasaction="raise");w.writeheader();w.writerows(rows)
def residency(rows):
 groups=defaultdict(lambda:{"attention_bytes":0,"mlp_bytes":0,"norm_other_bytes":0,"shards":set()})
 for row in rows:
  if row["decoder_layer_id"]=="":continue
  b=groups[int(row["decoder_layer_id"])];role=row["submodule_role"].split(":",1)[0]
  b[{"attention":"attention_bytes","MLP":"mlp_bytes"}.get(role,"norm_other_bytes")]+=row["exact_tensor_bytes"];b["shards"].add(row["source_shard"])
 return [{"decoder_layer_id":i,"attention_bytes":b["attention_bytes"],"mlp_bytes":b["mlp_bytes"],"norm_other_bytes":b["norm_other_bytes"],"total_decoder_layer_bytes":b["attention_bytes"]+b["mlp_bytes"]+b["norm_other_bytes"],"source_shard_count":len(b["shards"]),"source_shards":";".join(sorted(b["shards"]))} for i,b in sorted(groups.items())]
def select_layer(model_dir,layer_id,validate_headers=True):
 model_dir=Path(model_dir);mapping=index_weight_map(model_dir/"model.safetensors.index.json");names=sorted(n for n in mapping if tensor_role(n)[1]==layer_id)
 if not names:raise InventoryError(f"requested decoder layer absent: {layer_id}")
 headers={};result=[]
 for name in names:
  shard=mapping[name]
  if shard not in headers:headers[shard]=safetensors_header(model_dir/shard)
  meta=headers[shard].get(name)
  if not isinstance(meta,dict):raise InventoryError(f"mapped tensor absent from selected shard header: {name}")
  dtype,shape,offsets=meta.get("dtype"),meta.get("shape"),meta.get("data_offsets")
  if dtype not in DTYPE_BYTES or not isinstance(shape,list) or not isinstance(offsets,list) or len(offsets)!=2:raise InventoryError(f"malformed selected tensor metadata: {name}")
  exact_bytes=offsets[1]-offsets[0]
  numel=1
  for dim in shape:
   if not isinstance(dim,int) or dim<0:raise InventoryError(f"invalid selected tensor shape: {name}")
   numel*=dim
  if exact_bytes<0 or exact_bytes!=numel*DTYPE_BYTES[dtype]:raise InventoryError(f"selected tensor dtype/shape/offset mismatch: {name}")
  result.append({"tensor_name":name,"source_shard":shard,"dtype":dtype,"shape":"x".join(map(str,shape)),"exact_tensor_bytes":exact_bytes})
 return {"decoder_layer_id":layer_id,"dry_run":True,"tensor_count":len(result),"source_shards":sorted(set(mapping[n] for n in names)),"total_selected_parameter_bytes":sum(t["exact_tensor_bytes"] for t in result),"tensors":result}
class HeaderTests(unittest.TestCase):
 def test_header_deterministic(self):
  with tempfile.TemporaryDirectory() as d:
   raw=b'{"x":{"dtype":"F16","shape":[2],"data_offsets":[0,4]}}';p=Path(d,"one.safetensors");p.write_bytes(struct.pack("<Q",len(raw))+raw+b"\0"*4);self.assertEqual(safetensors_header(p),safetensors_header(p))
 def test_duplicate_fails_closed(self):
  with self.assertRaises(InventoryError):json.loads('{"x":1,"x":2}',object_pairs_hook=no_duplicates)
 def test_missing_mapping_fails_closed(self):
  with tempfile.TemporaryDirectory() as d:
   Path(d,"model.safetensors.index.json").write_text('{"weight_map":{"model.layers.0.x":"missing.safetensors"}}')
   with self.assertRaises(InventoryError):inventory(d)
 def test_residency_deterministic_and_tying_unproven(self):
  rows=[{"decoder_layer_id":0,"submodule_role":"attention:x","exact_tensor_bytes":2,"source_shard":"a"},{"decoder_layer_id":0,"submodule_role":"MLP:x","exact_tensor_bytes":4,"source_shard":"a"},{"decoder_layer_id":0,"submodule_role":"norm-other:x","exact_tensor_bytes":1,"source_shard":"b"}]
  self.assertEqual(residency(rows)[0]["total_decoder_layer_bytes"],7);self.assertEqual("PROVEN_UNRESOLVED","PROVEN_UNRESOLVED")
def main():
 ap=argparse.ArgumentParser();sub=ap.add_subparsers(dest="command",required=True)
 inv=sub.add_parser("inventory");inv.add_argument("model_dir");inv.add_argument("--tsv",required=True);inv.add_argument("--receipt-identity",required=True)
 lay=sub.add_parser("layer");lay.add_argument("model_dir");lay.add_argument("--layer",type=int,required=True);lay.add_argument("--dry-run",action="store_true");lay.add_argument("--no-header-validate",action="store_true")
 sub.add_parser("test");args=ap.parse_args()
 if args.command=="test":return 0 if unittest.main(argv=[sys.argv[0]],exit=False).result.wasSuccessful() else 1
 if args.command=="inventory":write_tsv(args.tsv,FIELDS,[{**r,"source_shard_sha256_or_receipt_identity":args.receipt_identity} for r in inventory(args.model_dir)]);return 0
 if not args.dry_run:raise InventoryError("payload loading is intentionally not implemented in CPU-only helper; use --dry-run")
 print(json.dumps(select_layer(args.model_dir,args.layer,not args.no_header_validate),sort_keys=True,indent=2)+"\n");return 0
if __name__=="__main__":
 try:raise SystemExit(main())
 except InventoryError as e:print("FAIL_CLOSED: "+str(e),file=sys.stderr);raise SystemExit(2)
