import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec=importlib.util.spec_from_file_location('prepare_ro_runtime',Path(__file__).parents[1]/'prepare_ro_runtime.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)


class ConfigBinding(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        self.r=self.root/'ranges.csv';self.r.write_text('first_line,last_line_inclusive\n')
        self.m=self.root/'manifest.json'
        self.manifest=dict(schema='EP_L2_RO_ORACLE_V1',epoch='whole_commandlist',scope='TRACE_MODEL_CLOSED_WORLD',
            address_domain='CANONICAL_GPU_GLOBAL_VA_NO_TRANSLATION_ALIAS',unresolved_opcodes={},
            artifacts={'certified_ranges.csv':module.digest(self.r)},commandlist_sha256='a'*64)
        self.b=self.root/'binding.json';self.save()
    def tearDown(self):self.tmp.cleanup()
    def save(self):
        self.m.write_text(json.dumps(self.manifest))
        self.b.write_text(json.dumps(dict(schema_version='EP_L2_RO_INPUT_BINDING_V1',status='ORACLE_INPUT_VERIFIED_NOT_RUNTIME_QUALIFICATION',
            epoch=self.manifest['epoch'],scope=self.manifest['scope'],address_domain=self.manifest['address_domain'],
            oracle_manifest_sha256=module.digest(self.m),certified_ranges_sha256=module.digest(self.r),
            trace_content_sha256='b'*64,eligible_unique_lines=0,eligible_read_lane_references=0)))
    def call(self,d,b):return module.prepare(self.b,self.m,self.r,self.root/'out',d,b)
    def test_empty_certificate_and_separate_bits(self):
        x=self.call(1,0);self.assertEqual(x['features'],dict(ro_tag_detach=True,ro_line_mshr_bypass=False))
        self.assertEqual(x['oracle_input_coverage']['unique_lines'],0)
        self.assertIn('-gpgpu_ep_l2_ro_manifest_sha256 ',(self.root/'out'/'ro.config').read_text())
        with self.assertRaises(FileExistsError):self.call(1,0)
    def test_corrupt_ranges(self):
        self.r.write_text('changed')
        with self.assertRaisesRegex(ValueError,'range identity'):self.call(1,1)
    def test_manifest_identity(self):
        self.m.write_text(self.m.read_text()+' ')
        with self.assertRaisesRegex(ValueError,'manifest identity'):self.call(1,1)
    def test_reject_kernel_scope(self):
        self.manifest['epoch']='one_kernel';self.save()
        with self.assertRaisesRegex(ValueError,'scope'):self.call(1,1)
    def test_reject_unresolved_agents(self):
        self.manifest['unresolved_opcodes']={'LD':1};self.save()
        with self.assertRaisesRegex(ValueError,'uncertain'):self.call(1,1)


if __name__=='__main__':unittest.main()
