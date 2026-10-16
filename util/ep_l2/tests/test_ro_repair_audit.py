"""Negative tests for the static audit itself; no C++ runtime claim."""
import importlib.util
import os
from pathlib import Path
import unittest

spec=importlib.util.spec_from_file_location('audit_ro_repair',Path(__file__).parents[1]/'audit_ro_repair.py')
audit=importlib.util.module_from_spec(spec);spec.loader.exec_module(audit)


@unittest.skipUnless(os.environ.get('EP_L2_RO_CORE_ROOT'),'explicit Core source required')
class ExactCandidateAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.source,cls.parent=audit.load(Path(os.environ['EP_L2_RO_CORE_ROOT']))
    def check(self,source):return audit.source_checks(source,self.parent)
    def change(self,name,old,new):
        files=dict(self.source)
        self.assertIn(old,files[name]);files[name]=files[name].replace(old,new,1);return files
    def test_exact_source_checks(self):self.assertTrue(all(self.check(self.source).values()))
    def test_braces_in_comments_and_literals(self):
        f='void demo() { const char *s="}"; /* } */ if(s){return;} }'
        self.assertEqual(audit.function(f+'\nvoid other() {}','void demo'),f)
    def test_missing_try_guard_rejected(self):
        x=self.change('ep-l2-ft-cache.inc','  if(m_ro && !m_ro->prefill_allowed())return false;\n','')
        self.assertFalse(self.check(x)['ro_try_prefill_guard_before_mutation'])
    def test_late_try_guard_rejected(self):
        files=dict(self.source);warm=audit.function(files['ep-l2-ft-cache.inc'],'bool l2_cache::ft_try_force_tag_access')
        guard='  if(m_ro && !m_ro->prefill_allowed())return false;\n'
        late=warm.replace(guard,'').replace('  baseline_cache::force_tag_access(addr, time, mask);',guard+'  baseline_cache::force_tag_access(addr, time, mask);')
        files['ep-l2-ft-cache.inc']=files['ep-l2-ft-cache.inc'].replace(warm,late)
        self.assertFalse(self.check(files)['ro_try_prefill_guard_before_mutation'])
    def test_common_dirty_gate_change_rejected(self):
        x=self.change('ep-l2-ft-cache.inc','m_tag_array->block_is_modified(index)','false')
        self.assertFalse(self.check(x)['preserves_l1_try_prefill_checks'])
    def test_offset_clock_rejected(self):
        x=self.change('ep-l2-ro-runtime.inc','return c.ft_physical_cycle();','return c.ft_physical_cycle()+4096;')
        self.assertFalse(self.check(x)['shared_physical_clock_helper'])
    def test_detached_tag_install_change_rejected(self):
        files=dict(self.source);fill=audit.function(files['ep-l2-ro-transactions.h'],'  bool fill(identity h, unsigned mask')
        changed=fill.replace('if (e.attached) {','if (true) {')
        self.assertNotEqual(fill,changed)
        files['ep-l2-ro-transactions.h']=files['ep-l2-ro-transactions.h'].replace(fill,changed)
        self.assertFalse(self.check(files)['detached_fill_has_no_tag_install'])
    def test_duplicate_bank_observer_rejected(self):
        files=dict(self.source)
        observer=audit.function(files['l2cache.h'],'unsigned long long ft_bank_grants_for_test(unsigned bank) const')
        x=self.change('l2cache.h',observer,observer+'\n  '+observer)
        self.assertFalse(self.check(x)['single_common_bank_observer'])
    def test_old_fixture_clock_rejected(self):
        x=self.change('test_ft_wbuf.cc','cache->cycle(); gpu->gpu_sim_cycle = ++time;',
                      'gpu->gpu_sim_cycle=time++; cache->cycle();')
        self.assertFalse(self.check(x)['exact_common_directed_fixture'])
    def test_descriptor_capacity_change_rejected(self):
        x=self.change('ep-l2-ro-transactions.h','shared.descriptor_pool_capacity() != 512','shared.descriptor_pool_capacity() != 1024')
        self.assertFalse(self.check(x)['shared_D512_descriptor_admission'])


if __name__=='__main__':unittest.main()
