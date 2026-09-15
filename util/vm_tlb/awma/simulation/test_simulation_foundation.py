#!/usr/bin/env python3
import hashlib,json,lzma,sys,tempfile,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent; sys.path.insert(0,str(HERE))
import simulation_foundation as s
def dig(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def fixture(root):
    (root/"k.traceg.xz").write_bytes(lzma.compress(b"record\n")); (root/"kernelslist.g").write_text("k.traceg.xz\n"); (root/"address.json").write_text("{}\n")
    m={"schema_version":s.SCHEMA_VERSION,"evidence_class":"SIM_COMPAT_CAPTURE_V1","workload_id":"W","target_id":"T","phase":"PREFILL","stream_context":"s0","grid":[1,1,1],"block":[32,1,1],"trace_schema":"SIM_COMPAT_CAPTURE_V1","producer_source_sha256":"a"*64,"producer_binary_sha256":"b"*64,"address_context_sidecar":"address.json","asid_epoch":"0","va_width":49,"page_policy":"4K","instruction_semantics":{x:"yes" for x in s.SEMANTICS},"terminal":{"status":"COMPLETE","drop_count":0,"overflow_count":0},"kernelslist":"kernelslist.g"}
    m["files"]={x:dig(root/x) for x in ("k.traceg.xz","kernelslist.g","address.json")}; p=root/"SIM_INPUT_MANIFEST.json"; p.write_text(json.dumps(m,sort_keys=True)); return p
class TestFoundation(unittest.TestCase):
 def test_ids(self):
  self.assertEqual(s.stable_id("X",{"a":1,"b":2}),s.stable_id("X",{"b":2,"a":1})); self.assertNotEqual(s.stable_id("X",{"a":1}),s.stable_id("X",{"a":2}))
 def test_admission_and_negative_contracts(self):
  with tempfile.TemporaryDirectory() as t:
   p=fixture(Path(t)); self.assertTrue(s.validate_bundle(p)["admitted"]); self.assertEqual(s.validate_bundle(p)["sim_input_id"],s.validate_bundle(p)["sim_input_id"])
   m=json.loads(p.read_text()); m["files"]["address.json"]="0"*64; p.write_text(json.dumps(m))
   with self.assertRaises(s.ContractError):s.validate_bundle(p)
   p=fixture(Path(t)); m=json.loads(p.read_text()); del m["instruction_semantics"]["byte_width"]; p.write_text(json.dumps(m))
   with self.assertRaises(s.ContractError):s.validate_bundle(p)
   p=fixture(Path(t)); m=json.loads(p.read_text()); del m["instruction_semantics"]["sync_control"]; p.write_text(json.dumps(m))
   with self.assertRaises(s.ContractError):s.validate_bundle(p)
   p=fixture(Path(t)); m=json.loads(p.read_text()); m["terminal"]["drop_count"]=1; p.write_text(json.dumps(m))
   with self.assertRaises(s.ContractError):s.validate_bundle(p)
 def test_c16_telemetry_catalog(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)/"m.json"; p.write_text(json.dumps({"evidence_class":"C16WARP1","simulator_eligibility":"NOT_PROVEN_LOSSLESS"})); self.assertIsNone(s.validate_bundle(p)["sim_input_id"])
   row={"metric_name":"tlb.l1.miss","metric_value":3,"unit":"count","evidence_origin":"HISTORICAL_RECORD","scientific_status":"FORMAL","claim_scope":"HISTORICAL_REFERENCE"}; self.assertEqual(len(s.normalize([row])),1)
   with self.assertRaises(s.ContractError):s.normalize([row,row])
   with self.assertRaises(s.ContractError):s.normalize([{**row,"metric_name":"unknown.x"}])
   r=Path(t)/"catalog"; self.assertEqual(s.catalog_put(r,"SIM_INPUTS",{"sim_input_id":"X","v":1})["result"],"CREATED"); self.assertEqual(s.catalog_put(r,"SIM_INPUTS",{"sim_input_id":"X","v":1})["result"],"NOOP_IDENTICAL")
   with self.assertRaises(s.ContractError):s.catalog_put(r,"SIM_INPUTS",{"sim_input_id":"X","v":2})
if __name__=="__main__":unittest.main(verbosity=2)
