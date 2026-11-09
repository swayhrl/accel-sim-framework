"""Exact, chunked checkpoint store for the Q1 isolated experiment.

Only load trusted self-produced bundles. SHA verification detects corruption; it
does not make Python pickle safe for untrusted files. Gradients are NOT inferred:
the runner must include parameter.grad and all deferred state explicitly.
"""
from __future__ import annotations

import ctypes
import hashlib
import io
import json
import os
from pathlib import Path
import pickle
import stat
import uuid

import torch

SCHEMA = "AIARCH_Q1_CHUNKED_STATE_V1"
DEFAULT_CHUNK_BYTES = 64 * 1024**2
MAX_CHUNK_BYTES = 256 * 1024**2
DEFAULT_MAX_BYTES = 28 * 1024**3


class StateStoreError(RuntimeError):
    pass


def _sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for part in iter(lambda: f.read(4 * 1024**2), b""):
            h.update(part)
    return h.hexdigest()


def _fsync_dir(path):
    fd = os.open(str(path), os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _publish_no_replace(source, target):
    # Linux renameat2 is atomic and cannot replace even an empty target directory.
    libc = ctypes.CDLL(None, use_errno=True)
    rename = getattr(libc, "renameat2", None)
    if rename is None:
        raise StateStoreError("atomic no-replace publication unavailable")
    rename.argtypes = [ctypes.c_int, ctypes.c_char_p,
                       ctypes.c_int, ctypes.c_char_p, ctypes.c_uint]
    rename.restype = ctypes.c_int
    if rename(-100, os.fsencode(source), -100, os.fsencode(target), 1) != 0:
        err = ctypes.get_errno()
        raise OSError(err, os.strerror(err), str(target))


def _write_bytes(path, data):
    with open(path, "xb") as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())


def _safe_member(directory, name):
    if not isinstance(name, str) or Path(name).name != name:
        raise StateStoreError("invalid checkpoint member")
    path = directory / name
    info = path.lstat()
    if not stat.S_ISREG(info.st_mode):
        raise StateStoreError("checkpoint member is not a regular file")
    return path


class _Encoder(pickle.Pickler):
    def __init__(self, stream):
        super().__init__(stream, protocol=5)
        self.tensors = []
        self.storages = []
        self._tensor_ids = {}
        self._storage_ids = {}
        self._refs = []  # Prevent temporary tensor/storage identities being reused.

    def persistent_id(self, obj):
        if not isinstance(obj, torch.Tensor):
            if isinstance(obj, (torch.UntypedStorage, torch.storage.TypedStorage)):
                raise StateStoreError("bare storage must be represented by a tensor")
            return None
        key = id(obj)
        if key in self._tensor_ids:
            return ("Q1_TENSOR", self._tensor_ids[key])
        if obj.layout != torch.strided or obj.is_quantized or obj.device.type == "meta":
            raise StateStoreError("unsupported tensor layout/quantization/meta device")
        if obj.is_conj() or obj.is_neg():
            raise StateStoreError("conjugate/negative tensor bits require explicit resolution")
        if type(obj) not in (torch.Tensor, torch.nn.Parameter):
            raise StateStoreError("unsupported tensor subclass: " + str(type(obj)))
        storage = obj.untyped_storage()
        storage_key = (str(storage.device), int(storage._cdata))
        if storage_key not in self._storage_ids:
            sid = len(self.storages)
            self._storage_ids[storage_key] = sid
            self.storages.append({
                "storage": storage,
                "nbytes": int(storage.nbytes()),
                "device": str(storage.device),
                "pinned": bool(obj.is_pinned()) if obj.device.type == "cpu" else False,
            })
            self._refs.append(storage)
        sid = self._storage_ids[storage_key]
        tid = len(self.tensors)
        self._tensor_ids[key] = tid
        self._refs.append(obj)
        self.tensors.append({
            "storage": sid, "dtype": str(obj.dtype), "shape": list(obj.shape),
            "stride": list(obj.stride()), "offset": int(obj.storage_offset()),
            "requires_grad": bool(obj.requires_grad),
            "parameter": isinstance(obj, torch.nn.Parameter),
            "device": str(obj.device),
            "pinned": bool(obj.is_pinned()) if obj.device.type == "cpu" else False,
            "attached_grad_requires_explicit_bundle_field": obj.grad is not None
                if obj.is_leaf else False,
        })
        return ("Q1_TENSOR", tid)


def save_state(bundle, directory, *, chunk_bytes=DEFAULT_CHUNK_BYTES,
               max_bytes=DEFAULT_MAX_BYTES):
    """Save raw storage bytes once, with tensor aliases and object references.

    Staging is one chunk CPU tensor plus bounded hash buffers (no torch.save of
    GPU storage). Device-to-host copy is blocking; caller must quiesce concurrent
    mutation and drain its training streams before calling this function.
    A failed save retains a clearly named incomplete directory and no final dir.
    """
    directory = Path(directory).absolute()
    if directory.exists():
        raise FileExistsError(str(directory))
    if not 0 < chunk_bytes <= MAX_CHUNK_BYTES:
        raise ValueError("chunk_bytes must be in (0,256MiB]")
    if max_bytes <= 0:
        raise ValueError("max_bytes must be positive")
    directory.parent.mkdir(parents=True, exist_ok=True)
    stream = io.BytesIO()
    encoder = _Encoder(stream)
    encoder.dump(bundle)
    metadata = stream.getvalue()
    total_storage = sum(s["nbytes"] for s in encoder.storages)
    if total_storage + len(metadata) > max_bytes:
        raise StateStoreError("checkpoint size cap exceeded")
    # Non-tensor bundle metadata is expected to be small. Enforce rather than
    # allowing hidden numpy payloads to defeat the bounded staging contract.
    if len(metadata) > 64 * 1024**2:
        raise StateStoreError("non-tensor metadata exceeds 64MiB")
    temp = directory.parent / ("." + directory.name + ".incomplete-" + uuid.uuid4().hex)
    temp.mkdir(mode=0o700)
    manifest = {
        "schema": SCHEMA, "complete": True,
        "chunk_bytes": chunk_bytes, "total_storage_bytes": total_storage,
        "metadata_bytes": len(metadata), "max_bytes": max_bytes,
        "tensors": encoder.tensors, "storages": [],
        "grad_policy": "parameter.grad must be included explicitly in bundle",
        "trust_policy": "trusted self-produced pickle only; hashes are integrity checks",
    }
    try:
        _write_bytes(temp / "bundle.pkl", metadata)
        manifest["metadata_sha256"] = hashlib.sha256(metadata).hexdigest()
        for sid, source in enumerate(encoder.storages):
            row = {k: v for k, v in source.items() if k != "storage"}
            row["chunks"] = []
            flat = torch.empty(0, dtype=torch.uint8, device=source["device"])
            flat.set_(source["storage"], 0, (source["nbytes"],), (1,))
            for offset in range(0, source["nbytes"], chunk_bytes):
                count = min(chunk_bytes, source["nbytes"] - offset)
                part = flat.narrow(0, offset, count).detach()
                cpu = part.to(device="cpu", non_blocking=False)
                # memoryview avoids a second chunk-sized Python bytes object.
                payload = memoryview(cpu.numpy())
                name = "storage-%06d-offset-%020d.bin" % (sid, offset)
                _write_bytes(temp / name, payload)
                row["chunks"].append({
                    "name": name, "offset": offset, "nbytes": count,
                    "sha256": hashlib.sha256(payload).hexdigest(),
                })
                del payload, cpu, part
            manifest["storages"].append(row)
            del flat
        encoded = json.dumps(manifest, sort_keys=True, indent=2).encode("utf-8")
        if total_storage + len(metadata) + len(encoded) + 1 > max_bytes:
            raise StateStoreError("checkpoint size cap including manifest exceeded")
        _write_bytes(temp / "MANIFEST.json", encoded + b"\n")
        _fsync_dir(temp)
        _publish_no_replace(temp, directory)
        _fsync_dir(directory.parent)
        return manifest
    except BaseException as exc:
        # No false complete publication; retain failure reason for audit.
        try:
            _write_bytes(temp / "INCOMPLETE_ERROR.txt",
                         (type(exc).__name__ + ": " + str(exc) + "\n").encode())
            _fsync_dir(temp)
        except Exception:
            pass
        raise


class _Decoder(pickle.Unpickler):
    def __init__(self, stream, manifest, bases):
        super().__init__(stream)
        self.manifest = manifest
        self.bases = bases
        self.cache = {}

    def persistent_load(self, pid):
        if (not isinstance(pid, tuple) or len(pid) != 2 or
                pid[0] != "Q1_TENSOR" or not isinstance(pid[1], int)):
            raise StateStoreError("invalid persistent tensor identifier")
        idx = pid[1]
        if idx in self.cache:
            return self.cache[idx]
        if idx < 0 or idx >= len(self.manifest["tensors"]):
            raise StateStoreError("tensor identifier out of range")
        row = self.manifest["tensors"][idx]
        dtype = getattr(torch, row["dtype"].removeprefix("torch."), None)
        if not isinstance(dtype, torch.dtype):
            raise StateStoreError("unknown tensor dtype")
        base = self.bases[row["storage"]]
        value = torch.empty(0, dtype=dtype, device=base.device)
        value.set_(base.untyped_storage(), row["offset"],
                   tuple(row["shape"]), tuple(row["stride"]))
        if row["parameter"]:
            value = torch.nn.Parameter(value, requires_grad=row["requires_grad"])
        else:
            value.requires_grad_(row["requires_grad"])
        self.cache[idx] = value
        return value


def load_state(directory, map_device=None, *, max_bytes=DEFAULT_MAX_BYTES):
    """Verify every byte before loading trusted metadata and reconstruct views.

    map_device=None preserves original devices. A str/device redirects all
    storages (e.g. 'cpu' for CPU tests); original identity remains in manifest.
    Full original storage allocation is unavoidable; chunk staging stays bounded.
    """
    directory = Path(directory).absolute()
    if directory.is_symlink() or not directory.is_dir():
        raise StateStoreError("not a regular complete checkpoint directory")
    manifest_path = _safe_member(directory, "MANIFEST.json")
    if manifest_path.stat().st_size > 64 * 1024**2:
        raise StateStoreError("manifest exceeds size cap")
    manifest = json.loads(manifest_path.read_text())
    if manifest.get("schema") != SCHEMA or manifest.get("complete") is not True:
        raise StateStoreError("incomplete or incompatible checkpoint")
    total = manifest["total_storage_bytes"] + manifest["metadata_bytes"]
    if total > max_bytes or manifest["metadata_bytes"] > 64 * 1024**2:
        raise StateStoreError("checkpoint size cap exceeded")
    if not 0 < manifest["chunk_bytes"] <= MAX_CHUNK_BYTES:
        raise StateStoreError("invalid chunk bound")
    metadata_path = _safe_member(directory, "bundle.pkl")
    if (metadata_path.stat().st_size != manifest["metadata_bytes"] or
            _sha(metadata_path) != manifest["metadata_sha256"]):
        raise StateStoreError("bundle metadata integrity failure")
    expected_total = 0
    for row in manifest["storages"]:
        offset = 0
        for chunk in row["chunks"]:
            if (chunk["offset"] != offset or chunk["nbytes"] <= 0 or
                    chunk["nbytes"] > manifest["chunk_bytes"]):
                raise StateStoreError("invalid storage chunk coverage")
            path = _safe_member(directory, chunk["name"])
            if (path.stat().st_size != chunk["nbytes"] or
                    _sha(path) != chunk["sha256"]):
                raise StateStoreError("storage chunk integrity failure")
            offset += chunk["nbytes"]
        if offset != row["nbytes"]:
            raise StateStoreError("missing storage bytes")
        expected_total += row["nbytes"]
    if expected_total != manifest["total_storage_bytes"]:
        raise StateStoreError("storage byte accounting mismatch")
    bases = []
    for row in manifest["storages"]:
        device = torch.device(map_device) if map_device is not None else torch.device(row["device"])
        pinned = row["pinned"] if device.type == "cpu" and row["device"] == "cpu" else False
        base = torch.empty(row["nbytes"], dtype=torch.uint8, device=device,
                           pin_memory=pinned if device.type == "cpu" else False)
        for chunk in row["chunks"]:
            path = _safe_member(directory, chunk["name"])
            # A bytearray plus torch.frombuffer aliases a single bounded staging
            # buffer; destination is the persistent original-sized allocation.
            payload = bytearray(chunk["nbytes"])
            with open(path, "rb", buffering=0) as f:
                view = memoryview(payload)
                done = 0
                while done < len(payload):
                    count = f.readinto(view[done:])
                    if not count:
                        raise StateStoreError("chunk truncated after integrity verification")
                    done += count
                del view
            cpu = torch.frombuffer(payload, dtype=torch.uint8)
            base.narrow(0, chunk["offset"], chunk["nbytes"]).copy_(cpu, non_blocking=False)
            del cpu, payload
        bases.append(base)
    with open(metadata_path, "rb") as f:
        bundle = _Decoder(f, manifest, bases).load()
    return bundle, manifest


def fingerprint(bundle, *, chunk_bytes=DEFAULT_CHUNK_BYTES):
    """Stable bitwise content/alias/layout fingerprint, independent of addresses."""
    if not 0 < chunk_bytes <= MAX_CHUNK_BYTES:
        raise ValueError("invalid fingerprint chunk bound")
    stream = io.BytesIO()
    encoder = _Encoder(stream)
    encoder.dump(bundle)
    h = hashlib.sha256(stream.getvalue())
    h.update(json.dumps(encoder.tensors, sort_keys=True).encode())
    for row in encoder.storages:
        meta = {k: v for k, v in row.items() if k != "storage"}
        h.update(json.dumps(meta, sort_keys=True).encode())
        flat = torch.empty(0, dtype=torch.uint8, device=row["device"])
        flat.set_(row["storage"], 0, (row["nbytes"],), (1,))
        for offset in range(0, row["nbytes"], chunk_bytes):
            part = flat.narrow(0, offset, min(chunk_bytes, row["nbytes"] - offset))
            cpu = part.detach().to("cpu", non_blocking=False)
            h.update(memoryview(cpu.numpy()))
            del cpu, part
    return h.hexdigest()


def semantic_fingerprint(bundle, *, chunk_bytes=DEFAULT_CHUNK_BYTES):
    """Canonical exact state hash, ignoring immutable Python pickle memo choices.

    Legacy fingerprint() remains unchanged for historical provenance. Mutable
    dict/list identity, Tensor object identity/storage aliases, exact tensor raw
    bytes/layout and scalar/NumPy/RNG content remain significant. Attached grads
    must be explicit bundle fields as required by save_state().
    """
    import struct
    import numpy as np
    if not 0 < chunk_bytes <= MAX_CHUNK_BYTES:
        raise ValueError("invalid semantic fingerprint chunk bound")
    h = hashlib.sha256()
    encoder = _Encoder(io.BytesIO())
    mutable = {}
    active_tuples = set()
    def token(kind, value=b""):
        if isinstance(value, str):
            value = value.encode("utf-8")
        h.update(kind.encode("ascii") + b":" + str(len(value)).encode() + b":" + value)
    def visit(value):
        if isinstance(value, torch.Tensor):
            pid = encoder.persistent_id(value)
            token("tensor", str(pid[1])); return
        if isinstance(value, (dict, list, bytearray)):
            ident = id(value)
            if ident in mutable:
                token("mutable_ref", str(mutable[ident])); return
            mutable[ident] = len(mutable)
            token("mutable_id", str(mutable[ident]))
        if value is None: token("none")
        elif isinstance(value, bool): token("bool", b"1" if value else b"0")
        elif isinstance(value, int): token("int", str(value))
        elif isinstance(value, float): token("float64", struct.pack(">d", value))
        elif isinstance(value, complex): token("complex128", struct.pack(">dd", value.real, value.imag))
        elif isinstance(value, str): token("str", value)
        elif isinstance(value, bytes): token("bytes", value)
        elif isinstance(value, bytearray): token("bytearray", bytes(value))
        elif isinstance(value, np.ndarray):
            if value.dtype.hasobject: raise StateStoreError("object ndarray unsupported for semantic hash")
            token("ndarray_dtype", value.dtype.str)
            token("ndarray_shape", json.dumps(list(value.shape)))
            token("ndarray_bits", value.tobytes(order="C"))
        elif isinstance(value, np.generic):
            token("numpy_scalar_dtype", value.dtype.str)
            token("numpy_scalar_bits", value.tobytes())
        elif isinstance(value, dict):
            token("dict_count", str(len(value)))
            for key, item in value.items(): visit(key); visit(item)
        elif isinstance(value, list):
            token("list_count", str(len(value)))
            for item in value: visit(item)
        elif isinstance(value, tuple):
            if id(value) in active_tuples: raise StateStoreError("cyclic tuple unsupported")
            active_tuples.add(id(value)); token("tuple_count", str(len(value)))
            for item in value: visit(item)
            active_tuples.remove(id(value))
        elif isinstance(value, torch.dtype): token("torch_dtype", str(value))
        elif isinstance(value, torch.device): token("torch_device", str(value))
        else:
            raise StateStoreError("unsupported semantic fingerprint type: " + str(type(value)))
    visit(bundle)
    for row in encoder.tensors:
        meta = {k: v for k, v in row.items()
                if k != "attached_grad_requires_explicit_bundle_field"}
        token("tensor_metadata", json.dumps(meta, sort_keys=True))
    for row in encoder.storages:
        meta = {k: v for k, v in row.items() if k != "storage"}
        token("storage_metadata", json.dumps(meta, sort_keys=True))
        flat = torch.empty(0, dtype=torch.uint8, device=row["device"])
        flat.set_(row["storage"], 0, (row["nbytes"],), (1,))
        for offset in range(0, row["nbytes"], chunk_bytes):
            part = flat.narrow(0, offset, min(chunk_bytes, row["nbytes"] - offset))
            cpu = part.detach().to("cpu", non_blocking=False)
            h.update(memoryview(cpu.numpy()))
            del cpu, part
    return h.hexdigest()
