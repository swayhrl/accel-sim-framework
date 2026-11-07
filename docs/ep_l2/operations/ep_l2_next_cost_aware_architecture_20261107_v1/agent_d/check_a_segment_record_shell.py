from pathlib import Path
import importlib.util,copy,json
O=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('a_shell',O/'a_segment_record_shell.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
tests=[]
def check(n,fn,reject=False):
 try:r=fn()
 except Exception as exc:
  if not reject:raise
  tests.append(dict(name=n,status='PASS_REJECT',reason=str(exc)));return
 if reject:raise AssertionError('accepted negative '+n)
 tests.append(dict(name=n,status='PASS'))
def fixture(mode):
 v=dict(slice=0,live=128,role_tvd=128 if mode!=2 else 256,mandatory=0,dirty_forward_responses=2,read_responses=10,served_sector_bytes=320,served_sectors=10)
 c=dict(slice=0,frontend_cam_ports=1,completion_cam_ports=1,directory_bound_wb_uid_bits=32,extra_packet_identity_bits=0,indexed_control_read_views=3,indexed_control_update_lanes=3,metadata_PPA='UNKNOWN',metadata_clock_closure='UNKNOWN')
 if mode==0:return v,c,None,None
 x=dict(slice=0,mode=mode,base_capacity=128,ext_capacity=128,base_live=128,ext_live=0 if mode==1 else 128,mandatory=0,ext_mandatory=0,spills=0 if mode==1 else 20,shared_query_ports=1,base_selector_cycles=2,indexed_ext_read_recheck_cycles=2,ext_write_ports=1,ext_indexed_read_views=1,base_reclaim_cycles=2,payload_slots=1168,bank_count=4,bank_ports=1,PPA='UNKNOWN')
 y=dict(slice=0,old_indexed_read_views=3,added_ext_indexed_read_views=1,old_update_lanes=3,added_ext_update_lanes=1,ext_read_responses=0 if mode==1 else 4,ext_served_sectors=0 if mode==1 else 4,ext_served_sector_bytes=0 if mode==1 else 128,ext_clean_installs=0 if mode==1 else 20,ext_reclaimed=0,ext_clean_slot_cycles=0 if mode==1 else 90,unexported_ext_waits='UNKNOWN')
 return v,c,x,y
for mode in [0,1,2]:
 vals=fixture(mode);check('CPU_fixture_mode'+str(mode)+'_cost_population_only',lambda vals=vals,mode=mode:m.validate_slice(*vals,mode))
for name,which,key,value in [('legacy_index3_not_total4',1,'indexed_control_read_views',4),('legacy_update3_not_total4',1,'indexed_control_update_lanes',4),('extra_CAM_gift',2,'shared_query_ports',2),('free_selector',2,'base_selector_cycles',0),('free_Ext_recheck',2,'indexed_ext_read_recheck_cycles',0),('payload_added',2,'payload_slots',1296),('Ext_overflow',2,'ext_live',129),('Base_global_population_fake',0,'role_tvd',128),('hidden_mandatory_Ext',2,'ext_mandatory',1),('wrong_added_read_views',3,'added_ext_indexed_read_views',2),('wrong_Ext_sectorbytes',3,'ext_served_sector_bytes',999),('unexported_waits_not_zero',3,'unexported_ext_waits',0)]:
 vals=list(copy.deepcopy(fixture(2)));vals[which][key]=value;check('reject_'+name,lambda vals=vals:m.validate_slice(*vals,2),True)
vals=list(copy.deepcopy(fixture(1)));vals[2]['ext_live']=1;vals[0]['role_tvd']=129;check('reject_disabled_mode1_used_Ext',lambda:m.validate_slice(*vals,1),True)
vals=fixture(2);check('mode0_must_have_no_extra_hardware',lambda:m.validate_slice(*vals,0),True)
check('unqualified_template_rejects_before_records',lambda:m.validate_final_frame([],2,dict(status='UNQUALIFIED_TEMPLATE')),True)
check('duplicate_field_parser',lambda:m.parse_line('EPL2TVDX1|CONTROL|slice=0|slice=1'),True)
check('negative_counter_parser',lambda:m.parse_line('EPL2TVDX1|CONTROL|slice=0|ext_read_responses=-1'),True)
out=dict(schema='NEXT_OPTIONAL_DIRECTORY_SOURCE_SPECIFIC_A_COST_SHELL_COUNTEREXAMPLES_V1',status='PASS_CPU_RECORD_FIXTURES_ONLY',count=len(tests),tests=tests,actual_new_source_or_producer_qualification=False,raw_Base_fields_never_rewritten=True,old_math_body_or_Host_NI_suite_rerun=False,new_scientific_starts=0)
(O/'A_RECORD_SHELL_CHECKS.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
print(json.dumps(dict(status=out['status'],count=len(tests))))
