"""Read-only stdlib checkpoint manifest and token-metadata inspection.

Never imports Torch, restores device storage, or invokes CUDA/NVML.
Finite checking optionally imports CPU NumPy after metadata identity validation.
Only trusted self-produced pickle metadata with verified hash is decoded;
all persistent tensors become non-allocating identity-preserving TensorTokens.
"""
import hashlib
import io
import json
import os
from pathlib import Path
import pickle
import time

SOURCE_SHA = "17e70b6466f7e33a24d1610aa7deb69316cd177dc2c212cd8b717b9884f4808a"
LIVE = {"is_densify", "counter", "valid_ids", "valid_ids_cpu",
        "valid_ids_cpu_prev", "camtoworlds", "Ks", "pixels", "image_ids",
        "masks", "height", "width", "opacities", "colors0", "colorsN"}


class TensorToken:
    def __init__(self, index, row):
        self.index, self.row = index, row


class NumpyDtypeToken:
    def __init__(self, *args):
        self.args, self.state = args, None

    def __setstate__(self, state):
        self.state = state


class NumpyValueToken:
    def __init__(self, kind, *args):
        self.kind, self.args = kind, args


def numpy_scalar(*args):
    return NumpyValueToken("scalar", *args)


def numpy_frombuffer(*args):
    return NumpyValueToken("array_frombuffer", *args)


class MetadataOnly(pickle.Unpickler):
    def __init__(self, data, manifest):
        super().__init__(io.BytesIO(data))
        self.manifest, self.cache = manifest, {}

    def find_class(self, module, name):
        allowed = {
            ("numpy", "dtype"): NumpyDtypeToken,
            ("numpy.core.multiarray", "scalar"): numpy_scalar,
            ("numpy.core.numeric", "_frombuffer"): numpy_frombuffer,
        }
        if (module, name) not in allowed:
            raise ValueError("PICKLE_GLOBAL_NOT_ALLOWED:" + module + "." + name)
        return allowed[module, name]

    def persistent_load(self, pid):
        if (not isinstance(pid, tuple) or len(pid) != 2
                or pid[0] != "Q1_TENSOR" or type(pid[1]) is not int
                or not 0 <= pid[1] < len(self.manifest["tensors"])):
            raise ValueError("INVALID_TENSOR_TOKEN")
        index = pid[1]
        if index not in self.cache:
            self.cache[index] = TensorToken(index, self.manifest["tensors"][index])
        return self.cache[index]


def sha(path):
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        for data in iter(lambda: stream.read(4 * 1024 ** 2), b""):
            hasher.update(data)
    return hasher.hexdigest()


def member(directory, name):
    if not isinstance(name, str) or Path(name).name != name:
        raise ValueError("INVALID_MANIFEST_MEMBER")
    path = directory / name
    if path.is_symlink() or not path.is_file():
        raise ValueError("NONREGULAR_MANIFEST_MEMBER")
    return path


def summary(value):
    if isinstance(value, TensorToken):
        return dict(token=value.index, **value.row)
    if isinstance(value, NumpyDtypeToken):
        return {"numpy_dtype_token": [summary(x) for x in value.args],
                "dtype_state": summary(value.state)}
    if isinstance(value, NumpyValueToken):
        return {"numpy_value_token": value.kind,
                "arguments": [summary(x) for x in value.args]}
    if isinstance(value, (bytes, bytearray)):
        return {"bytes": len(value), "sha256": hashlib.sha256(value).hexdigest()}
    if isinstance(value, dict):
        return {str(k): summary(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [summary(x) for x in value]
    return value


def finite_storage_checks(directory, manifest, bundle):
    # Optional CPU NumPy only. No device storages or Tensor objects are created.
    import numpy as np
    dtype_map = {"torch.float16": np.dtype("<f2"),
                 "torch.float32": np.dtype("<f4"),
                 "torch.float64": np.dtype("<f8")}
    requested = {}
    for name, token in bundle["parameter_grads"].items():
        if token is not None:
            requested["parameter_grads." + name] = token
    for name, token in bundle["live"].items():
        if isinstance(token, TensorToken) and token.row["dtype"] in dtype_map:
            requested["live." + name] = token
    reports = {}
    storage_results = {}
    for name, token in requested.items():
        row = token.row
        storage = manifest["storages"][row["storage"]]
        dtype = dtype_map.get(row["dtype"])
        shape, stride = row["shape"], row["stride"]
        numel = 1
        for value in shape:
            numel *= value
        # A strided view covers a dense whole storage when non-unit dimensions
        # have strides 1, extent0, extent0*extent1... in increasing-stride order.
        expected = 1
        dense = True
        for step, extent in sorted((s, n) for s, n in zip(stride, shape) if n > 1):
            if step != expected:
                dense = False
            expected *= extent
        coverage = (dtype is not None and row["offset"] == 0 and dense
                    and numel * dtype.itemsize == storage["nbytes"])
        if not coverage:
            reports[name] = {
                "status": "NOT_CHECKED_VIEW_COVERAGE_OR_DTYPE_NOT_QUALIFIED",
                "token": token.index, "storage": row["storage"],
                "dtype": row["dtype"], "shape": shape, "stride": stride,
            }
            continue
        sid = row["storage"]
        if sid not in storage_results:
            count = nan = positive_inf = negative_inf = 0
            for chunk in storage["chunks"]:
                assert chunk["offset"] % dtype.itemsize == 0
                assert chunk["nbytes"] % dtype.itemsize == 0
                with member(directory, chunk["name"]).open("rb") as stream:
                    while True:
                        payload = stream.read(4 * 1024**2)
                        if not payload:
                            break
                        assert len(payload) % dtype.itemsize == 0
                        values = np.frombuffer(payload, dtype=dtype)
                        count += int(values.size)
                        nan += int(np.count_nonzero(np.isnan(values)))
                        positive_inf += int(np.count_nonzero(np.isposinf(values)))
                        negative_inf += int(np.count_nonzero(np.isneginf(values)))
            assert count == numel
            storage_results[sid] = {
                "status": "RAW_STORAGE_FINITE_NOT_GPU_RESTORE",
                "all_finite": nan + positive_inf + negative_inf == 0,
                "values_checked": count, "nan_count": nan,
                "positive_inf_count": positive_inf,
                "negative_inf_count": negative_inf,
                "storage": sid, "dtype": row["dtype"],
                "coverage": "EXACT_DENSE_FULL_STORAGE_NO_PADDING",
            }
        reports[name] = dict(storage_results[sid], token=token.index,
                             shape=shape, stride=stride)
    return {
        "method": "CPU_NUMPY_FROMBUFFER_STREAM_4MIB",
        "scope": "REAL_EARLY_PENDING_GRADS_AND_FLOAT_LIVE_OPERANDS",
        "torch_imported": False, "gpu_restore_qualified": False,
        "requested_tensor_count": len(requested),
        "checked_unique_storage_count": len(storage_results),
        "all_checked_storages_finite": all(
            row["all_finite"] for row in storage_results.values()),
        "all_requested_views_checked": len(reports) == len(requested) and all(
            row["status"] == "RAW_STORAGE_FINITE_NOT_GPU_RESTORE"
            for row in reports.values()),
        "per_tensor": reports,
    }


def inspect(directory, out):
    start = time.monotonic()
    directory = directory.resolve()
    manifest_path = member(directory, "MANIFEST.json")
    manifest = json.loads(manifest_path.read_text())
    assert manifest["schema"] == "AIARCH_Q1_CHUNKED_STATE_V1"
    assert manifest["complete"] is True
    metadata_path = member(directory, "bundle.pkl")
    assert metadata_path.stat().st_size == manifest["metadata_bytes"]
    assert sha(metadata_path) == manifest["metadata_sha256"]
    checked = []
    total = 0
    for index, storage in enumerate(manifest["storages"]):
        offset = 0
        for chunk in storage["chunks"]:
            assert chunk["offset"] == offset
            path = member(directory, chunk["name"])
            assert path.stat().st_size == chunk["nbytes"]
            actual = sha(path)
            assert actual == chunk["sha256"]
            checked.append(dict(name=chunk["name"], nbytes=chunk["nbytes"],
                                sha256=actual, storage=index, offset=offset))
            offset += chunk["nbytes"]
        assert offset == storage["nbytes"]
        total += offset
    assert total == manifest["total_storage_bytes"]
    side_path = directory.with_suffix(".sidecar.json")
    owner_path = directory.with_suffix(".owner.json")
    public_path = out / "raw" / ("STATE_" + directory.name + "_MANIFEST.json")
    side, owner, public = [json.loads(p.read_text())
                           for p in [side_path, owner_path, public_path]]
    manifest_hash = sha(manifest_path)
    assert side["manifest_sha256"] == manifest_hash
    assert public["manifest_sha256"] == manifest_hash
    assert public["manifest"] == manifest
    assert side["state_fingerprint"] == public["state_fingerprint"]
    assert side["next_step"] == public["next_step"]
    bundle = MetadataOnly(metadata_path.read_bytes(), manifest).load()
    assert bundle["schema"] == "Q1_FULL_PIPELINE_STATE_V1"
    assert bundle["source_sha256"] == side["source_sha256"] == SOURCE_SHA
    assert bundle["next_step"] == side["next_step"]
    assert bundle["current_camera_ids"] == side["current_camera_ids"]
    assert bundle["current_camera_ids"] == public["current_camera_ids"]
    assert set(bundle["live"]) == LIVE
    assert bundle["loader"]["epoch_indices"] == side["loader"]["epoch_indices"]
    for key in ["epoch", "consumed_samples", "consumed_batches", "dataset_digest",
                "base_seed", "batch_size", "num_workers", "persistent_workers",
                "pin_memory"]:
        assert bundle["loader"][key] == side["loader"][key]
    assert set(bundle["rng"]) == {"python", "numpy", "torch_cpu", "torch_cuda"}
    assert set(bundle["parameter_grads"]) == set(bundle["parameters"])
    assert bundle["live"]["counter"].row["dtype"] == "torch.int8"
    assert bundle["loader"]["num_workers"] == 4
    assert bundle["loader"]["deterministic_dataset_required"] is True
    parameter_rows = {}
    optimizer_rows = {}
    for name, param in bundle["parameters"].items():
        assert isinstance(param, TensorToken) and param.row["parameter"]
        grad = bundle["parameter_grads"][name]
        if grad is not None:
            assert isinstance(grad, TensorToken)
            assert grad.row["shape"] == param.row["shape"]
        parameter_rows[name] = {"parameter": summary(param), "grad": summary(grad)}
    for kind, optimizers in bundle["optimizers"].items():
        optimizer_rows[kind] = {}
        for name, opt in optimizers.items():
            state = opt["state_dict"]
            assert len(state["param_groups"]) == 1
            assert len(state["param_groups"][0]["params"]) == 1
            assert len(state["state"]) == 1
            values = next(iter(state["state"].values()))
            assert {"step", "exp_avg", "exp_avg_sq"} <= set(values)
            shape = bundle["parameters"][name].row["shape"]
            assert values["exp_avg"].row["shape"] == shape
            assert values["exp_avg_sq"].row["shape"] == shape
            optimizer_rows[kind][name] = {
                "keys": sorted(values), "state": summary(values),
                "param_groups": summary(state["param_groups"]),
                "extra_keys": sorted(opt["extra"]),
            }
    refs = {}
    for index, tensor in enumerate(manifest["tensors"]):
        refs.setdefault(tensor["storage"], []).append(index)
        assert 0 <= tensor["storage"] < len(manifest["storages"])
        assert len(tensor["shape"]) == len(tensor["stride"])
    actual_bytes = sum(p.stat().st_size for p in directory.iterdir() if p.is_file())
    return {
        "name": directory.name,
        "classification": "EARLY_SELF_PRODUCED_FULL_STATE_BYTES_VERIFIED",
        "next_step": bundle["next_step"],
        "manifest_sha256": manifest_hash, "metadata_sha256": manifest["metadata_sha256"],
        "state_fingerprint_bound_to_saved_receipt": side["state_fingerprint"],
        "storage_bytes": total, "metadata_bytes": manifest["metadata_bytes"],
        "directory_file_bytes": actual_bytes,
        "sidecar_bytes": side_path.stat().st_size,
        "owner_marker_bytes": owner_path.stat().st_size,
        "chunks": checked, "storage_count": len(manifest["storages"]),
        "tensor_count": len(manifest["tensors"]),
        "storage_alias_groups": {str(k): v for k, v in refs.items() if len(v) > 1},
        "same_object_references_preserved": True,
        "parameters_and_grads": parameter_rows, "optimizers": optimizer_rows,
        "live_keys": sorted(bundle["live"]),
        "live_tensor_metadata": {k: summary(v) for k, v in bundle["live"].items()
                                 if isinstance(v, TensorToken)},
        "counter_values": "NOT_DECODED_FROM_RAW_STORAGE",
        "rng_keys": sorted(bundle["rng"]),
        "rng_metadata_summary": {
            "python_version": bundle["rng"]["python"][0],
            "python_tuple_length": len(bundle["rng"]["python"][1]),
            "numpy": summary(bundle["rng"]["numpy"]),
            "torch_cpu": summary(bundle["rng"]["torch_cpu"]),
            "torch_cuda": summary(bundle["rng"]["torch_cuda"]),
        },
        "loader": {k: summary(v) for k, v in bundle["loader"].items()
                   if k not in ["epoch_indices", "initial_base_seed_rng_state"]},
        "epoch_permutation_length": len(bundle["loader"]["epoch_indices"]),
        "epoch_permutation_sha256": hashlib.sha256(json.dumps(
            bundle["loader"]["epoch_indices"]).encode()).hexdigest(),
        "current_camera_ids": bundle["current_camera_ids"],
        "frontier": bundle["frontier"],
        "stable_ids": summary(bundle["stable_ids"]), "next_id": bundle["next_id"],
        "strategy_keys": sorted(bundle["strategy_state"]),
        "scheduler_count": len(bundle["schedulers"]),
        "owner_marker": owner,
        "elapsed_seconds": time.monotonic() - start,
        "early_snapshot_finite_checks": finite_storage_checks(directory, manifest, bundle),
        "missing_or_unverified": [
            "GPU restore and resumed training NOT_EXECUTED",
            "late-state qualification NOT_EXECUTED",
            "runtime parameter/optimizer reconstruction NOT_VERIFIED",
            "continuous-versus-restored numerical trajectory NOT_VERIFIED",
            "counter scalar range and unrelated floating-point storages not rescanned",
            "saved state fingerprint was receipt-bound, not recomputed with Torch",
        ],
    }


def static_transform_check():
    import ast
    from source_transform import transform_train, transform_gpu
    source_path = Path("/data/c16/aiarch_a26gr1_gsscale_rubble_109_20261014/software_sources/gsscale/examples/simple_trainer_hybrid_optimized.py")
    source = source_path.read_text()
    assert hashlib.sha256(source.encode()).hexdigest() == SOURCE_SHA
    cls = next(n for n in ast.parse(source).body
               if isinstance(n, ast.ClassDef) and n.name == "Runner")
    original_train = next(n for n in cls.body
                          if isinstance(n, ast.FunctionDef) and n.name == "train")
    original_loop = next(n for n in original_train.body
                         if isinstance(n, ast.For) and n.target.id == "step")
    off = transform_train(source, False)
    off_loop = next(n for n in off.body
                    if isinstance(n, ast.For) and n.target.id == "step")
    dump = lambda n: ast.dump(n, include_attributes=False)
    assert [dump(n) for n in original_loop.body] == [
        dump(n) for n in off_loop.body[1:-1]]
    class Unwrap(ast.NodeTransformer):
        def visit_Expr(self, node):
            call = node.value
            if (isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute)
                    and isinstance(call.func.value, ast.Name)
                    and call.func.value.id == "_q1_ctl"
                    and call.func.attr in {"region_begin", "region_end"}):
                return None
            return self.generic_visit(node)
        def visit_Call(self, node):
            node = self.generic_visit(node)
            if isinstance(node.func, ast.Name) and node.func.id in {"_q1_copy", "_q1_to"}:
                receiver, *args = node.args
                name = "copy_" if node.func.id == "_q1_copy" else "to"
                node.func = ast.Attribute(value=receiver, attr=name, ctx=ast.Load())
                node.args = args
            return node
    diag = Unwrap().visit(transform_train(source, True))
    assert dump(diag) == dump(off)
    original_gpu = next(n for n in cls.body
                        if isinstance(n, ast.FunctionDef)
                        and n.name == "gpu_forward_backward")
    original_gpu.name = "q1_gpu_forward_backward"
    assert dump(Unwrap().visit(transform_gpu(source))) == dump(original_gpu)
    return {
        "status": "PASS_STATIC_AST_MATH_PRESERVATION",
        "original_loop_statement_order": "EXACT_AFTER_REMOVING_CONTROL_CALLBACKS",
        "diagnostic_math": "EXACT_AFTER_UNWRAPPING_REGION_AND_TRANSFER_OBSERVERS",
        "gpu_forward_backward_math": "EXACT_AFTER_UNWRAPPING_OBSERVERS",
        "source_sha256": SOURCE_SHA,
        "source_transform_sha256": sha(Path(__file__).with_name("source_transform.py")),
        "execution_scope": "EARLY_OBSERVER_OFF_ONLY; DIAG_NOT_EXECUTED",
        "does_not_prove_runtime_or_numerical_restore": True,
    }


def main():
    os.sched_setaffinity(0, {22, 23})
    root = Path(__file__).resolve().parents[3]
    out = root / "docs/ai_workload_research/runs/AI_ARCH_Q1_CPU_HARDENING_109_V1"
    rows = [inspect(out / ".private/STATES" / name, out)
            for name in ["C_E", "C_R_E"]]
    receipt = {
        "schema": "Q1_CPU_CHECKPOINT_INSPECTION_V1",
        "method": "SHA256_RESTRICTED_PICKLE_TENSOR_TOKENS_PLUS_CPU_NUMPY_FINITE",
        "torch_imported": False, "numpy_imported": True,
        "cuda_calls": 0, "nvml_calls": 0, "lock_attempts": 0,
        "source_or_checkpoint_modified": False, "states": rows,
        "source_transform_static_check": static_transform_check(),
    }
    import sys
    assert "torch" not in sys.modules
    (out / "STATE_MANIFEST.json").write_text(json.dumps(receipt, indent=2) + "\n")
    qualification = {
        "schema": "Q1_RESTORE_QUALIFICATION_V1",
        "state_byte_integrity": "PASS",
        "metadata_and_receipt_binding": "PASS",
        "complete_state_capture_structure": "PRESENT_AT_EARLY_FRONTIER_ONLY",
        "gpu_restore": "NOT_EXECUTED",
        "early_snapshot_finite_checks": {row["name"]: row["early_snapshot_finite_checks"] for row in rows},
        "actual_runner_reconstruction": "NOT_EXECUTED",
        "same_state_resumed_numeric_qualification": "NOT_EXECUTED",
        "late_state": "NOT_ACQUIRED",
        "late_thread_formal_comparison": "NOT_EXECUTED",
        "critical_path_diagnostic": "NOT_EXECUTED",
        "independent_validation": "NOT_EXECUTED",
        "restoration_scientific_pass": False,
        "reason": "GPU window ended after early state capture; no resumed worker or late training",
        "checkpoints": [{"name": row["name"], "next_step": row["next_step"],
                         "storage_bytes": row["storage_bytes"],
                         "manifest_sha256": row["manifest_sha256"]}
                        for row in rows],
        "scope": "Byte integrity and metadata coverage do not prove numerical restore correctness",
    }
    (out / "RESTORE_QUALIFICATION.json").write_text(
        json.dumps(qualification, indent=2) + "\n")
    print(json.dumps({"states": [{"name": r["name"], "storage_bytes":
                                 r["storage_bytes"], "next_step": r["next_step"]}
                                for r in rows],
                      "gpu_restore": "NOT_EXECUTED"}))


if __name__ == "__main__":
    main()
