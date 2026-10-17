"""Focused input-scope admission guards; no production scan or simulation."""
import json
from pathlib import Path
import tempfile
import unittest
from run import digest, validate_atomic_input_scope

class AtomicAdmission(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.path=Path(self.tmp.name)/'audit.json'
        self.identity={k:k for k in ('core_source_commit','framework_source_commit','binary_sha256','trace_content_sha256')}
        self.traces=[{'name':'kernel-1.traceg','sha256':'content','bytes':10}]
        self.audit={'status':'COMPLETE_NATIVE_OPCODE_AUDIT','input_scope':'COMPLETE_INPUT_HAS_NO_NATIVE_ATOMIC_OPCODE_RECORDS','tool_sha256':'tool','producer_publication':'producer','identity':self.identity,'trace_content_manifest':self.traces,'global_atomic_records_with_repeats':0,'shared_atomic_records_with_repeats':0}
        self.release={'application_input_scope':'FULL_NATIVE_NONATOMIC_ONLY','atomic_input_auditor_sha256':'tool','producer_publication_commit':'producer'}
        self.spec={'identity':dict(self.identity)};self.save()
    def save(self):
        self.path.write_text(json.dumps(self.audit));self.spec['atomic_input_scope']={'path':str(self.path),'sha256':digest(self.path)}
    def test_exact_complete_input_passes(self):
        self.assertEqual(validate_atomic_input_scope(self.spec,self.release,self.traces)['scope'],'FULL_NATIVE_NONATOMIC_ONLY')
    def test_missing_or_changed_proof_refuses(self):
        self.spec.pop('atomic_input_scope')
        with self.assertRaises(ValueError):validate_atomic_input_scope(self.spec,self.release,self.traces)
        self.save();self.path.write_text('{}')
        with self.assertRaises(ValueError):validate_atomic_input_scope(self.spec,self.release,self.traces)
    def test_other_source_or_trace_refuses(self):
        self.spec['identity']['core_source_commit']='other'
        with self.assertRaises(ValueError):validate_atomic_input_scope(self.spec,self.release,self.traces)
        self.spec['identity']=dict(self.identity)
        with self.assertRaises(ValueError):validate_atomic_input_scope(self.spec,self.release,[])
    def test_atomic_present_refuses_even_if_scope_label_falsely_absent(self):
        self.audit['global_atomic_records_with_repeats']=1;self.save()
        with self.assertRaises(ValueError):validate_atomic_input_scope(self.spec,self.release,self.traces)
        self.audit['global_atomic_records_with_repeats']=0;self.audit['shared_atomic_records_with_repeats']=1;self.save()
        with self.assertRaises(ValueError):validate_atomic_input_scope(self.spec,self.release,self.traces)

if __name__=='__main__':unittest.main()
