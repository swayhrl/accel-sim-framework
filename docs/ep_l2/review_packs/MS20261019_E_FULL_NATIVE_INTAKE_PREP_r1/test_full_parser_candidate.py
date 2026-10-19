"""Synthetic full-combination decoder checks; never native qualification."""
import sys
sys.path.insert(0,'/workspace/worktrees/accel-sim-ep-l2-ms20261019-e-eval-v1/util/ep_l2/mechanism_e')
import unittest
import json
from pathlib import Path
import policy_v2
import coordinator as c
import test_terminal as base
import parse_full_terminal as full


class FullParserTests(unittest.TestCase):
    setUp=base.TerminalTests.setUp
    line=staticmethod(base.TerminalTests.line)

    def fixture(self):
        def mutate(sid,s,t,i,o,d):s.update(role_free=1167,descriptor_responses=0)
        # Build the baseline synthetic schema only; no native executable exists.
        raw,spec=base.TerminalTests.fixture(self,'U',mutate=mutate)
        spec['profile']='F';switches=dict(W=1,V=1,T=1,M=1)
        spec['profile_semantics']['research_switches']=switches
        opts=spec['profile_semantics']['effective_options']
        opts.update({'-gpgpu_ep_l2_tvd_clean':'1','-gpgpu_ep_l2_tvd_dirty':'1','-gpgpu_ep_l2_tvd_fixed_entries':'0',
         '-gpgpu_ep_l2_ro_tag_detach':'1','-gpgpu_ep_l2_ro_line_mshr_bypass':'1',
         '-gpgpu_ep_l2_ro_manifest_sha256':'b'*64,'-gpgpu_ep_l2_ro_scope':'TRACE_MODEL_CLOSED_WORLD'})
        self.q['supported_profiles']={'F':{'research_switches':switches}}
        self.q['full_system_v2']={'authority_commit':policy_v2.AUTHORITY,'fixed_policy':True,
         'victim_scope':'CLEAN_DIRTY_PENDING_INFLIGHT','resource_budget':{'data_slots':1168,'line_bytes':128,
          'resident_tags':1024,'banks':4,'bank_ops':1,'descriptors':512,'line_mshrs':128,'shared_wad_tvd':128}}
        existing=next(iter(self.q['gates'].values()))
        self.q['gates'].update({name:dict(existing) for name in policy_v2.COMBINATION_GATES})
        lines=[]
        for sid in range(64):
            for reason in (15,16):
                lines.append(self.line('EPL2MSV2','WAIT',dict(slice=sid,reason=reason,requests=0,observations=0,resolved=0,
                 sum=0,max=0,unknown_while_unresolved=0,hist_log2=[0]*65)))
            lines.append(self.line('EPL2TVDV2','SUMMARY',dict(slice=sid,mandatory=0,live=1,role_tvd=1,
             served_sectors=0,served_sector_bytes=0,dirty_forward_responses=0,read_responses=0)))
            lines.append(self.line('EPL2TVDV3','METADATA_COST',dict(slice=sid,frontend_cam_ports=1,completion_cam_ports=1,
             directory_bound_wb_uid_bits=32,extra_packet_identity_bits=0,indexed_control_read_views=3,indexed_control_update_lanes=3,
             metadata_PPA='UNKNOWN',metadata_clock_closure='UNKNOWN')))
            lines.append(self.line('EPL2ROV1','SUMMARY',dict(slice=sid,detach=1,bypass=1,manifest='b'*64,scope='TRACE_MODEL_CLOSED_WORLD',
             live=0,responses=0,accepted_ro=0,transactions=0,merges=0,accepted_oracle_candidates=0,accepted_global_reads=2,
             lower_sectors=0,concurrent_duplicate_sectors=0)))
            lines.append(self.line('EPL2ROC1','CLOSURE',dict(slice=sid,ro_live=0,shared_descriptor_used=0,shared_line_used=0,epoch_closed=1,
             ro_descriptor_responses=0,native_descriptor_responses=0,scope='NATIVE_AND_RO_DISTINCT_SUBCOUNTERS_NOT_ALL_FRONTEND_REQUESTS')))
            lines.append(self.line('EPL2ROC1','RESOURCE',dict(slice=sid,oracle='TRACE_MODEL_CLOSED_WORLD',shared_descriptor_capacity=512,
             payload_capacity=1168,line_capacity=128,query_ports_per_slice=1,query_latency_gpu_cycles=1,
             peak_shared_descriptors=0,peak_shared_lines=0,peak_transactions=0,lower_read_bytes=0,concurrent_duplicate_read_bytes=0)))
            lines.append(self.line('EPL2ROC1','LOWER_CONCURRENCY',dict(slice=sid,completed_ro_requesters=0,
             epoch_begin_gpu_cycle=1,epoch_end_gpu_cycle=100,last_response_gpu_cycle='NA',scope='RO_ISSUED_NOT_RETURNED_PER_SLICE',
             measurement='OBSERVER_ONLY_NO_ADMISSION_LOOKUP')))
            for reason in ('TAG_SET_ALL_PENDING','LINE_MSHR_FULL','SHARED_DESCRIPTOR_FULL','PER_ADDRESS_FULL'):
                lines.append(self.line('EPL2ROC1','WAIT',dict(slice=sid,reason=reason,pending_head=0,hist_log2=[0]*16,
                 unique_head_requests=0,scope='SLICE_FRONTEND_HEAD_NONEXCLUSIVE_WAIT')))
        raw.write_text(raw.read_text()+''.join(lines));return raw,spec

    def test_retained_clean_victim_counted_as_valid_not_transient(self):
        raw,spec=self.fixture();result=full.parse(raw,spec,self.q)
        self.assertEqual(result['payload_roles']['TVD_VALID'],64)
        self.assertEqual(result['transient_payloads'],0)
        self.assertEqual(result['unique_requesters'],result['responses'])

    def test_no_missing_slice_imputed_as_zero(self):
        raw,spec=self.fixture();raw.write_text(''.join(line for line in raw.read_text().splitlines(True)
            if not line.startswith('EPL2ROC1|RESOURCE|slice=63|')))
        with self.assertRaisesRegex(ValueError,'exact64slice TVD/RO'):full.parse(raw,spec,self.q)

    def test_wrong_manifest_cannot_be_reused(self):
        raw,spec=self.fixture();raw.write_text(raw.read_text().replace('manifest='+'b'*64,'manifest='+'c'*64,1))
        with self.assertRaisesRegex(ValueError,'oracle scope/hash'):full.parse(raw,spec,self.q)

    def test_live_ro_cannot_hide_in_resident_budget(self):
        raw,spec=self.fixture();raw.write_text(raw.read_text().replace('ro_live=0','ro_live=1',1))
        with self.assertRaisesRegex(ValueError,'not drained'):full.parse(raw,spec,self.q)

    def test_new_reason_namespace_cannot_reinterpret_old14(self):
        raw,spec=self.fixture();raw.write_text(raw.read_text().replace('EPL2MSV1|WAIT|slice=0|reason=14|','EPL2MSV2|WAIT|slice=0|reason=14|',1))
        with self.assertRaisesRegex(ValueError,'reason namespace'):full.parse(raw,spec,self.q)


if __name__=='__main__':unittest.main()
