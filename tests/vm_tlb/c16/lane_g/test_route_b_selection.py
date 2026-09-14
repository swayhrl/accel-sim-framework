#!/usr/bin/env python3
"""CPU fixtures for V2 full-census Route-B selection."""
from __future__ import annotations
import sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]; sys.path.insert(0,str(ROOT/'util'/'vm_tlb'/'c16'/'lane_g'))
from route_b_selection import RouteBSelectionError, freeze_final_selection_v2, normalize_active_map_results_v2
SHA="a"*64
def req(i,duration,launch=1,grid="1x1x1"):
 return {"request_id":i,"exact_full_function":"f"+i,"known_mangled_name":"MAP_DISCOVERY_REQUIRED","code_object_sha256":"MAP_DISCOVERY_REQUIRED","source_catalog_sha":SHA,"phase_observations":{"PREFILL":{"launch_count":launch,"phase_duration_ns":duration,"geometries":[{"grid":grid,"block":"32x1x1","shape_key":"S","dtype_key":"D","launch_count":launch,"duration_ns":duration}]}}}
def mapped(row,count):
 return {"request_id":row["request_id"],"terminal_status":"MAPPED_EXACT","exact_full_function":row["exact_full_function"],"function_mangled_name":"_Z"+row["request_id"],"static_global_mref_count":count,"static_map_sha256":SHA,"code_object_sha256":SHA}
class V2Selection(unittest.TestCase):
 def test_real_duration_prefix_and_geometry_proxy(self):
  a,b,c=req("a",70,1),req("b",20,100),req("c",10,1)
  out=freeze_final_selection_v2({"schema_version":"C16_ROUTE_B_MAP_REQUESTS_V2","requests":[a,b,c]},[mapped(a,1),mapped(b,1),mapped(c,1)])
  phase=out["phases"]["PREFILL"]
  self.assertEqual(["a"],phase["duration_prefix_request_ids"])
  self.assertEqual(["b"],phase["memory_proxy_prefix_request_ids"])
  self.assertEqual(.7,phase["duration_prefix_coverage"])
  self.assertGreaterEqual(phase["memory_proxy_coverage"],.8)
 def test_failed_map_keeps_full_duration_denominator_and_is_not_runnable(self):
  a,b=req("a",60),req("b",40)
  out=freeze_final_selection_v2({"schema_version":"C16_ROUTE_B_MAP_REQUESTS_V2","requests":[a,b]},[mapped(a,1),{"request_id":"b","terminal_status":"FAILED_CLOSED","exact_full_function":"fb","failure_reason":"owner unresolved"}])
  phase=out["phases"]["PREFILL"]
  self.assertEqual(100,phase["full_frozen_duration_denominator_ns"])
  self.assertEqual("NOT_PROVABLE_FAILED_CLOSED",phase["memory_proxy_coverage_status"])
  self.assertEqual(["a","b"],phase["duration_prefix_request_ids"])
  self.assertEqual(["b"],phase["required_duration_failed_closed_request_ids"])
  self.assertEqual([],phase["final_request_ids"])
  self.assertEqual("SELECTION_NOT_ADMISSIBLE_DUE_TO_FAILED_CLOSED_COVERAGE",out["status"])
  self.assertEqual([],out["final_request_ids"])
 def test_active_evidence_normalization_is_explicit_and_closed(self):
  active={"schema_version":"C16_ROUTE_B_MAP_RESULTS_V2_V2","results":[
   {"request_id":"a","status":"MAPPED_EXACT","exact_full_function":"fa","full_mangled_function":"_Za","global_mref_count":2,"static_map_sha256":SHA,"actual_owning_code_object_sha256":SHA},
   {"request_id":"b","status":"FAILED_CLOSED","exact_full_function":"fb","failure_reason":"owner unresolved"}]}
  rows=normalize_active_map_results_v2(active)
  self.assertEqual("_Za",rows[0]["function_mangled_name"])
  self.assertEqual(2,rows[0]["static_global_mref_count"])
  self.assertEqual("FAILED_CLOSED",rows[1]["terminal_status"])
 def test_legacy_geometry_is_not_promoted_to_proxy_evidence(self):
  a,b=req("a",60),req("b",40)
  del a["phase_observations"]["PREFILL"]["geometries"][0]["launch_count"]
  del a["phase_observations"]["PREFILL"]["geometries"][0]["duration_ns"]
  out=freeze_final_selection_v2({"schema_version":"C16_ROUTE_B_MAP_REQUESTS_V2","requests":[a,b]},[mapped(a,1),{"request_id":"b","terminal_status":"FAILED_CLOSED","exact_full_function":"fb","failure_reason":"owner unresolved"}])
  self.assertEqual(["a"],out["phases"]["PREFILL"]["geometry_observations_incomplete_request_ids"])
  self.assertEqual([],out["final_request_ids"])
 def test_unresolved_or_address_result_is_rejected(self):
  a=req("a",1)
  with self.assertRaises(RouteBSelectionError): freeze_final_selection_v2({"schema_version":"C16_ROUTE_B_MAP_REQUESTS_V2","requests":[a]},[])
  with self.assertRaises(RouteBSelectionError): freeze_final_selection_v2({"schema_version":"C16_ROUTE_B_MAP_REQUESTS_V2","requests":[a]},[mapped(a,1)|{"gpu_va":1}])
if __name__=='__main__': unittest.main()
