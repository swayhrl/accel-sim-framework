"""CPU-only tests: no CUDA/NVML calls or shared GPU lock access."""
import copy
import json
import os
from pathlib import Path
import random
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
import torch

import state_store as ss


class StateStoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="q1-state-store-cpu-")
        self.base = Path(self.tmp.name)
        self.directory = self.base / "state"

    def tearDown(self):
        self.tmp.cleanup()

    def roundtrip(self, bundle, **kwargs):
        manifest = ss.save_state(bundle, self.directory, chunk_bytes=13, **kwargs)
        loaded, actual = ss.load_state(self.directory, map_device="cpu")
        self.assertEqual(manifest, actual)
        return loaded, manifest

    def test_semantic_immutable_python_memo_is_not_numeric_identity(self):
        text="a-long-noninterned-source-value"
        same=text.encode().decode()
        a={"fields":[text,text],"t":torch.arange(3)}
        b={"fields":[text,same],"t":a["t"]}
        self.assertEqual(ss.semantic_fingerprint(a),ss.semantic_fingerprint(b))
        self.assertNotEqual(ss.fingerprint(a),ss.fingerprint(b))

    def test_semantic_mutable_alias_is_significant(self):
        shared=[1,2]
        self.assertNotEqual(ss.semantic_fingerprint([shared,shared]),
                            ss.semantic_fingerprint([[1,2],[1,2]]))

    def test_semantic_roundtrip_bits_alias_and_rng(self):
        base=torch.tensor([0,-2147483648,2143289345],dtype=torch.int32)
        bundle={"a":base,"v":base.view(torch.float32),"rng":np.random.RandomState(9).get_state()}
        expected=ss.semantic_fingerprint(bundle)
        restored,_=self.roundtrip(bundle)
        self.assertEqual(expected,ss.semantic_fingerprint(restored))
        restored["a"][0]=1
        self.assertNotEqual(expected,ss.semantic_fingerprint(restored))

    def test_raw_nan_signedzero_and_inf_bytes(self):
        words = torch.tensor([0, -2147483648, 2143289345, 2143289346,
                              2139095040, -8388608], dtype=torch.int32)
        original = words.view(torch.float32)
        restored, _ = self.roundtrip(original)
        self.assertTrue(torch.equal(original.view(torch.int32), restored.view(torch.int32)))

    def test_views_strides_offsets_and_aliases(self):
        base = torch.arange(40, dtype=torch.float32).reshape(5, 8)
        view = base[1:, 1::2].t()
        out, _ = self.roundtrip({"base": base, "view": view})
        self.assertEqual(tuple(out["view"].stride()), tuple(view.stride()))
        self.assertEqual(out["view"].storage_offset(), view.storage_offset())
        self.assertTrue(torch.equal(out["view"], view))
        self.assertEqual(out["base"].untyped_storage()._cdata,
                         out["view"].untyped_storage()._cdata)
        out["base"][1, 1] = 999
        self.assertEqual(out["view"][0, 0].item(), 999)

    def test_mixed_dtype_storage_alias(self):
        base = torch.arange(32, dtype=torch.uint8)
        out, manifest = self.roundtrip([base, base.view(torch.int32)])
        self.assertEqual(len(manifest["storages"]), 1)
        self.assertEqual(out[0].untyped_storage()._cdata, out[1].untyped_storage()._cdata)
        self.assertTrue(torch.equal(out[1], base.view(torch.int32)))

    def test_tensor_object_repeated_reference(self):
        value = torch.ones(3)
        out, _ = self.roundtrip({"x": value, "nested": (value, [value])})
        self.assertIs(out["x"], out["nested"][0])
        self.assertIs(out["x"], out["nested"][1][0])

    def test_parameter_and_explicit_gradient(self):
        param = torch.nn.Parameter(torch.arange(6, dtype=torch.float64))
        param.grad = torch.arange(6, dtype=torch.float64) + 2
        out, manifest = self.roundtrip({"param": param, "grad": param.grad, "again": param})
        self.assertIsInstance(out["param"], torch.nn.Parameter)
        self.assertIs(out["param"], out["again"])
        self.assertTrue(out["param"].requires_grad)
        self.assertIsNone(out["param"].grad)
        self.assertTrue(torch.equal(out["grad"], param.grad))
        self.assertTrue(manifest["tensors"][0]["attached_grad_requires_explicit_bundle_field"])
        out["param"].grad = out["grad"]
        self.assertTrue(torch.equal(out["param"].grad, param.grad))

    def test_tensor_requires_grad_and_device(self):
        value = torch.arange(8, dtype=torch.float32, requires_grad=True)
        out, manifest = self.roundtrip(value[1::2])
        self.assertTrue(out.requires_grad)
        self.assertEqual(str(out.device), "cpu")
        self.assertEqual(manifest["tensors"][0]["device"], "cpu")
        self.assertFalse(out.is_pinned())

    def test_nested_numpy_rng_and_scalars(self):
        rng = np.random.RandomState(7)
        original = {
            "tuple": (None, True, 7, -2.5, "text", b"bytes"),
            "rng": rng.get_state(), "python_rng": random.getstate(),
            "array": np.array([1, 3, 8], dtype=np.uint32),
            "nested": [{"t": torch.tensor(2, dtype=torch.int64)}],
        }
        out, _ = self.roundtrip(original)
        self.assertEqual(out["tuple"], original["tuple"])
        self.assertEqual(out["rng"][0], original["rng"][0])
        self.assertTrue(np.array_equal(out["rng"][1], original["rng"][1]))
        self.assertEqual(out["rng"][2:], original["rng"][2:])
        self.assertEqual(out["python_rng"], original["python_rng"])
        self.assertTrue(np.array_equal(out["array"], original["array"]))

    def test_empty_tensor_zero_storage(self):
        out, manifest = self.roundtrip(torch.empty((0, 4)))
        self.assertEqual(tuple(out.shape), (0, 4))
        self.assertEqual(manifest["total_storage_bytes"], 0)
        self.assertEqual(manifest["storages"][0]["chunks"], [])

    def test_scalar_tensor(self):
        out, _ = self.roundtrip(torch.tensor(17.0))
        self.assertEqual(out.shape, torch.Size([]))
        self.assertEqual(out.item(), 17)

    def test_empty_view_retains_nonempty_storage(self):
        source = torch.arange(20)[12:12]
        out, manifest = self.roundtrip(source)
        self.assertEqual(out.storage_offset(), 12)
        self.assertEqual(manifest["total_storage_bytes"], 20 * 8)

    def test_chunk_bound_and_hashes(self):
        _, manifest = self.roundtrip(torch.arange(43, dtype=torch.uint8))
        chunks = manifest["storages"][0]["chunks"]
        self.assertEqual([c["nbytes"] for c in chunks], [13, 13, 13, 4])
        for chunk in chunks:
            self.assertEqual(ss._sha(self.directory / chunk["name"]), chunk["sha256"])

    def test_corrupt_chunk_rejected_before_unpickle(self):
        _, manifest = self.roundtrip(torch.arange(20))
        path = self.directory / manifest["storages"][0]["chunks"][0]["name"]
        raw = bytearray(path.read_bytes())
        raw[0] ^= 1
        path.write_bytes(raw)
        with patch.object(ss._Decoder, "load", side_effect=AssertionError("must not unpickle")):
            with self.assertRaisesRegex(ss.StateStoreError, "integrity"):
                ss.load_state(self.directory)

    def test_missing_chunk_rejected(self):
        _, manifest = self.roundtrip(torch.arange(20))
        (self.directory / manifest["storages"][0]["chunks"][0]["name"]).unlink()
        with self.assertRaises(FileNotFoundError):
            ss.load_state(self.directory)

    def test_metadata_hash_rejected(self):
        self.roundtrip({"test": torch.ones(2)})
        path = self.directory / "bundle.pkl"
        path.write_bytes(path.read_bytes() + b"x")
        with self.assertRaisesRegex(ss.StateStoreError, "metadata integrity"):
            ss.load_state(self.directory)

    def test_incomplete_directory_rejected(self):
        self.directory.mkdir()
        (self.directory / "bundle.pkl").write_bytes(b"unfinished")
        with self.assertRaises(FileNotFoundError):
            ss.load_state(self.directory)

    def test_incomplete_manifest_rejected(self):
        self.roundtrip(torch.ones(2))
        path = self.directory / "MANIFEST.json"
        data = json.loads(path.read_text())
        data["complete"] = False
        path.write_text(json.dumps(data))
        with self.assertRaisesRegex(ss.StateStoreError, "incomplete"):
            ss.load_state(self.directory)

    def test_save_size_cap_before_publication(self):
        with self.assertRaisesRegex(ss.StateStoreError, "size cap"):
            ss.save_state(torch.ones(100), self.directory, max_bytes=100)
        self.assertFalse(self.directory.exists())

    def test_load_size_cap(self):
        self.roundtrip(torch.ones(100))
        with self.assertRaisesRegex(ss.StateStoreError, "size cap"):
            ss.load_state(self.directory, max_bytes=100)

    def test_atomic_failure_does_not_publish(self):
        original = ss._write_bytes
        writes = [0]
        def fail_second(path, data):
            writes[0] += 1
            if writes[0] == 2:
                raise OSError("injected disk failure")
            return original(path, data)
        with patch.object(ss, "_write_bytes", side_effect=fail_second):
            with self.assertRaisesRegex(OSError, "injected"):
                ss.save_state(torch.arange(30), self.directory, chunk_bytes=13)
        self.assertFalse(self.directory.exists())
        remnants = list(self.base.glob(".state.incomplete-*"))
        self.assertEqual(len(remnants), 1)
        self.assertTrue((remnants[0] / "INCOMPLETE_ERROR.txt").is_file())
        self.assertFalse((remnants[0] / "MANIFEST.json").exists())

    def test_existing_target_never_overwritten(self):
        self.directory.mkdir()
        marker = self.directory / "marker"
        marker.write_text("original")
        with self.assertRaises(FileExistsError):
            ss.save_state(torch.ones(1), self.directory)
        self.assertEqual(marker.read_text(), "original")

    def test_publication_race_does_not_replace_empty_directory(self):
        source = self.base / "source"
        target = self.base / "target"
        source.mkdir()
        target.mkdir()
        with self.assertRaises(FileExistsError):
            ss._publish_no_replace(source, target)
        self.assertTrue(source.is_dir())
        self.assertTrue(target.is_dir())

    def test_fingerprint_preserves_raw_content_alias_and_layout(self):
        value = torch.arange(24, dtype=torch.float32).reshape(4, 6)
        bundle = [value, value[:, 1::2], value]
        initial = ss.fingerprint(bundle, chunk_bytes=13)
        out, _ = self.roundtrip(bundle)
        self.assertEqual(ss.fingerprint(out, chunk_bytes=13), initial)
        out[0][0, 0] = 123
        self.assertNotEqual(ss.fingerprint(out, chunk_bytes=13), initial)

    def test_invalid_chunk_bounds(self):
        for count in [0, -1, ss.MAX_CHUNK_BYTES + 1]:
            with self.assertRaises(ValueError):
                ss.save_state(torch.ones(1), self.directory, chunk_bytes=count)

    def test_sparse_tensor_rejected_explicitly(self):
        sparse = torch.sparse_coo_tensor(torch.tensor([[0]]), torch.tensor([1.]), (2,))
        with self.assertRaisesRegex(ss.StateStoreError, "unsupported tensor"):
            ss.save_state(sparse, self.directory)

    def test_numpy_and_torch_rng_replay(self):
        np_rng = np.random.RandomState(31)
        torch_rng = torch.Generator(device="cpu").manual_seed(41)
        bundle = {"numpy": np_rng.get_state(), "torch": torch_rng.get_state()}
        out, _ = self.roundtrip(bundle)
        restored_np = np.random.RandomState()
        restored_np.set_state(out["numpy"])
        restored_torch = torch.Generator(device="cpu")
        restored_torch.set_state(out["torch"])
        self.assertTrue(np.array_equal(np_rng.rand(12), restored_np.rand(12)))
        self.assertTrue(torch.equal(torch.rand(12, generator=torch_rng),
                                    torch.rand(12, generator=restored_torch)))

    def test_bfloat16_float16_and_bool(self):
        bundle = [torch.arange(8, dtype=torch.bfloat16),
                  torch.arange(8, dtype=torch.float16),
                  torch.tensor([True, False])]
        out, _ = self.roundtrip(bundle)
        for original, restored in zip(bundle, out):
            self.assertEqual(original.dtype, restored.dtype)
            self.assertTrue(torch.equal(original, restored))

    def test_symlink_chunk_rejected(self):
        _, manifest = self.roundtrip(torch.ones(2))
        path = self.directory / manifest["storages"][0]["chunks"][0]["name"]
        moved = self.base / "other"
        path.rename(moved)
        path.symlink_to(moved)
        with self.assertRaisesRegex(ss.StateStoreError, "regular file"):
            ss.load_state(self.directory)


if __name__ == "__main__":
    unittest.main(verbosity=2)
