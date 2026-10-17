import json
from pathlib import Path
import tempfile
import unittest
from run import digest,validate_native_legacy_semantic_proof
class NativeSemanticAdmission(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.path=Path(self.tmp.name)/'proof.json';self.release={'input_adapter_revision':{'source_commit':'adapter'}};self.identity={'core_source_commit':'core','framework_source_commit':'fw','binary_sha256':'binary','workload':'app'};self.body={'name':'kernel-1.traceg','sha256':'body','bytes':20};self.report={'status':'PASS_FULL_NATIVE_BYTE_AND_ZERO_MASK_SEMANTIC_PROOF','tool_sha256':'tool','tooling_source_commit':'source','source_identity':self.identity,'workloads':[{'workload':'app','status':'FULL_ORIGINAL_BYTES_AND_NATIVE_ZERO_MASK_SEMANTICS_PROVEN','files':[self.body]}]};self.path.write_text(json.dumps(self.report));sha=digest(self.path);self.binding={'report_sha256':sha,'tool_sha256':'tool','source_commit':'source'};self.spec={'identity':dict(self.identity),'entry_trace_name':'kernelslist.g','native_legacy_semantic_proof':{'path':str(self.path),'sha256':sha}};self.traces=[self.body,{'name':'kernelslist.g','sha256':'list','bytes':10}]
    def test_exact_source_and_complete_bytes_pass(self):validate_native_legacy_semantic_proof(self.spec,self.release,self.traces,self.binding)
    def test_missing_proof_refuses(self):
        self.spec.pop('native_legacy_semantic_proof')
        with self.assertRaises(ValueError):validate_native_legacy_semantic_proof(self.spec,self.release,self.traces,self.binding)
    def test_changed_proof_refuses(self):
        self.path.write_text('{}')
        with self.assertRaises(ValueError):validate_native_legacy_semantic_proof(self.spec,self.release,self.traces,self.binding)
    def test_wrong_source_or_partial_body_refuses(self):
        self.spec['identity']['binary_sha256']='other'
        with self.assertRaises(ValueError):validate_native_legacy_semantic_proof(self.spec,self.release,self.traces,self.binding)
        self.spec['identity']=dict(self.identity)
        with self.assertRaises(ValueError):validate_native_legacy_semantic_proof(self.spec,self.release,[],self.binding)
if __name__=='__main__':unittest.main()
