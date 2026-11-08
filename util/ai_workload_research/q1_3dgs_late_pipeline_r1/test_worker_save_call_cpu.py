"""Execute the real Controller.save method with CPU mock Runner/store."""
import os
os.sched_setaffinity(0,{22,23})
import ast
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import time
import types
import unittest
from unittest.mock import patch

SOURCE=Path(__file__).with_name("worker.py")


class FakeRng:
    def tolist(self):return [1,2,3]


class SaveCallTests(unittest.TestCase):
    def test_real_save_calls_both_fingerprints_and_publishes_bound_receipts(self):
        tree=ast.parse(SOURCE.read_text())
        cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=="Controller")
        method=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=="save")
        wrapper=ast.ClassDef(name="SaveController",bases=[],keywords=[],
                            body=[method],decorator_list=[])
        module=ast.fix_missing_locations(ast.Module(body=[wrapper],type_ignores=[]))
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)
            def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
            def dump(path,value):
                Path(path).parent.mkdir(parents=True,exist_ok=True)
                Path(path).write_text(json.dumps(value))
            namespace=dict(Path=Path,copy=copy,time=time,OUT=out,
                CFG={"goal_start_epoch":123},sha=sha,dump=dump,
                state_dir=lambda name:out/".private/STATES"/name)
            exec(compile(module,"<real-save>","exec"),namespace)
            control=namespace["SaveController"]()
            bundle={"loader":{"initial_base_seed_rng_state":FakeRng()},
                    "current_camera_ids":[17],"frontier":{"pending":7}}
            runner=object()
            control.capture=lambda real_runner,step,loc:bundle
            control.source_sha="source";control.saved=[]
            calls=[]
            store=types.ModuleType("state_store")
            store.fingerprint=lambda value:calls.append("legacy") or "legacy-value"
            store.semantic_fingerprint=lambda value:calls.append("semantic") or "semantic-value"
            def save_state(value,path,**kwargs):
                calls.append("save")
                path.mkdir(parents=True)
                (path/"bundle.pkl").write_bytes(b"mock-state")
                result={"metadata_sha256":sha(path/"bundle.pkl"),"storages":[]}
                (path/"MANIFEST.json").write_text(json.dumps(result))
                return result
            store.save_state=save_state
            with patch.dict(sys.modules,{"state_store":store}):
                result=control.save("C_AA",runner,7,{})
            self.assertEqual(result,"legacy-value")
            self.assertEqual(calls,["legacy","semantic","save"])
            path=out/".private/STATES/C_AA"
            side=json.loads(path.with_suffix(".sidecar.json").read_text())
            public=json.loads((out/"raw/STATE_C_AA_MANIFEST.json").read_text())
            self.assertEqual(side["semantic_state_fingerprint"],"semantic-value")
            self.assertEqual(public["semantic_state_fingerprint"],"semantic-value")
            self.assertEqual(side["manifest_sha256"],sha(path/"MANIFEST.json"))
            self.assertEqual(public["sidecar_sha256"],sha(path.with_suffix(".sidecar.json")))
            self.assertEqual(side["next_step"],8)
            self.assertEqual(side["loader"]["initial_base_seed_rng_state"],[1,2,3])
            self.assertEqual(len(control.saved),1)


if __name__=="__main__":unittest.main(verbosity=2)
