#!/usr/bin/env python3
from __future__ import annotations
import json, sys, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]; LANE=ROOT/'util'/'vm_tlb'/'c16'/'lane_g'; sys.path.insert(0,str(LANE))
from route_b_memory_event_contract import RouteBContractError
from route_b_q2_bridge import PREFILL_MANGLED, all_global_mref_rows, check_bridge, freeze_whitelist
HEADER="nvbit_static_index\tinstruction_offset\topcode\tmemory_space\tis_load\tis_store\thas_mref\tmref_count\twidth_bytes\tfunction_mangled_name\n"
class Q2Bridge(unittest.TestCase):
 def test_all_global_mrefs_and_ordinals_are_frozen(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d); m=p/'map.tsv'; c=p/'code'; c.write_bytes(b'x')
   m.write_text(HEADER+f"3\t24\tLDG.E.64\tGLOBAL\t1\t0\t1\t2\t8\t{PREFILL_MANGLED}\n"+f"4\t32\tSTG.E.32\tGLOBAL\t0\t1\t1\t1\t4\t{PREFILL_MANGLED}\n")
   out=freeze_whitelist(m,c,'PREFILL',p/'w.json',p/'w.tsv')
   self.assertEqual(3,out['whitelist_row_count']); self.assertEqual([(3,0),(3,1),(4,0)],[(x.static_index,x.mref_ordinal) for x in all_global_mref_rows(m,'PREFILL')])
 def test_missing_width_authority_and_missing_bridge_reference_fail(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d); m=p/'map.tsv'; m.write_text(HEADER.replace('\twidth_bytes','')+f"3\t24\tLDG\tGLOBAL\t1\t0\t1\t1\t{PREFILL_MANGLED}\n")
   with self.assertRaises(RouteBContractError): all_global_mref_rows(m,'PREFILL')
  with self.assertRaises(RouteBContractError): check_bridge([], {})
 def test_structure_compares_buckets_not_absolute_va(self):
  raw=[{'function_mangled_name':PREFILL_MANGLED,'static_index':101,'kernel_launch_id':1,'warp_instruction_instance_id':0,'lane_id':0,'gpu_va':0x1000},{'function_mangled_name':PREFILL_MANGLED,'static_index':101,'kernel_launch_id':1,'warp_instruction_instance_id':0,'lane_id':2,'gpu_va':0x1010}]
  ref={'schema_version':'C16_ROUTE_A_BRIDGE_REFERENCE_V1','exact_function_mangled_name':PREFILL_MANGLED,'selected_static_index':101,'bucket_shift':6,'selected_instance_lane_cardinalities':[2],'selected_address_bucket_cardinality':1}
  self.assertEqual('PASS_Q2_ROUTE_A_BRIDGE_STRUCTURE',check_bridge(raw,ref)['result'])
if __name__=='__main__': unittest.main()
