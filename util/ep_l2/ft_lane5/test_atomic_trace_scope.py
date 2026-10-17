"""Tiny new native-format fixtures only; no production trace reads or simulator."""
import gzip
import hashlib
import io
import json
import sys
from unittest.mock import patch
from pathlib import Path
import tempfile
import unittest

import atomic_trace_scope as scope
from atomic_trace_scope import inspect_lines,kernel

OPS={'MOV':'OP_MOV','ATOM':'OP_ATOM','ATOMG':'OP_ATOMG','ATOMS':'OP_ATOMS','RED':'OP_RED'}
MOV='0 0 0 0 0000 ffffffff 1 R0 MOV 0 0'
ATOM='0 0 0 0 0000 ffffffff 1 R0 ATOM.E.ADD 1 R1 4 1 0x1000 4'


def trace(rows,count=None,version=0,lineinfo=0):
    n=len(rows) if count is None else count
    return ('-kernel name = fixture\n-kernel id = 1\n-grid dim = (1,1,1)\n-block dim = (32,1,1)\n-binary version = 70\n'
            f'-accelsim tracer version = {version}\n-enable lineinfo = {lineinfo}\n'
            '#traces format = native\n#BEGIN_TB\nthread block = 0,0,0\nwarp = 0\n'+f'insts = {n}\n'+'\n'.join(rows)+'\n#END_TB\n')


def inspect(text):return inspect_lines(io.StringIO(text),{70:OPS})


class AtomicScope(unittest.TestCase):
    def test_complete_nonatomic(self):
        r=inspect(trace([MOV]));self.assertTrue(r['atomic_absence']);self.assertEqual(r['instruction_records'],1)

    def test_global_atomic_suffix_and_active_lanes(self):
        r=inspect(trace([ATOM]));self.assertFalse(r['atomic_absence']);self.assertEqual(r['global_atomic_records'],1);self.assertEqual(r['global_atomic_active_lane_records'],32)

    def test_shared_atomic_is_recorded_separately_not_claimed_absent(self):
        r=inspect(trace([ATOM.replace('ATOM.E.ADD','ATOMS.ADD')]));self.assertEqual(r['global_atomic_records'],0);self.assertEqual(r['shared_atomic_records'],1);self.assertFalse(r['atomic_absence'])

    def test_masked_reduction_still_reports_opcode_presence(self):
        s='0 0 0 0 0000 00000000 0 RED.E.ADD 1 R1 4 1 0x1000 4';r=inspect(trace([s]));self.assertEqual(r['global_atomic_records'],1);self.assertEqual(r['global_atomic_active_lane_records'],0);self.assertFalse(r['atomic_absence'])

    def test_modern_lineinfo_uses_native_prefix_rule(self):
        s='77 0000 ffffffff 1 R0 ATOMG.E.ADD 1 R1 4 1 0x1000 4';r=inspect(trace([s],version=3,lineinfo=1));self.assertEqual(r['global_atomic_records'],1)

    def test_truncated_count_cannot_turn_into_zero_atomic(self):
        with self.assertRaisesRegex(ValueError,'Truncated'):inspect(trace([MOV],count=2))

    def test_extra_record_refuses(self):
        with self.assertRaisesRegex(ValueError,'extra instruction'):inspect(trace([MOV,ATOM],count=1))

    def test_unknown_opcode_refuses(self):
        with self.assertRaisesRegex(ValueError,'Unknown native opcode'):inspect(trace([MOV.replace('MOV','UNKNOWN')]))

    def test_register_shift_refuses(self):
        with self.assertRaisesRegex(ValueError,'destination register'):inspect(trace([MOV.replace('1 R0 MOV','1 MOV')]))

    def test_duplicate_tb_refuses(self):
        s=trace([MOV]);part=s[s.index('#BEGIN_TB'):]
        with self.assertRaisesRegex(ValueError,'Duplicate'):inspect(s+part)

    def test_native_dimension_spacing(self):
        r=inspect(trace([MOV]).replace('(1,1,1)','(1, 1, 1)').replace('(32,1,1)','(32, 1, 1)'))
        self.assertTrue(r['atomic_absence'])

    def test_known_uncorrected_release_no_full_scan_or_lease(self):
        with tempfile.TemporaryDirectory(prefix='ep_l2_atomic_scope_test_') as raw:
            d=Path(raw);identity={'core_source_commit':'088146f7f85b4073deb5d166a0a4484c7f3b48b2','framework_source_commit':'861a06b91e309832161eab0836b512853c833ffb','binary_sha256':'e'*64,'runtime_config_sha256':'c'*64,'trace_content_sha256':'d'*64,'workload':'test','feature_vector':{'finite_wbuf':True},'ideal_vector':{'wb':False},'epoch_range':{'scope':'full_application'},'termination_contract':{'normal_exit':True}}
            p=d/'spec.json';p.write_text(json.dumps({'identity':identity}));producer={**{k:identity[k] for k in ['core_source_commit','framework_source_commit','binary_sha256']},'owner':'lane1','release':'R0.1','status':'PRODUCER_TESTS_PASS_NOT_INDEPENDENTLY_QUALIFIED'}
            argv=['atomic_trace_scope','--spec',str(p),'--framework',str(d),'--critical-release-publication','f'*40,'--producer-receipt-path','docs/receipt.json','--out',str(d/'out.json'),'--deadline-unix','9999999999']
            with patch.object(sys,'argv',argv),patch.object(scope.subprocess,'check_output',return_value=json.dumps(producer).encode()),patch.object(scope,'kernel') as scan,patch.object(scope,'Registry') as registry:
                with self.assertRaisesRegex(ValueError,'corrected-source milestone'):scope.main()
                scan.assert_not_called();registry.assert_not_called();self.assertFalse((d/'out.json').exists())

    def test_plain_and_gzip_hash_exact_raw_bytes(self):
        with tempfile.TemporaryDirectory(prefix='ep_l2_atomic_scope_test_') as raw:
            text=trace([ATOM]).replace('\n','\r\n').encode();p=Path(raw)/'a.traceg';p.write_bytes(text)
            report,binding=kernel(p,{70:OPS});self.assertEqual(binding['sha256'],hashlib.sha256(text).hexdigest());self.assertEqual(report['global_atomic_records'],1)
            z=gzip.compress(text,mtime=0);q=Path(raw)/'a.traceg.gz';q.write_bytes(z);report,binding=kernel(q,{70:OPS});self.assertEqual(binding['sha256'],hashlib.sha256(z).hexdigest());self.assertEqual(binding['bytes'],len(z));self.assertEqual(report['global_atomic_records'],1)

    def test_corrupt_gzip_refuses_without_eligibility(self):
        with tempfile.TemporaryDirectory(prefix='ep_l2_atomic_scope_test_') as raw:
            data=bytearray(gzip.compress(trace([MOV]).encode(),mtime=0));data[-8]^=255;p=Path(raw)/'bad.traceg.gz';p.write_bytes(data)
            with self.assertRaises((gzip.BadGzipFile,EOFError,OSError)):kernel(p,{70:OPS})


if __name__=='__main__':unittest.main()
