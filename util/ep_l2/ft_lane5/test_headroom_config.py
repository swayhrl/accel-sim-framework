"""Admission security tests; no simulator, lease or producer qualification."""
import copy
import json
from pathlib import Path
import tempfile
import unittest

from headroom_config import validate,options,EXPERIMENT,COORDINATION,OVERRIDES
from run import asset_manifest,content_hash,digest

REPO=Path(__file__).resolve().parents[3]

class HeadroomConfigTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
        self.spec=json.loads(Path('/workspace/results/ep_l2_ft20261016/lane5_a1_b1_formal_preparation_r1/specs/FWT_7_21_B16_BANKED.json').read_text())
        self.spec.update(experiment_id=EXPERIMENT,regime='D4')
        self.overlay=self.root/'overlay.config';self.overlay.write_text(''.join(k+' '+v+'\n' for k,v in OVERRIDES['D4'].items()))
        self.spec['configs'].append({'name':'config-5.config','path':str(self.overlay)})
        self.configs=asset_manifest(self.spec['configs'],ordered=True);self.assets=[]
        self.spec['identity']['runtime_config_sha256']=content_hash({'ordered_configs':self.configs,'auxiliary_assets':self.assets,'environment':self.spec['environment']})
        self.evidence=self.root/'evidence.json';self.evidence.write_text('{}')
        self.manifest={'status':'INDEPENDENT_CONFIG_PASS','coordination_commit':COORDINATION,'experiment_id':EXPERIMENT,'regime':'D4','identity':self.spec['identity'],'modes':{'B16_BANKED':{'ordered_configs':self.configs,'auxiliary_assets':self.assets,'environment':self.spec['environment'],'runtime_config_sha256':self.spec['identity']['runtime_config_sha256'],'effective_options':options([r['path'] for r in self.spec['configs']])}},'evidence':[{'path':str(self.evidence),'sha256':digest(self.evidence)}]}
        self.path=self.root/'qualification.json';self.release={};self.save()
    def save(self):
        self.path.write_text(json.dumps(self.manifest));self.release['downstream_config_qualification']={'path':str(self.path),'sha256':digest(self.path)}
    def check(self):return validate(self.spec,self.release,self.configs,self.assets)
    def test_actual_initialized_dump_and_clock_guard(self):
        from headroom_config import validate_runtime_dump
        raw=self.root/'raw.log';native=Path('/workspace/results/ep_l2_ft20261016/8f445bf74185f8c6640741372a637ae873be08ac796a2920441e0379acd6c86c/raw.log')
        lines=[]
        with native.open() as stream:
            for line in stream:
                if line.startswith('-') or line.startswith('GPGPU-Sim uArch: clock freqs: '):lines.append(line)
        text=''.join(lines)
        import re
        for key,value in OVERRIDES['D4'].items():text=re.sub(r'(?m)^'+re.escape(key)+r'\s+[^#\n]+',key+' '+value+' ',text)
        text=text.replace(':850000000.000000',':3400000000.000000');raw.write_text(text)
        self.assertEqual(validate_runtime_dump(raw,self.spec)['clock_frequencies_Hz'][-1],3400000000)
        raw.write_text(text.replace(':3400000000.000000',':850000000.000000'))
        with self.assertRaisesRegex(ValueError,'clocks differ'):validate_runtime_dump(raw,self.spec)
        raw.write_text(text.replace('-dram_latency                         100','-dram_latency                         25'))
        with self.assertRaisesRegex(ValueError,'option dump differs'):validate_runtime_dump(raw,self.spec)
    def test_exact_condition_pass(self):self.assertEqual(self.check()['regime'],'D4')
    def test_missing_condition_qualification_refuses(self):
        with self.assertRaisesRegex(ValueError,'Diagnostic requires'):validate(self.spec,{},self.configs,self.assets)
    def test_unknown_H0_config_refuses(self):
        self.spec.pop('experiment_id');self.spec.pop('regime')
        with self.assertRaisesRegex(ValueError,'Unknown runtime'):validate(self.spec,{},self.configs,self.assets)
    def test_wrong_group_and_regime_refuse(self):
        for key,value in [('experiment_id','H0'),('regime','Q4')]:
            before=self.spec[key];self.spec[key]=value
            with self.assertRaises(ValueError):self.check()
            self.spec[key]=before
    def test_modified_production_evidence_refuses(self):
        self.evidence.write_text('{"changed":true}')
        with self.assertRaisesRegex(ValueError,'evidence changed'):self.check()
    def test_different_source_refuses(self):
        self.manifest['identity']=copy.deepcopy(self.spec['identity']);self.manifest['identity']['core_source_commit']='0'*40;self.save()
        with self.assertRaisesRegex(ValueError,'source/binary mismatch'):self.check()
    def test_hidden_nonwhitelisted_overlay_refuses_even_if_manifest_resealed(self):
        self.overlay.write_text(self.overlay.read_text()+'-gpgpu_ep_l2_wad_entries 512\n')
        self.configs=asset_manifest(self.spec['configs'],ordered=True);row=self.manifest['modes']['B16_BANKED'];row['ordered_configs']=self.configs;self.spec['identity']['runtime_config_sha256']=content_hash({'ordered_configs':self.configs,'auxiliary_assets':[],'environment':self.spec['environment']});row['runtime_config_sha256']=self.spec['identity']['runtime_config_sha256'];self.save()
        with self.assertRaisesRegex(ValueError,'forbidden'):self.check()
    def test_environment_or_order_refuses(self):
        self.spec['environment']['OMP_NUM_THREADS']='2'
        with self.assertRaisesRegex(ValueError,'assets/environment'):self.check()
    def test_unqualified_simple_path_refuses(self):
        self.spec['regime']='LOWER_CEILING';self.manifest['regime']='LOWER_CEILING';self.save()
        with self.assertRaisesRegex(ValueError,'condition'):self.check()
    def test_original_H0_unchanged_accepts(self):
        s=json.loads(Path('/workspace/results/ep_l2_ft20261016/lane5_a1_b1_formal_preparation_r1/specs/FWT_7_21_B16_BANKED.json').read_text());self.assertIsNone(validate(s,{},asset_manifest(s['configs'],ordered=True),[]))
class RegistryExperimentTests(unittest.TestCase):
    def setUp(self):
        from registry import write_json,Registry
        from test_lane5 import identity
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name);(self.root/'REGISTRY.lock').touch()
        self.data=json.loads(Path('/workspace/ep_l2_ft20261016_shared/RUN_REGISTRY.json').read_text());self.data['runs']={str(i):{'experiment_id':EXPERIMENT} for i in range(24)}
        write_json(self.root/'RUN_REGISTRY.json',self.data);self.registry=Registry(self.root);self.identity=identity();self.experiment={'experiment_id':EXPERIMENT,'regime':'D4','deadline_unix':1792256956}
    def test_cap_counts_failed_and_reserved_attempts(self):
        with self.assertRaisesRegex(ValueError,'cap'):self.registry.claim(self.identity,'lane5',self.root/'output',experiment=self.experiment)
    def test_expired_window_refuses(self):
        self.experiment['deadline_unix']=0
        with self.assertRaisesRegex(ValueError,'deadline|altered'):self.registry.claim(self.identity,'lane5',self.root/'output',experiment=self.experiment)
    def test_wrong_owner_or_unqualified_regime_refuses(self):
        with self.assertRaisesRegex(ValueError,'unknown|dispatcher'):self.registry.claim(self.identity,'lane4',self.root/'output',experiment=self.experiment)
        self.experiment['regime']='LOWER_CEILING'
        with self.assertRaisesRegex(ValueError,'unknown|dispatcher'):self.registry.claim(self.identity,'lane5',self.root/'output',experiment=self.experiment)
if __name__=='__main__':unittest.main()
