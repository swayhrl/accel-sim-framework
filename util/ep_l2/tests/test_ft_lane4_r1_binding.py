"""R1 input/qualification bindings only; synthetic files never launch a simulator."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import run_ft_lane4_diagnostic as subject


class R1Binding(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client,cls.api,cls.tools=subject.load_tools()

    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)
        def file(name,value):
            p=self.root/name;p.write_text(value);return p
        self.binary=file('synthetic-binary.txt','SYNTHETIC_NOT_EXECUTABLE\n'+ '\n'.join(
            '-gpgpu_ep_l2_ideal_'+s for s in ['wb','meta','read_hit']))
        cfg=file('baseline.config','-gpgpu_dram_timing_opt "nbk=16:\n CL=12:WL=2"\n')
        trace=file('kernelslist.g','kernel-0.traceg\n');kernel=file('kernel-0.traceg','SYNTHETIC_NOT_A_TRACE\n')
        evidence=file('evidence.txt','SYNTHETIC_UNIT_TEST_FIXTURE_NOT_QUALIFICATION\n')
        parser=file('parser.txt','# synthetic parser identity only\n')
        self.release_path=self.root/'qualified.json'
        self.base=dict(owner='lane5',binary=str(self.binary),
            configs=[dict(name='config-0.config',path=str(cfg))],auxiliary_assets=[],
            trace_files=[dict(name=p.name,path=str(p)) for p in [trace,kernel]],
            entry_trace_name=trace.name,environment={'OMP_NUM_THREADS':'1'},timeout_seconds=1,
            qualified_release=str(self.release_path),parser=dict(path=str(parser),sha256=self.tools.digest(parser)))
        identity=dict(core_source_commit='1'*40,framework_source_commit='2'*40,
            binary_sha256=self.tools.digest(self.binary),runtime_config_sha256='',
            trace_content_sha256=self.tools.content_hash(self.tools.asset_manifest(self.base['trace_files'])),
            workload='convolutionSeparable',epoch_range={'scope':'full_application'},
            feature_vector=dict(finite_wbuf=True,unified_wb=False,tvd=False,ro=False,adaptive_policy=False,
                wbuf_entries=16,payload_capacity_per_slice=1168,bank_count=4,ops_per_bank_cycle=1),
            ideal_vector=dict(wb=False,meta=False,read_hit=False),termination_contract={'normal_exit':True})
        identity['runtime_config_sha256']=self.config_hash(self.base)
        self.base['identity']=identity
        gate=dict(status='PASS',production_driven=True,evidence_path=str(evidence),evidence_sha256=self.tools.digest(evidence))
        ideal_evidence=file('ideal-evidence.txt','SYNTHETIC_MODE_FIXTURE_NOT_QUALIFICATION\n')
        self.release=dict(status='INDEPENDENTLY_QUALIFIED',qualified_by='lane5',evidence_kind='PRODUCTION_DRIVEN',
            **{k:identity[k] for k in ['core_source_commit','framework_source_commit','binary_sha256']},
            qualified_feature_vectors=[identity['feature_vector']],gates={k:gate for k in self.tools.GATES},
            ideal_gates={'I_WB':dict(gate,ideal_vector=subject.B16_MODES['I_WB'],evidence_path=str(ideal_evidence),evidence_sha256=self.tools.digest(ideal_evidence))})
        self.write_release()
        self.spec=copy.deepcopy(self.base)
        self.spec.update(owner='lane4',campaign_class='B16_IDEAL_DIAGNOSTIC',mode='I_WB',
            baseline_spec=copy.deepcopy(self.base),baseline_run_key=self.api.run_key(identity),
            baseline_qualified_release_sha256=self.tools.digest(self.release_path))
        overlay=file('ideal.config','-gpgpu_ep_l2_ideal_wb 1\n-gpgpu_ep_l2_ideal_meta 0\n-gpgpu_ep_l2_ideal_read_hit 0\n')
        self.spec['configs'].append(dict(name='lane4-ideal-vector.config',path=str(overlay)))
        self.spec['identity']['ideal_vector']=copy.deepcopy(subject.B16_MODES['I_WB'])
        self.spec['identity']['runtime_config_sha256']=self.config_hash(self.spec)

    def write_release(self):self.release_path.write_text(json.dumps(self.release))
    def config_hash(self,spec):
        return self.tools.content_hash(dict(ordered_configs=self.tools.asset_manifest(spec['configs'],ordered=True),
            auxiliary_assets=[],environment=spec['environment']))
    def validate(self):return subject.validate_b16_variant(self.spec,self.tools,self.api)
    def refresh_release_binding(self):
        self.write_release();self.spec['baseline_qualified_release_sha256']=self.tools.digest(self.release_path)
    def test_valid_same_binary_with_only_requested_mode_qualified(self):
        result=self.validate();self.assertEqual(result['baseline_run_key'],self.api.run_key(self.base['identity']))
        self.assertEqual(list(self.release['ideal_gates']),['I_WB'])
    def test_normal_r0_baseline_has_no_ideal_gate_requirement(self):
        self.binary.write_text('SYNTHETIC_R0_WITHOUT_DIAGNOSTICS')
        digest=self.tools.digest(self.binary)
        self.base['identity']['binary_sha256']=digest
        self.release['binary_sha256']=digest;self.release.pop('ideal_gates')
        self.write_release()
        result=subject.inspect_baseline(self.base,self.tools)
        self.assertEqual(result['run_key'],self.api.run_key(self.base['identity']))
    def test_core_mismatch(self):
        self.spec['identity']['core_source_commit']='3'*40
        with self.assertRaisesRegex(ValueError,'identity change'):self.validate()
    def test_framework_mismatch(self):
        self.spec['identity']['framework_source_commit']='4'*40
        with self.assertRaisesRegex(ValueError,'identity change'):self.validate()
    def test_binary_mismatch(self):
        self.spec['identity']['binary_sha256']='5'*64
        with self.assertRaisesRegex(ValueError,'identity change'):self.validate()
    def test_trace_mismatch(self):
        self.spec['identity']['trace_content_sha256']='6'*64
        with self.assertRaisesRegex(ValueError,'identity change'):self.validate()
    def test_epoch_mismatch(self):
        self.spec['identity']['epoch_range']['scope']='fragment'
        with self.assertRaisesRegex(ValueError,'identity change'):self.validate()
    def test_environment_changed(self):
        self.spec['environment']['OMP_NUM_THREADS']='2'
        with self.assertRaisesRegex(ValueError,'physical inputs'):self.validate()
    def test_overlay_changes_architecture(self):
        Path(self.spec['configs'][-1]['path']).write_text('-gpgpu_ep_l2_ideal_wb 1\n-gpgpu_ep_l2_wbuf_entries 32\n')
        with self.assertRaisesRegex(ValueError,'overlay changes'):self.validate()
    def test_derived_config_identity_mismatch(self):
        self.spec['identity']['runtime_config_sha256']='f'*64
        with self.assertRaisesRegex(ValueError,'runtime config identity mismatch'):self.validate()
    def test_wrong_baseline_owner(self):
        self.spec['baseline_spec']['owner']='lane4'
        with self.assertRaisesRegex(ValueError,'owner mismatch'):self.validate()
    def test_wrong_baseline_key(self):
        self.spec['baseline_run_key']='0'*64
        with self.assertRaisesRegex(ValueError,'baseline key'):self.validate()
    def test_r0_without_ideal_registrations_cannot_be_r1(self):
        self.binary.write_text('SYNTHETIC_R0_WITHOUT_DIAGNOSTICS')
        digest=self.tools.digest(self.binary)
        self.spec['binary']=str(self.binary);self.spec['identity']['binary_sha256']=digest
        self.spec['baseline_spec']['identity']['binary_sha256']=digest
        self.release['binary_sha256']=digest;self.refresh_release_binding()
        self.spec['baseline_run_key']=self.api.run_key(self.spec['baseline_spec']['identity'])
        with self.assertRaisesRegex(ValueError,'lacks Lane 4 registrations'):self.validate()
    def test_normal_release_without_requested_ideal_qualification(self):
        self.release['ideal_gates']={};self.refresh_release_binding()
        with self.assertRaisesRegex(ValueError,'not independently qualified'):self.validate()
    def test_module_only_gate_cannot_qualify(self):
        self.release['ideal_gates']['I_WB']['production_driven']=False;self.refresh_release_binding()
        with self.assertRaisesRegex(ValueError,'not independently qualified'):self.validate()
    def test_qualification_changed_after_prepare(self):
        self.release['note']='changed';self.write_release()
        with self.assertRaisesRegex(ValueError,'frozen R1 qualification changed'):self.validate()
    def test_mode_evidence_changed(self):
        Path(self.release['ideal_gates']['I_WB']['evidence_path']).write_text('changed fixture')
        with self.assertRaisesRegex(ValueError,'ideal qualification evidence changed'):self.validate()
    def test_vector_uses_boolean_fields(self):
        self.spec['identity']['ideal_vector']['wb']=1
        with self.assertRaisesRegex(ValueError,'boolean'):self.validate()
    def test_combination_outside_two_points(self):
        self.spec['identity']['workload']='sad';self.spec['baseline_spec']['identity']['workload']='sad'
        self.spec['mode']='I_WB_META';self.spec['identity']['ideal_vector']=subject.B16_MODES['I_WB_META']
        with self.assertRaisesRegex(ValueError,'combination not scheduled'):self.validate()


if __name__=='__main__':unittest.main()
