"""CPU stdlib-only control tests; never imports worker or device framework."""
import os
os.sched_setaffinity(0,{22,23})
import ast
import gc
import json
from pathlib import Path
import re
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

WORKER=Path(__file__).with_name("worker.py")
TREE=ast.parse(WORKER.read_text())


def selected(names, namespace):
    body=[node for node in TREE.body if isinstance(node,(ast.FunctionDef,ast.ClassDef))
          and node.name in names]
    exec(compile(ast.Module(body=body,type_ignores=[]),"<worker-selected>","exec"),namespace)
    return namespace


class PathTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        root=Path(self.temp.name)
        self.out=root/"new";self.external=root/"old"
        self.external.mkdir()
        self.namespace=selected({"state_dir","restore_state_dir"},dict(
            Path=Path,re=re,OUT=self.out,
            CFG={"external_readonly_state_root":str(self.external)}))
    def tearDown(self):self.temp.cleanup()
    def test_external_readonly_fallback(self):
        (self.external/"C_E").mkdir()
        self.assertEqual(self.external/"C_E",self.namespace["restore_state_dir"]("C_E"))
        self.assertEqual(self.out/".private/STATES/C_E",self.namespace["state_dir"]("C_E"))
    def test_owned_new_generation_preferred(self):
        own=self.namespace["state_dir"]("C_E");own.mkdir(parents=True)
        (self.external/"C_E").mkdir()
        self.assertEqual(own,self.namespace["restore_state_dir"]("C_E"))
    def test_nonapproved_external_rejected(self):
        (self.external/"C_D").mkdir()
        with self.assertRaisesRegex(AssertionError,"NOT_APPROVED"):
            self.namespace["restore_state_dir"]("C_D")
    def test_invalid_name_rejected(self):
        for name in ["../C_E","/tmp/foreign","C-E",""]:
            with self.assertRaises(AssertionError):
                self.namespace["state_dir"](name)
    def test_external_symlink_rejected(self):
        other=Path(self.temp.name)/"foreign";other.mkdir()
        (self.external/"C_E").symlink_to(other,target_is_directory=True)
        with self.assertRaises(AssertionError):
            self.namespace["restore_state_dir"]("C_E")


class ControlTests(unittest.TestCase):
    def make(self,mode,actual_semantic="same"):
        controller=next(n for n in TREE.body
                        if isinstance(n,ast.ClassDef) and n.name=="Controller")
        method=next(n for n in controller.body
                    if isinstance(n,ast.FunctionDef) and n.name=="assert_restored")
        tree=ast.Module(body=[ast.ClassDef(
            name="Control",bases=[],keywords=[],body=[method],decorator_list=[])],
            type_ignores=[])
        ast.fix_missing_locations(tree)
        class BlockDone(Exception):pass
        records=[]
        namespace=dict(gc=gc,BlockDone=BlockDone,
                       dump=lambda path,value:records.append(value))
        exec(compile(tree,"<restore-control>","exec"),namespace)
        control=namespace["Control"]()
        control.capture=lambda runner,step,loc:dict(frontier={"pending":step})
        control.resume_next_step=5;control.sidecar={"state_fingerprint":"old"}
        control.expected_restore_semantic="same"
        control.context=Path("/mock");control.bundle=object()
        control.resume_live=object();control.current_ids=[18]
        control.job={"mode":mode};control.result={"status":"RUNNING"}
        store=types.ModuleType("state_store")
        store.fingerprint=lambda value:"different-python-memo"
        store.semantic_fingerprint=lambda value:actual_semantic
        return control,BlockDone,store,records
    def test_restore_only_stops_before_math(self):
        control,stop,store,records=self.make("RESTORE_ONLY")
        with patch.dict(sys.modules,{"state_store":store}):
            with self.assertRaises(stop):
                control.assert_restored(None,[],{})
        self.assertEqual(control.result["new_training_steps"],0)
        self.assertEqual(control.result["reached_next_step"],5)
        self.assertEqual(control.result["continuation_numeric_class"],"NOT_EXECUTED")
        self.assertEqual(control.result["roundtrip_class"],"ACTUAL_RUNNER_STATE_EXACT")
        self.assertFalse(records[0]["legacy_fingerprint_equal"])
        self.assertTrue(records[0]["semantic_fingerprint_equal"])
    def test_actual_semantic_mismatch_stops(self):
        control,stop,store,records=self.make("RESTORE_ONLY","bad")
        with patch.dict(sys.modules,{"state_store":store}):
            with self.assertRaisesRegex(AssertionError,"NOT_EXACT"):
                control.assert_restored(None,[],{})
        self.assertEqual(control.result["status"],"RUNNING")
    def test_produce_continues_only_after_exact_roundtrip(self):
        control,stop,store,records=self.make("PRODUCE")
        with patch.dict(sys.modules,{"state_store":store}):
            control.assert_restored(None,[],{})
        self.assertIsNone(control.bundle)
        self.assertIsNone(control.resume_live)
    def test_restore_uses_separate_resolver(self):
        text=WORKER.read_text()
        self.assertIn('restore_runner(ctl,runner,restore_state_dir(job["restore"]))',text)
    def test_save_endpoint_and_semantic_fields_present(self):
        text=WORKER.read_text()
        self.assertIn('self.save(self.job["final_checkpoint_name"],runner,step,loc)',text)
        self.assertIn('"semantic_state_fingerprint":semantic',text)
        self.assertIn('expected_semantic=self.job.get("expected_semantic_fingerprint")',text)
    def test_author_math_not_rewritten_in_worker(self):
        text=WORKER.read_text()
        self.assertIn('cfg.max_steps==200000',text)
        self.assertNotRegex(text,r"cfg\.max_steps\s*=(?!=)")
        self.assertNotIn('cfg.strategy.refine_stop_iter=',text)
    def test_worker_static_compile(self):
        compile(WORKER.read_text(),str(WORKER),"exec")


if __name__=="__main__":unittest.main(verbosity=2)
