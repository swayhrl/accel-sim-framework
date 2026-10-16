"""Withdrawal veto tests with synthetic files; no simulator or qualification is created."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import ft_lane4_scientific_acceptance as subject


def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def key(i):return hashlib.sha256(json.dumps(i,sort_keys=True).encode()).hexdigest()


class Acceptance(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);root=Path(self.tmp.name)
        self.evidence=root/'synthetic-evidence.txt';self.evidence.write_text('NOT_PRODUCTION_EVIDENCE_SYNTHETIC_UNIT_TEST_ONLY')
        self.path=root/'synthetic-qualified.json'
        self.identity=dict(core_source_commit='a'*40,framework_source_commit='b'*40,binary_sha256='c'*64,
            runtime_config_sha256='d'*64,trace_content_sha256='e'*64,workload='convolutionSeparable',
            epoch_range={'scope':'full_application'},feature_vector={'synthetic':True},ideal_vector={'wb':True})
        gate=dict(status='PASS',production_driven=True,evidence_path=str(self.evidence),evidence_sha256=digest(self.evidence))
        self.release=dict(status='INDEPENDENTLY_QUALIFIED',qualified_by='lane5',evidence_kind='PRODUCTION_DRIVEN',
            **{k:self.identity[k] for k in subject.IDENTITY_FIELDS[:3]},gates={k:copy.deepcopy(gate) for k in subject.REPAIR_GATES})
        self.authority=dict(publication_commit='f'*40,records={'APPLICATION_ACCEPTANCE.json':{'rows':[]},'SCIENTIFIC_HOLD.json':{'status':'HISTORIC_SUSPENSION'}},
            sha256={'APPLICATION_ACCEPTANCE.json':'1'*64,'SCIENTIFIC_HOLD.json':'2'*64},
            qualified_release_relative='synthetic-only.json')
        self.refresh()
        self.spec=dict(identity=self.identity,qualified_release=str(self.path))
        self.result=dict(identity=self.identity,run_key=key(self.identity),status='COMPLETE_VALID',raw_log_sha256='9'*64)

    def refresh(self):
        raw=json.dumps(self.release).encode();self.path.write_bytes(raw);self.authority['qualified_release_bytes']=raw
    def launch(self):return subject.check_release_current(self.spec,self.authority,digest)
    def accept(self):return subject.check_result_current(self.result,self.authority,key)
    def accepted_row(self):
        row=dict(self.identity,run_key=self.result['run_key'],scientific_acceptance='CURRENT_ACCEPTED',raw_log_sha256=self.result['raw_log_sha256'])
        self.authority['records']['APPLICATION_ACCEPTANCE.json']['rows']=[row];return row
    def test_repaired_release_eligible_is_not_run_acceptance(self):
        self.assertEqual(self.launch()['current_release_eligibility'],'PASS_NOT_A_RUN_ACCEPTANCE')
        with self.assertRaisesRegex(ValueError,'missing/ambiguous'):self.accept()
    def test_all_three_old_cores_veto_even_with_pass_certificate(self):
        for core in subject.WITHDRAWN_CORES:
            with self.subTest(core=core):
                self.identity['core_source_commit']=core
                with self.assertRaisesRegex(ValueError,'withdrawn'):self.launch()
    def test_old_binary_veto_despite_different_core(self):
        self.identity['binary_sha256']=next(iter(subject.WITHDRAWN_BINARIES))
        with self.assertRaisesRegex(ValueError,'withdrawn'):self.launch()
    def test_latest_source_suspension_overrides_immutable_pass(self):
        self.authority['records']['APPLICATION_ACCEPTANCE.json']['rows']=[dict(core_source_commit=self.identity['core_source_commit'],scientific_acceptance='SUSPENDED_NEW_COUNTEREXAMPLE')]
        with self.assertRaisesRegex(ValueError,'latest Lane5'):self.launch()
    def test_other_unrun_cell_does_not_hold_repaired_source(self):
        self.authority['records']['APPLICATION_ACCEPTANCE.json']['rows']=[dict(core_source_commit=self.identity['core_source_commit'],scientific_acceptance='NOT_RUN')]
        self.assertEqual(self.launch()['current_release_eligibility'],'PASS_NOT_A_RUN_ACCEPTANCE')
    def test_missing_raw_hash_rejected(self):
        row=self.accepted_row();row.pop('raw_log_sha256');self.result.pop('raw_log_sha256')
        with self.assertRaisesRegex(ValueError,'raw log hash'):self.accept()
    def test_published_suspended_certificate(self):
        self.release['status']='SUSPENDED';self.refresh()
        with self.assertRaisesRegex(ValueError,'not independently qualified'):self.launch()
    def test_local_pass_differs_from_published_bytes(self):
        self.path.write_text('changed')
        with self.assertRaisesRegex(ValueError,'qualification hash'):self.launch()
    def test_missing_physical_clock_gate(self):
        del self.release['gates']['physical_bank_clock'];self.refresh()
        with self.assertRaisesRegex(ValueError,'physical_bank_clock'):self.launch()
    def test_missing_memcpy_identity_gate(self):
        del self.release['gates']['memcpy_payload_identity'];self.refresh()
        with self.assertRaisesRegex(ValueError,'memcpy_payload_identity'):self.launch()
    def test_nonproduction_repair_gate(self):
        self.release['gates']['physical_bank_clock']['production_driven']=False;self.refresh()
        with self.assertRaisesRegex(ValueError,'repair gate'):self.launch()
    def test_repair_evidence_changed(self):
        self.evidence.write_text('changed')
        with self.assertRaisesRegex(ValueError,'repair evidence changed'):self.launch()
    def test_current_exact_row_accepted(self):
        self.accepted_row();self.assertEqual(self.accept()['status'],'CURRENT_ACCEPTED')
    def test_later_revocation_overrides_previous_acceptance(self):
        row=self.accepted_row();self.assertEqual(self.accept()['status'],'CURRENT_ACCEPTED')
        row['scientific_acceptance']='SUSPENDED_LATER_PROBE'
        before=copy.deepcopy(self.result)
        with self.assertRaises(ValueError):self.accept()
        self.assertEqual(self.result,before)
    def test_missing_acceptance_fails_closed(self):
        with self.assertRaisesRegex(ValueError,'missing/ambiguous'):self.accept()
    def test_ambiguous_acceptance_fails_closed(self):
        row=self.accepted_row();self.authority['records']['APPLICATION_ACCEPTANCE.json']['rows'].append(copy.deepcopy(row))
        with self.assertRaisesRegex(ValueError,'missing/ambiguous'):self.accept()
    def test_acceptance_config_mismatch(self):
        self.accepted_row()['runtime_config_sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'identity mismatch'):self.accept()
    def test_acceptance_trace_mismatch(self):
        self.accepted_row()['trace_content_sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'identity mismatch'):self.accept()
    def test_acceptance_raw_mismatch(self):
        self.accepted_row()['raw_log_sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'raw hash'):self.accept()
    def test_key_recomputed_not_trusted(self):
        self.accepted_row();self.result['run_key']='0'*64
        with self.assertRaisesRegex(ValueError,'run-key'):self.accept()
    def test_incomplete_execution_cannot_be_accepted(self):
        self.accepted_row();self.result['status']='FAILED'
        with self.assertRaisesRegex(ValueError,'execution'):self.accept()


if __name__=='__main__':unittest.main()
