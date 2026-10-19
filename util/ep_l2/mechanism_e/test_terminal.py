"""Synthetic64slice parsing checks; never producer/independent native qualification."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
import coordinator as c
import parse_terminal as decoder
from headroom_config import options

class TerminalTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='ep_l2_ms_terminal_fixture_',dir='/workspace');self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);e=self.root/'not-native-evidence.txt';e.write_text('Synthetic decoder unit fixture only; not a scientific gate.')
        self.identity={'core_source_commit':'1'*40,'framework_source_commit':'2'*40,'binary_sha256':'3'*64,
         'feature_vector':{'payload_capacity_per_slice':1168,'wbuf_entries':16,'ops_per_bank_cycle':1,
           'static_s64':False,'wb_local_cap':0,'unified_wb':False},'ideal_vector':{},'termination_contract':{'full':True}}
        self.q={'campaign_id':c.CAMPAIGN,'qualified_by':'E','status':'INDEPENDENTLY_QUALIFIED',
          'source_identity':{n:self.identity[n] for n in ('core_source_commit','framework_source_commit','binary_sha256')},
          'affected_additional_gates':['local_diagnostic'],
          'gates':{n:{'status':'PASS','production_driven':True,'evidence_path':str(e),'evidence_sha256':c.digest(e)}
             for n in c.NATIVE_GATES|{'local_diagnostic'}}}
    @staticmethod
    def line(prefix,kind,row):
        return prefix+'|'+kind+'|'+'|'.join(k+'='+(','.join(map(str,v)) if isinstance(v,list) else str(v)) for k,v in row.items())+'\n'
    def fixture(self,profile='S',enabled=1,mutate=None):
        mode,cf,df=decoder.PROFILES[profile];identity=copy.deepcopy(self.identity);identity['feature_vector']['unified_wb']=mode==2
        config=Path('docs/ep_l2/review_packs/MS20261019_E_A_R1_SOURCE_INTAKE_r1/A_frozen_handoff/profiles')/(profile+'_observer'+str(enabled)+'.config')
        effective=options([config]);spec={'identity':identity,'profile':profile,'profile_semantics':{'effective_options':effective}}
        raw=['gpu_tot_sim_cycle = 100\n','gpu_tot_sim_insn = 10\n']
        for sid in range(64):
            s=dict(slice=sid,mode=mode,wbuf=16,physical_slots=1168,observed_cycles=100,
               role_free=1168,role_resident=0,role_bypass=0,wb_slots=0,ownership_consistent=1,
               reserved=0,read_refs=0,wb_live=0,wb_created=0,wb_lower_accept=0,wb_completed=0)
            t=dict(slice=sid,requester_exact_once=1,hardware_drained=1,unique_requesters=1,responses=1,
               pending_lower_reads=0,pending_returns=0,pending_responses=0)
            i=dict(slice=sid,kernel_uid=18446744073709551615,descriptor_used=0,line_mshr_used=0,wad_live=0,
               resident_pending=0,bypass_live=0,bank_pending=0,terminal_clean=1,resident_tag_payload_consistent=1,
               payload_double_owner=0,line_mshr_capacity=128,descriptor_capacity=512,descriptor_free=512,wad_capacity=128)
            o=dict(slice=sid,enabled=enabled,sampled_cycles=100 if enabled else 0,unfinished_head=0,
               head_changes_without_admission=0,lower_reads=2,lower_read_bytes=64,lower_writes=1,
               lower_write_bytes=32,lower_wb_bytes=0,unclassified_refusal_observations=0)
            d=dict(slice=sid,copy_free=cf,l2_data_free=df,logical_copy_reads=1,logical_copy_writes=1,
               physical_grants=0 if df else 2,hardware_P1_throughput_eligible=int(not(cf or df)))
            d.update({'exempt_'+n:int(cf or df) if n.startswith('copy') else int(df) for n in decoder.EXEMPT})
            if mutate:mutate(sid,s,t,i,o,d)
            raw += [self.line('EPL2FTV1','SUMMARY',s),self.line('EPL2FTV1','TERMINAL',t),self.line('EPL2B0V1','INVARIANT',i),
                    self.line('EPL2MSV1','OBSERVER',o),self.line('EPL2MSV1','LOCAL_DIAGNOSTIC',d)]
            if enabled:
                for reason in range(len(decoder.REASONS)):
                    w=dict(slice=sid,reason=reason,requests=0,observations=0,resolved=0,sum=0,max=0,
                       unknown_while_unresolved=0,hist_log2=[0]*65)
                    if sid==0 and reason==0:w.update(requests=1,observations=5,resolved=1,sum=4,max=4);w['hist_log2'][3]=1
                    raw.append(self.line('EPL2MSV1','WAIT',w))
            config=dict(slice=sid,static_s64=0,physical_slots=1168,resident_nominal=1024,bypass_capacity=128,
              wb_begin=1152,static_wb_capacity=16,legacy_wbuf=16,bank_count=4,bank_ops_per_physical_cycle=1,copy_latch_bytes=128)
            peak=dict(slice=sid,ops_per_physical_cycle=1,bank0=0 if df else 1,bank1=0,bank2=0,bank3=0)
            quota=dict(slice=sid,cap=0,reserved=0,live=0)
            raw += [self.line('EPL2STRUCTV1','CONFIG',config),self.line('EPL2STRUCTV1','BANK_PEAK',peak),self.line('EPL2STRUCTV1','WB_QUOTA',quota)]
        raw.append('GPGPU-Sim: *** exit detected ***\n');path=self.root/'raw.log';path.write_text(''.join(raw));return path,spec
    def test_all_five_initial_profiles_decode(self):
        for profile in decoder.PROFILES:
            path,spec=self.fixture(profile);summary=decoder.parse(path,spec,self.q)
            self.assertEqual(summary['cycles'],100);self.assertEqual(summary['instructions'],10)
            self.assertEqual(summary['live_descriptors'],0)
            self.assertEqual(summary['mechanism_metrics']['bottleneck']['WB_DATA_SPACE']['request_wait_cycle_sum'],4)
    def test_observer_disabled_missing_metrics_are_unknown(self):
        path,spec=self.fixture(enabled=0);summary=decoder.parse(path,spec,self.q)
        self.assertEqual(summary['mechanism_metrics']['bottleneck'],'UNKNOWN_OBSERVER_DISABLED')
        self.assertEqual(summary['mechanism_metrics']['local_service']['lower_read_bytes'],'UNKNOWN')
    def test_copy_free_does_not_exempt_downstream_read(self):
        def mutate(sid,s,t,i,o,d):
            if sid==0:d['exempt_lower_wb']=1
        path,spec=self.fixture('S_COPY_FREE',mutate=mutate)
        with self.assertRaisesRegex(ValueError,'noncopy'):decoder.parse(path,spec,self.q)
    def test_data_free_never_labels_logical_work_as_P1(self):
        def mutate(sid,s,t,i,o,d):
            if sid==0:d['hardware_P1_throughput_eligible']=1
        path,spec=self.fixture('U_L2_DATA_FREE',mutate=mutate)
        with self.assertRaisesRegex(ValueError,'mislabeled'):decoder.parse(path,spec,self.q)
    def test_bank_pending_cannot_be_hidden_by_exit(self):
        def mutate(sid,s,t,i,o,d):
            if sid==0:i['bank_pending']=1
        path,spec=self.fixture(mutate=mutate)
        with self.assertRaisesRegex(ValueError,'bank queue'):decoder.parse(path,spec,self.q)
    def test_different_descriptor_budget_rejected(self):
        def mutate(sid,s,t,i,o,d):
            if sid==0:i['descriptor_capacity']=1024
        path,spec=self.fixture(mutate=mutate)
        with self.assertRaisesRegex(ValueError,'capacity'):decoder.parse(path,spec,self.q)
    def test_missing64th_mechanism_slice_not_zero_filled(self):
        path,spec=self.fixture();path.write_text(''.join(line for line in path.read_text().splitlines(True)
          if not (line.startswith('EPL2MSV1|') and '|slice=63|' in line)))
        with self.assertRaisesRegex(ValueError,'exact64slice mechanism'):decoder.parse(path,spec,self.q)
    def test_data_qualification_not_inferred_from_performance(self):
        path,spec=self.fixture();self.q['gates']['sector_reference_data']['status']='FAIL'
        with self.assertRaisesRegex(ValueError,'production gate'):decoder.parse(path,spec,self.q)
    def test_cumulative_clock_mismatch_rejected(self):
        path,spec=self.fixture();path.write_text(path.read_text().replace('observed_cycles=100','observed_cycles=99',1))
        with self.assertRaisesRegex(ValueError,'final cumulative'):decoder.parse(path,spec,self.q)
    def test_negative_counter_not_hidden_in_slice_sum(self):
        path,spec=self.fixture();path.write_text(path.read_text().replace('lower_reads=2','lower_reads=-2',1))
        with self.assertRaisesRegex(ValueError,'negative source counter'):decoder.parse(path,spec,self.q)
    def test_A_r2_disabled_observer_marker_remains_unknown(self):
        path,spec=self.fixture(enabled=0)
        lines=[]
        for line in path.read_text().splitlines(True):
            if line.startswith('EPL2MSV1|OBSERVER|'):
                slice_id=line.split('|slice=')[1].split('|')[0]
                line='EPL2MSV1|OBSERVER|slice='+slice_id+'|enabled=0|measurement=DISABLED_NOT_OBSERVED\n'
            lines.append(line)
        path.write_text(''.join(lines));summary=decoder.parse(path,spec,self.q)
        self.assertEqual(summary['mechanism_metrics']['local_service']['lower_read_bytes'],'UNKNOWN')
        self.assertEqual(summary['mechanism_metrics']['bottleneck'],'UNKNOWN_OBSERVER_DISABLED')
    def test_repeat_snapshot_accepted_only_when_identical(self):
        path,spec=self.fixture();text=path.read_text();line=next(l for l in text.splitlines(True) if l.startswith('EPL2MSV1|LOCAL_DIAGNOSTIC|'))
        path.write_text(text+line);decoder.parse(path,spec,self.q)
        path.write_text(text+line.replace('physical_grants=2','physical_grants=3'))
        with self.assertRaisesRegex(ValueError,'conflicting mechanism snapshot'):decoder.parse(path,spec,self.q)

if __name__=='__main__':unittest.main()
