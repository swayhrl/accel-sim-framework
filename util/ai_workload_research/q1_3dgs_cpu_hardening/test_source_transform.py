"""Static regression checks; no trainer/Torch/CUDA/API execution."""
import os
os.sched_setaffinity(0, {22, 23})
import ast
import copy
import hashlib
from pathlib import Path
import unittest
from source_transform import transform_train, transform_gpu, LIVE_KEYS

AUTHOR = Path("/data/c16/aiarch_a26gr1_gsscale_rubble_109_20261014/software_sources/gsscale/examples/simple_trainer_hybrid_optimized.py")
SOURCE = AUTHOR.read_text()
EXPECTED = "17e70b6466f7e33a24d1610aa7deb69316cd177dc2c212cd8b717b9884f4808a"
TOOL = Path(__file__).parent


def original_method(name):
    cls = next(n for n in ast.parse(SOURCE).body
               if isinstance(n, ast.ClassDef) and n.name == "Runner")
    return copy.deepcopy(next(n for n in cls.body
                              if isinstance(n, ast.FunctionDef) and n.name == name))


def dumps(node):
    return ast.dump(node, include_attributes=False)


def ctl_call(node, methods):
    return (isinstance(node, ast.Expr) and isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Attribute)
            and isinstance(node.value.func.value, ast.Name)
            and node.value.func.value.id == "_q1_ctl"
            and node.value.func.attr in methods)


class StripRegions(ast.NodeTransformer):
    def visit_Call(self,node):
        node=self.generic_visit(node)
        if isinstance(node.func,ast.Name) and node.func.id in {"_q1_copy","_q1_to"}:
            name="copy_" if node.func.id=="_q1_copy" else "to"
            node.func=ast.Attribute(value=node.args[0],attr=name,ctx=ast.Load());node.args=node.args[1:]
        return node
    def visit_Expr(self, node):
        if ctl_call(node, {"region_begin", "region_end"}):
            return None
        return self.generic_visit(node)


class SourceTransformTests(unittest.TestCase):
    def test_author_source_authority(self):
        self.assertEqual(EXPECTED, hashlib.sha256(SOURCE.encode()).hexdigest())

    def test_off_compiles_without_executing_trainer(self):
        compile(ast.Module(body=[transform_train(SOURCE)], type_ignores=[]),
                "<static-off>", "exec")

    def test_diagnostic_compiles_without_executing_trainer(self):
        compile(ast.Module(body=[transform_train(SOURCE, True)], type_ignores=[]),
                "<static-diag>", "exec")

    def test_original_loop_arithmetic_and_control_order_unchanged(self):
        original = original_method("train")
        before = next(n for n in original.body
                      if isinstance(n, ast.For) and n.target.id == "step")
        transformed = transform_train(SOURCE)
        after = next(n for n in transformed.body
                     if isinstance(n, ast.For) and n.target.id == "step")
        self.assertTrue(ctl_call(after.body[0], {"before"}))
        self.assertTrue(ctl_call(after.body[-1], {"after"}))
        self.assertEqual([dumps(n) for n in before.body],
                         [dumps(n) for n in after.body[1:-1]])

    def test_diagnostic_adds_regions_without_math_changes(self):
        off = transform_train(SOURCE)
        diag = StripRegions().visit(transform_train(SOURCE, True))
        self.assertEqual(dumps(off), dumps(diag))

    def test_gpu_diagnostic_preserves_original_math(self):
        original = original_method("gpu_forward_backward")
        original.name = "q1_gpu_forward_backward"
        transformed = StripRegions().visit(transform_gpu(SOURCE))
        self.assertEqual(dumps(original), dumps(transformed))

    def test_fifteen_cross_step_live_values_present(self):
        self.assertEqual(set(LIVE_KEYS), {
            "is_densify", "counter", "valid_ids", "valid_ids_cpu",
            "valid_ids_cpu_prev", "camtoworlds", "Ks", "pixels", "image_ids",
            "masks", "height", "width", "opacities", "colors0", "colorsN"})
        transformed = transform_train(SOURCE)
        restored = {
            n.targets[0].id for n in ast.walk(transformed)
            if isinstance(n, ast.Assign) and len(n.targets) == 1
            and isinstance(n.targets[0], ast.Name)
            and isinstance(n.value, ast.Subscript)
            and isinstance(n.value.value, ast.Attribute)
            and n.value.value.attr == "resume_live"}
        self.assertEqual(set(LIVE_KEYS), restored)

    def test_resume_does_not_reexecute_prologue_or_zero_pending_grads(self):
        transformed = transform_train(SOURCE)
        branches = [n for n in transformed.body if isinstance(n, ast.If)
                    and dumps(n.test) == dumps(ast.parse(
                        "not _q1_ctl.resuming", mode="eval").body)]
        self.assertEqual(4, len(branches))
        original = original_method("train")
        expected = [n for n in original.body
                    if 1006 <= getattr(n, "lineno", 0) <= 1009]
        self.assertEqual([dumps(n) for n in expected],
                         [dumps(n) for n in branches[-1].body])
        self.assertEqual([], branches[0].orelse)
        self.assertEqual([], branches[1].orelse)
        self.assertEqual([], branches[2].orelse)

    def test_original_scheduler_math_retained(self):
        original = original_method("train")
        transformed = transform_train(SOURCE)
        def scheduler(fn):
            return next(n for n in fn.body if isinstance(n, ast.Assign)
                        and any(isinstance(t, ast.Name) and t.id == "schedulers"
                                for t in n.targets))
        self.assertEqual(dumps(scheduler(original)), dumps(scheduler(transformed)))

    def test_worker_binds_frozen_source_hash_before_import(self):
        text = (TOOL / "worker.py").read_text()
        self.assertIn(EXPECTED, text)
        self.assertLess(text.index('assert source_sha=='),
                        text.index('spec.loader.exec_module(mod)'))

    def test_worker_preforks_loader_before_loading_large_state(self):
        module = ast.parse((TOOL / "worker.py").read_text())
        function = next(n for n in module.body
                        if isinstance(n, ast.FunctionDef) and n.name == "restore_runner")
        calls = [n for n in ast.walk(function) if isinstance(n, ast.Call)]
        init = next(n.lineno for n in calls if isinstance(n.func, ast.Name)
                    and n.func.id == "iter")
        load = next(n.lineno for n in calls if isinstance(n.func, ast.Name)
                    and n.func.id == "load_state")
        self.assertLess(init, load)

    def test_worker_manifest_filename_agrees_with_store(self):
        worker = (TOOL / "worker.py").read_text()
        store = (TOOL / "state_store.py").read_text()
        self.assertIn('"MANIFEST.json"', store)
        self.assertNotIn('"manifest.json"', worker)
        self.assertIn('"MANIFEST.json"', worker)


if __name__ == "__main__":
    unittest.main(verbosity=2)
