"""Reuse the old strict closure validator; test new pair and version boundaries."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import test_coordinator as fixtures
import coordinator as c
import runner
from validate import validate_summary,InvalidEvidence

# Reuse fixture setup without inheriting its test methods.
class IntakeTests(unittest.TestCase):
    setUp=fixtures.ControlTests.setUp
    save=fixtures.ControlTests.save
    read=fixtures.ControlTests.read
    def summary(self):
        return {'cycles':100,'instructions':10,'slices':64,'unique_requesters':3,'responses':3,
         'live_descriptors':0,'live_line_mshrs':0,'live_wad':0,'pending_lower_reads':0,
         'pending_returns':0,'pending_responses':0,'transient_payloads':0,'wb_created':1,
         'wb_lower_accepted':1,'wb_completed':1,'payload_capacity':1168*64,'payload_free':1168*64,
         'payload_roles':{'RESIDENT_OR_FILL':0},'hardware_drained':True,
         'workload_termination':self.identity['termination_contract'],
         'requester_exact_once_audit':True,'data_correctness_qualification':True}
    def test_reuse_real64slice_summary_validator(self):
        self.identity['feature_vector']['payload_capacity_per_slice']=1168
        self.assertEqual(validate_summary(self.summary(),self.identity)['status'],'PASS')
    def test_missing_not_zero(self):
        summary=self.summary();summary.pop('live_descriptors')
        with self.assertRaisesRegex(InvalidEvidence,'missing explicit'):validate_summary(summary,self.identity)
    def test_nonzero_live_resource_rejected(self):
        summary=self.summary();summary['live_descriptors']=1
        with self.assertRaisesRegex(InvalidEvidence,'nonempty terminal'):validate_summary(summary,self.identity)
    def test_data_correctness_not_inferred_from_cycles(self):
        summary=self.summary();summary['data_correctness_qualification']=False
        self.identity['feature_vector']['payload_capacity_per_slice']=1168
        with self.assertRaisesRegex(InvalidEvidence,'data correctness'):validate_summary(summary,self.identity)
    def test_63slices_rejected(self):
        summary=self.summary();summary['slices']=63
        with self.assertRaisesRegex(InvalidEvidence,'64 slices'):validate_summary(summary,self.identity)
    def test_wb_completion_required(self):
        summary=self.summary();summary['wb_completed']=0
        with self.assertRaisesRegex(InvalidEvidence,'WB terminal'):validate_summary(summary,self.identity)
    def endpoints(self):
        for i,profile in enumerate(('S','U')):
            record={'attempt_id':str(i),'run_key':str(i),'identity':self.identity,'profile':profile,
              'source_identity':{'binary_sha256':self.identity['binary_sha256'],'core_source_commit':'1'*40,
                 'framework_source_commit':'2'*40,'vendor_pybind11_commit':'3'*40},
              'selection_id':'fixture','comparison_group':'g','comparison_invariants_sha256':'same',
              'qualification_id':'q','complete_input_verified':True,'status':'COMPLETE_VALID','independent_acceptance':'PASS',
              'summary':{'cycles':100+i,'instructions':10}}
            path=self.root/f'endpoint{i}.json';path.write_text(json.dumps(record))
            self.ledger['accepted_results'][str(i)]={'path':str(path),'sha256':c.digest(path),
               'run_key':str(i),'identity':self.identity}
        (self.root/c.FIELD/'events').mkdir();self.save()
    def change_endpoint(self,field,value):
        e=self.ledger['accepted_results']['1'];p=Path(e['path']);r=json.loads(p.read_text());r[field]=value
        p.write_text(json.dumps(r));e['sha256']=c.digest(p);self.save()
    def test_complete_pair_immediately_produces_D_event(self):
        self.endpoints();row=runner.accept_pair(self.coord,'0','1','p')
        self.assertEqual(row['ratio_left_over_right'],100/101)
        self.assertTrue((self.root/c.FIELD/'events/E_TO_D_PAIR_p.json').is_file())
        self.assertEqual(self.coord.snapshot()['actual_starts'],0)
    def test_current_D_parser_accepts_new_E_pair_schema(self):
        # Read D's published consumer only; do not edit its files or real results.
        import importlib.util
        source=Path('/workspace/worktrees/accel-sim-ep-l2-ms20261019-d-analysis-v1/util/ep_l2/mechanism_study_lane_d/sync_intake.py')
        module_spec=importlib.util.spec_from_file_location('D_published_consumer',source)
        consumer=importlib.util.module_from_spec(module_spec);module_spec.loader.exec_module(consumer)
        self.endpoints();declaration=runner.accept_pair(self.coord,'0','1','p','W')
        row=consumer.analyze_pair('p',declaration,self.coord.snapshot()['accepted_results'])
        self.assertEqual(row['status'],'E_ACCEPTED_D_ANALYZED')
        self.assertEqual(row['cycles_baseline_minus_variant'],-1)
        self.assertEqual(row['trigger'],'UNKNOWN')
    def test_cross_binary_pair_rejected(self):
        self.endpoints();self.change_endpoint('source_identity',{'binary_sha256':'other'})
        with self.assertRaisesRegex(ValueError,'source_identity'):runner.accept_pair(self.coord,'0','1','p')
    def test_nonresearch_option_mismatch_rejected(self):
        self.endpoints();self.change_endpoint('comparison_invariants_sha256','different')
        with self.assertRaisesRegex(ValueError,'comparison_invariants'):runner.accept_pair(self.coord,'0','1','p')
    def test_missing_pair_never_imputed(self):
        self.endpoints();self.ledger['accepted_results'].pop('1');self.save()
        with self.assertRaises(KeyError):runner.accept_pair(self.coord,'0','1','p')
    def test_withdrawn_changed_qualification_rejected(self):
        self.endpoints();Path(self.ledger['qualifications']['q']['path']).write_text('{}')
        with self.assertRaisesRegex(ValueError,'withdrawn/changed'):runner.accept_pair(self.coord,'0','1','p')
    def test_raw_acceptance_receipt_mutation_rejected(self):
        self.endpoints();Path(self.ledger['accepted_results']['1']['path']).write_text('{}')
        with self.assertRaisesRegex(ValueError,'endpoint changed'):runner.accept_pair(self.coord,'0','1','p')
    def test_pair_published_only_once(self):
        self.endpoints();runner.accept_pair(self.coord,'0','1','p')
        with self.assertRaisesRegex(ValueError,'already published'):runner.accept_pair(self.coord,'0','1','p')
    def test_native_dump_and_terminal_are_checked(self):
        path=self.root/'raw.log';path.write_text('-gpgpu_ep_l2_diag_copy_free 0\ngpu_tot_sim_cycle = 100\ngpu_tot_sim_insn = 10\nGPGPU-Sim: *** exit detected ***\n')
        self.assertEqual(runner.runtime_metrics(path,{'-gpgpu_ep_l2_diag_copy_free':'0'}),{'cycle':100,'insn':10})
    def test_wrong_effective_diagnostic_rejected(self):
        path=self.root/'raw.log';path.write_text('-gpgpu_ep_l2_diag_copy_free 1\ngpu_tot_sim_cycle = 100\ngpu_tot_sim_insn = 10\nGPGPU-Sim: *** exit detected ***\n')
        with self.assertRaisesRegex(ValueError,'effective native L2'):runner.runtime_metrics(path,{'-gpgpu_ep_l2_diag_copy_free':'0'})
    def test_exit_without_native_counters_rejected(self):
        path=self.root/'raw.log';path.write_text('GPGPU-Sim: *** exit detected ***\n')
        with self.assertRaisesRegex(ValueError,'native exit/counters'):runner.runtime_metrics(path,{'-gpgpu_ep_l2_diag_copy_free':'0'})
    def qualification_fixture(self):
        evidence=self.root/'native-fixture.json';evidence.write_text('{"fixture":"control test only, not native production evidence"}')
        bound={'path':str(evidence),'sha256':c.digest(evidence)}
        source={k:self.identity[k] for k in ('core_source_commit','framework_source_commit','binary_sha256')}
        source['vendor_pybind11_commit']='3'*40
        q={'campaign_id':c.CAMPAIGN,'qualified_by':'E','status':'INDEPENDENTLY_QUALIFIED',
          'source_identity':source,'binary_path':str(self.bin),'affected_additional_gates':['diagnostic_effect'],
          'gates':{n:{'status':'PASS','production_driven':True,'evidence_path':str(evidence),
                    'evidence_sha256':c.digest(evidence)} for n in c.NATIVE_GATES|{'diagnostic_effect'}},
          'supported_profiles':{'S':{'control_fixture_only':True}},'producer_release':{
             'publication_commit':'a'*40,'source_identity':source,**bound},'build_log':bound,'producer_test_manifest':bound,
          'scope_note':'control fixture; no real qualification','default_off_equivalence':True}
        path=self.root/'new-q-fixture.json';path.write_text(json.dumps(q));return q,path
    def test_new_qualification_requires_all11_and_affected_evidence(self):
        q,path=self.qualification_fixture();qid=self.coord.register_qualification(path)
        self.assertEqual(qid,c.digest(path));self.assertIn(qid,self.coord.snapshot()['qualifications'])
        self.assertEqual(self.coord.snapshot()['actual_starts'],0)
    def test_failed_affected_gate_blocks_qualification(self):
        q,path=self.qualification_fixture();q['gates']['diagnostic_effect']['status']='FAIL';path.write_text(json.dumps(q))
        with self.assertRaisesRegex(ValueError,'failed/missing gate'):self.coord.register_qualification(path)
    def test_control_head_not_usable_as_runtime_framework(self):
        q,path=self.qualification_fixture();q['source_identity']['framework_source_commit']=c.AUTHORITY
        q['producer_release']['source_identity']=q['source_identity'];path.write_text(json.dumps(q))
        with self.assertRaisesRegex(ValueError,'control HEAD'):self.coord.register_qualification(path)
    def test_failure_hold_blocks_new_pair_and_informs_D(self):
        self.endpoints();runner.accept_pair(self.coord,'0','1','p','W')
        self.coord.place_scientific_hold('q','failed','fixture actual terminal violation','fixture-evidence-path')
        item=self.coord.snapshot();self.assertEqual(item['accepted_pairs']['p']['status'],'WITHDRAWN_SCIENTIFIC_HOLD')
        self.assertEqual(len(item['pair_status_history']),1)
        self.assertEqual(len(item['accepted_results']),2) # immutable raw pointers retained
        with self.assertRaisesRegex(ValueError,'scientific review hold'):runner.accept_pair(self.coord,'0','1','p2','W')
        self.assertTrue((self.root/c.FIELD/'events/E_TO_D_PAIR_p_HOLD.json').exists())
    def test_hold_stops_only_named_qualification(self):
        self.endpoints();self.coord.place_scientific_hold('q','failed','fixture terminal violation','fixture-evidence')
        with self.assertRaisesRegex(ValueError,'scientific review hold'):self.coord.reserve_application(self.spec)
        c.Coordinator.require_no_hold(self.coord.snapshot(),'independent_other_qualified_version')
        self.assertEqual(self.coord.snapshot()['actual_starts'],0)
    def test_clear_hold_requires_current_evidence_and_does_not_restore_old_pair(self):
        self.endpoints();runner.accept_pair(self.coord,'0','1','p','W')
        hold=self.coord.place_scientific_hold('q','failed','fixture parser review','fixture-evidence')
        e=Path(self.ledger['qualifications']['q']['path']);review={
          'reviewed_by':'E','qualification_id':'q','status':'RESOLVED_WITH_EXPLICIT_EVIDENCE',
          'hold_at_unix':hold['at_unix'],'reason':'fixture engineering correction independently reviewed',
          'evidence':[{'path':str(e),'sha256':c.digest(e)}]}
        path=self.root/'resolution.json';path.write_text(json.dumps(review));self.coord.resolve_scientific_hold('q',path)
        self.assertFalse(self.coord.snapshot()['scientific_holds'])
        self.assertEqual(self.coord.snapshot()['accepted_pairs']['p']['status'],'WITHDRAWN_SCIENTIFIC_HOLD')
        self.assertEqual(self.coord.snapshot()['actual_starts'],0)
    def test_controller_does_not_rehash_or_execute_held_ready_spec(self):
        import controller
        self.endpoints();self.coord.place_scientific_hold('q','failed','fixture terminal hold','fixture-evidence')
        path=self.root/'spec.json';path.write_text(json.dumps(self.spec))
        queue={'campaign_id':c.CAMPAIGN,'prepared_by':'E','authority_commit':c.AUTHORITY,
               'input_and_profile_freeze_unix':1792410000,'specs':[{'path':str(path),'sha256':c.digest(path)}],'pairs':[]}
        qp=self.root/'queue.json';qp.write_text(json.dumps(queue))
        with patch.object(controller,'execute') as execute:
            result=controller.step(self.coord,qp);execute.assert_not_called()
        self.assertEqual(result['status'],'SCOPED_HOLDS_PENDING')
        self.assertEqual(result['held_run_keys'],[c.run_key(self.identity)])
        self.assertEqual(result['applications_started_by_this_step'],0)
    def test_no_inherited_old_release_qualification(self):
        q={'campaign_id':'OLD_LANE5','qualified_by':'lane5','status':'INDEPENDENTLY_QUALIFIED'}
        path=self.root/'old-q.json';path.write_text(json.dumps(q))
        with self.assertRaisesRegex(ValueError,'new E independent qualification'):self.coord.register_qualification(path)

if __name__=='__main__':unittest.main()
