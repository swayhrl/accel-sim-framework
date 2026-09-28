import ast,math,unittest
from pathlib import Path
from contracts import *

class Tests(unittest.TestCase):
 def test_tiny(self): self.assertEqual(tiny_reference()["reference_sha256"],TINY_SHA)
 def test_points(self):
  self.assertEqual(KS,(2048,2560,3072,4096)); self.assertTrue(all(k%128==0 for k in KS))
  self.assertEqual([point_math(k,1)["gemm_grid"] for k in KS],[6144]*4); self.assertEqual([point_math(k,8)["gemm_grid"] for k in KS],[49152]*4)
  self.assertEqual([point_math(k,1)["scratch_bytes"] for k in KS],[25165824]*4); self.assertEqual([point_math(k,8)["scratch_bytes"] for k in KS],[201326592]*4)
 def test_footprints(self):
  self.assertEqual([point_math(k,1)["full_w4_bytes"] for k in KS],[52297728,65372160,78446592,104595456])
  self.assertEqual([candidate_split8_static_bytes(k) for k in KS],[7274496,9093120,10911744,14548992])
 def test_delayed_cuda(self):
  root=Path(__file__).parent; text=(root/'runner.py').read_text(); tree=ast.parse(text); imports=[]
  for node in tree.body:
   if isinstance(node,ast.Import): imports += [x.name for x in node.names]
   if isinstance(node,ast.ImportFrom): imports.append(node.module or '')
  self.assertNotIn('torch',imports); main=text[text.index('def main():'):]; self.assertLess(main.index('require_lock()'),main.index('import_module("torch")'))
if __name__=='__main__': unittest.main(verbosity=2)
