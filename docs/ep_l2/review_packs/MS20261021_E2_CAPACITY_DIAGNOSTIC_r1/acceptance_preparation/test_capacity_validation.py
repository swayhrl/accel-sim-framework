"""Bounded synthetic controls, NOT native/scientific qualification."""
import copy,unittest
from capacity_validation import validate_summary,AUTHORITY,SLICE_ZERO,LEGACY_MAIN61

def example(master=1):
    # Synthetic capacities only; these are NOT the A2-frozen real vector.
    b={'tag_slots':1024,'resident_payload_slots':1024,'bypass_payload_slots':128,'wb_payload_slots':16,'payload_slots_total':1168,'wad_entries':128,'line_mshr_entries':128,'descriptor_entries':512,'per_address_descriptors':32,'miss_queue_entries':128}
    scale=64 if master else 1;caps={k:v*scale for k,v in b.items()};drain=['wad_entries','line_mshr_entries','descriptor_entries','per_address_descriptors','miss_queue_entries','wb_payload_slots']
    config={'native_tag_sets':64*scale,'native_tag_ways':16,'native_line_bytes':128,'copy_latch_bytes':128,'ft_mode':1,'W':0,'V':0,'T':0,'M':0,'mq2':0,'rg1':0,'copy_free':0,'l2_data_free':master,'hardware_P1_throughput_eligible':1-master,'bank_count':4,'bank_ops_per_physical_cycle':1}
    source={'core_source_commit':'1'*40,'framework_source_commit':'2'*40,'binary_sha256':'3'*64}
    i={**source,'feature_vector':{'payload_capacity_per_slice':caps['payload_slots_total'],'wbuf_entries':caps['wb_payload_slots']},'termination_contract':{'scope':'full_application'}}
    profile='S_CAPACITY_ON' if master else 'S_CAPACITY_OFF'
    q={'schema':'E2_CAPACITY_VALIDATION_SCOPE_V1','authority_commit':AUTHORITY,'source_identity':source,'capacity_manifest_sha256':'4'*64,'expected_full_instructions':1000,'termination_contract':i['termination_contract'],'profiles':{profile:{'master':master,'capacities':caps,'configuration':config,'enlarged_resources':list(caps) if master else [],'drained_resources':drain}}}
    records={}
    for sid in range(64):
        c={**{k:0 for k in SLICE_ZERO},'hardware_drained':1,'requester_exact_once':1,'ownership_consistent':1,'resident_tag_payload_consistent':1,'payload_double_owner':0,'descriptor_free':caps['descriptor_entries'],'unique_requesters':10,'responses':10,'wb_created':2,'wb_lower_accepted':2,'wb_completed':2,'payload_roles':{'RESIDENT_OR_FILL':10,'BYPASS':0,'WB_STAGED':0},'payload_free':caps['payload_slots_total']-10}
        records[str(sid)]={'observed_cycles':100,'configuration':copy.deepcopy(config),'closure':c,'resources':{k:{'capacity':v,'highwater':v//4,'capacity_refusals':0,'counter_covered':True,'full_input_scope':True,'terminal_used':0 if k in drain else 10} for k,v in caps.items()},'local_service':{'physical_grants':0 if master else 20,'logical_copy_reads':2,'logical_copy_writes':2,'exempt_services':{k:(2 if master and k in ('copy_read','copy_write') else 0) for k in ('response','fill','lower_wb','frontend','copy_read','copy_write')}}}
    s={'diagnostic_scope':'CAPACITY_DIAGNOSTIC_V1','profile':profile,'cycles':100,'instructions':1000,'slices':64,'hardware_drained':True,'workload_termination':i['termination_contract'],'requester_exact_once_audit':True,'data_correctness_qualification':True,'live_descriptors':0,'live_line_mshrs':0,'live_wad':0,'pending_lower_reads':0,'pending_returns':0,'pending_responses':0,'transient_payloads':0,'unique_requesters':640,'responses':640,'wb_created':128,'wb_lower_accepted':128,'wb_completed':128,'payload_capacity':caps['payload_slots_total']*64,'payload_free':(caps['payload_slots_total']-10)*64,'payload_roles':{'RESIDENT_OR_FILL':640,'BYPASS':0,'WB_STAGED':0},'capacity_diagnostic':{'schema':'E2_CAPACITY_NORMALIZED_TERMINAL_V1','requested_master':master,'effective_master':master,'capacity_manifest_sha256':q['capacity_manifest_sha256'],'complete_input_scope':True,'slices':records}}
    return s,i,q

class Controls(unittest.TestCase):
    def test_on(self):self.assertTrue(validate_summary(*example())['capacity_classification']['near_unbounded'])
    def test_off(self):self.assertEqual(validate_summary(*example(0))['capacity_classification']['label'],'FINITE_OFF_BASELINE')
    def test_refusal_valid_negative(self):
        s,i,q=example();s['capacity_diagnostic']['slices']['0']['resources']['wad_entries']['capacity_refusals']=1
        v=validate_summary(s,i,q);self.assertEqual(v['status'],'PASS');self.assertEqual(v['capacity_classification']['label'],'LARGE_FINITE')
    def test_exact_half_boundary(self):
        s,i,q=example();r=s['capacity_diagnostic']['slices']['0']['resources']['wad_entries'];r['highwater']=r['capacity']//2
        self.assertTrue(validate_summary(s,i,q)['capacity_classification']['near_unbounded']);r['highwater']+=1
        self.assertEqual(validate_summary(s,i,q)['capacity_classification']['label'],'LARGE_FINITE')
    def test_missing_counter_unknown(self):
        s,i,q=example();r=s['capacity_diagnostic']['slices']['1']['resources']['tag_slots'];r['counter_covered']=False;r['highwater']=None
        self.assertEqual(validate_summary(s,i,q)['capacity_classification']['label'],'UNKNOWN')
    def test_known_binding_unknown_other(self):
        s,i,q=example();r=s['capacity_diagnostic']['slices'];r['0']['resources']['tag_slots']['counter_covered']=False;r['1']['resources']['tag_slots']['capacity_refusals']=1
        self.assertEqual(validate_summary(s,i,q)['capacity_classification']['label'],'LARGE_FINITE')
    def test_missing_slice(self):
        s,i,q=example();del s['capacity_diagnostic']['slices']['63']
        with self.assertRaises(ValueError):validate_summary(s,i,q)
    def test_capacity_mismatch(self):
        s,i,q=example();s['capacity_diagnostic']['slices']['2']['resources']['descriptor_entries']['capacity']+=1
        with self.assertRaises(ValueError):validate_summary(s,i,q)
    def test_not_drained(self):
        s,i,q=example();s['capacity_diagnostic']['slices']['3']['closure']['wad_live']=1
        with self.assertRaises(ValueError):validate_summary(s,i,q)
    def test_old_binary(self):
        s,i,q=example();i['binary_sha256']=LEGACY_MAIN61;q['source_identity']['binary_sha256']=LEGACY_MAIN61
        with self.assertRaises(ValueError):validate_summary(s,i,q)
    def test_wrong_full_instructions(self):
        s,i,q=example();s['instructions']-=1
        with self.assertRaises(ValueError):validate_summary(s,i,q)
    def test_wrong_geometry(self):
        s,i,q=example();s['capacity_diagnostic']['slices']['0']['configuration']['native_tag_sets']+=1
        with self.assertRaises(ValueError):validate_summary(s,i,q)
    def test_on_physical_grants(self):
        s,i,q=example();s['capacity_diagnostic']['slices']['0']['local_service']['physical_grants']=1
        with self.assertRaises(ValueError):validate_summary(s,i,q)
    def test_off_exemptions(self):
        s,i,q=example(0);s['capacity_diagnostic']['slices']['0']['local_service']['exempt_services']['copy_read']=1
        with self.assertRaises(ValueError):validate_summary(s,i,q)
    def test_hwm_over_bound(self):
        s,i,q=example();r=s['capacity_diagnostic']['slices']['0']['resources']['wad_entries'];r['highwater']=r['capacity']+1
        with self.assertRaises(ValueError):validate_summary(s,i,q)

if __name__=='__main__':unittest.main()
