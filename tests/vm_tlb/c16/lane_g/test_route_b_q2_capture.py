from __future__ import annotations
import json, sys, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]; sys.path.insert(0,str(ROOT/'util'/'vm_tlb'/'c16'/'lane_g'))
from route_b_q2_capture import validate_events
from route_b_memory_event_contract import WhitelistRow
from route_b_producer_q0 import whitelist_sha256

class Q2Capture(unittest.TestCase):
 def test_requires_exact_function_and_nonzero_address(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'raw.jsonl'; event={"record_kind":"LANE_EVENT","raw_schema":"C16_ROUTE_B_LANE_EVENT_V1","sequence_label":"OBSERVED_CALLBACK_ORDER","observed_event_sequence":0,"warp_instruction_instance_id":0,"kernel_launch_id":0,"function_mangled_name":"_Zx","deployment_id":"d","run_id":"r","scenario_id":"S0","phase":"PREFILL","decode_step":"ALL","cta":[0,0,0],"warp_id":0,"static_index":1,"instruction_offset":2,"opcode":"LDG.E","mref_ordinal":0,"access_kind":"READ","width_bytes":4,"memory_space":"GLOBAL","active_mask":1,"predicate_mask":1,"predicate_semantics":"GUARD_PREDICATE_MASK","executing_mask":1,"lane_id":0,"gpu_va":4096}; terminal={"record_kind":"TERMINAL","terminal_status":"COMPLETE","overflow_count":0,"drop_count":0,"event_count":1}; p.write_text(json.dumps(event)+'\n'+json.dumps(terminal)+'\n'); row={"static_index":1,"opcode":"LDG.E","memory_space":"GLOBAL","has_mref":True,"access_kind":"READ","width_bytes":4,"mref_ordinal":0,"mref_count":1}; producer={"schema_version":"C16_ROUTE_B_LANE_EVENT_PRODUCER_MANIFEST_V1","raw_schema":"C16_ROUTE_B_LANE_EVENT_V1","whitelist_sha256":whitelist_sha256((WhitelistRow(**row),)),"host_output_cap_bytes":10000,"whitelist":[row]}; self.assertEqual(1,validate_events(p,producer,"_Zx")["event_count"])

if __name__=='__main__': unittest.main()
