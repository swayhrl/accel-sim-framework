#!/usr/bin/env python3
"""Audited ctypes wrapper for the locally compiled CUDA persistence helper."""

import ctypes
import time
from pathlib import Path

import torch


LIBRARY = Path("/data/c16/e1_residency_cost_benefit_closure_v1/build/libc16_cuda_persistence.so")


class Capability(ctypes.Structure):
    _fields_ = [
        ("runtime_version", ctypes.c_int),
        ("driver_version", ctypes.c_int),
        ("device_ordinal", ctypes.c_int),
        ("l2_bytes", ctypes.c_int),
        ("max_persisting_l2_bytes", ctypes.c_int),
        ("max_access_policy_window_bytes", ctypes.c_int),
        ("device_name", ctypes.c_char * 256),
    ]


class PersistenceHelper:
    def __init__(self):
        self.library = ctypes.CDLL(str(LIBRARY))
        self.library.c16_query_capability.argtypes = [ctypes.c_int, ctypes.POINTER(Capability)]
        self.library.c16_query_capability.restype = ctypes.c_int
        self.library.c16_set_persisting_limit.argtypes = [ctypes.c_size_t]
        self.library.c16_set_persisting_limit.restype = ctypes.c_int
        self.library.c16_get_persisting_limit.argtypes = [ctypes.POINTER(ctypes.c_size_t)]
        self.library.c16_get_persisting_limit.restype = ctypes.c_int
        self.library.c16_reset_persisting_l2.restype = ctypes.c_int
        self.library.c16_set_access_policy.argtypes = [ctypes.c_uint64, ctypes.c_uint64, ctypes.c_size_t, ctypes.c_float, ctypes.c_int]
        self.library.c16_set_access_policy.restype = ctypes.c_int
        self.library.c16_set_access_policy_mode.argtypes = [ctypes.c_uint64, ctypes.c_uint64, ctypes.c_size_t, ctypes.c_float, ctypes.c_int, ctypes.c_int]
        self.library.c16_set_access_policy_mode.restype = ctypes.c_int
        self.library.c16_clear_access_policy.argtypes = [ctypes.c_uint64]
        self.library.c16_clear_access_policy.restype = ctypes.c_int
        self.library.c16_cuda_error_string.argtypes = [ctypes.c_int]
        self.library.c16_cuda_error_string.restype = ctypes.c_char_p

    def checked(self, operation, status):
        if status != 0:
            message = self.library.c16_cuda_error_string(status).decode("utf-8", errors="replace")
            raise RuntimeError(f"{operation} failed: CUDA {status}: {message}")
        return {"operation": operation, "status": status, "error_string": "no error"}

    def query_capability(self, device=0):
        value = Capability()
        self.checked("cuda capability query", self.library.c16_query_capability(device, ctypes.byref(value)))
        return {
            "runtime_version": value.runtime_version,
            "driver_version": value.driver_version,
            "device_ordinal": value.device_ordinal,
            "device_name": value.device_name.split(b"\0", 1)[0].decode(),
            "l2_bytes": value.l2_bytes,
            "max_persisting_l2_bytes": value.max_persisting_l2_bytes,
            "max_access_policy_window_bytes": value.max_access_policy_window_bytes,
        }

    def get_limit(self):
        value = ctypes.c_size_t()
        self.checked("cudaDeviceGetLimit", self.library.c16_get_persisting_limit(ctypes.byref(value)))
        return value.value

    def stream_value(self):
        return int(torch.cuda.current_stream().cuda_stream)

    def begin_condition(self, condition, budget_bytes, qweight=None, hit_ratio=1.0):
        stream = self.stream_value()
        operations = []
        operations.append(self.checked("clear stream access-policy before condition", self.library.c16_clear_access_policy(stream)))
        operations.append(self.checked("reset persisting L2 before condition", self.library.c16_reset_persisting_l2()))
        operations.append(self.checked("set persisting-L2 limit", self.library.c16_set_persisting_limit(int(budget_bytes))))
        actual_limit = self.get_limit()
        window = None
        if qweight is not None:
            pointer = int(qweight.data_ptr())
            num_bytes = int(qweight.numel() * qweight.element_size())
            operations.append(
                self.checked(
                    "set stream access-policy window",
                    self.library.c16_set_access_policy(stream, pointer, num_bytes, float(hit_ratio), 1),
                )
            )
            window = {
                "base_ptr": pointer,
                "num_bytes": num_bytes,
                "hit_ratio": float(hit_ratio),
                "hit_property": "cudaAccessPropertyPersisting",
                "miss_property": "cudaAccessPropertyStreaming",
            }
        return {
            "condition": condition,
            "requested_setaside_bytes": int(budget_bytes),
            "actual_setaside_bytes": int(actual_limit),
            "stream_value": stream,
            "access_policy_window": window,
            "reset_before": True,
            "operations_before": operations,
        }

    def end_condition(self, receipt):
        stream = self.stream_value()
        operations = []
        operations.append(self.checked("clear stream access-policy after condition", self.library.c16_clear_access_policy(stream)))
        operations.append(self.checked("reset persisting L2 after condition", self.library.c16_reset_persisting_l2()))
        operations.append(self.checked("clear persisting-L2 limit after condition", self.library.c16_set_persisting_limit(0)))
        receipt["actual_setaside_after_reset_bytes"] = int(self.get_limit())
        receipt["reset_after"] = True
        receipt["operations_after"] = operations
        return receipt

    def update_access_policy(self, label, qweight, hit_ratio, persisting):
        stream = self.stream_value()
        pointer = int(qweight.data_ptr())
        num_bytes = int(qweight.numel() * qweight.element_size())
        hit_mode = 2 if persisting else 0
        miss_mode = 1 if persisting else 0
        started = time.perf_counter_ns()
        status = self.library.c16_set_access_policy_mode(
            stream, pointer, num_bytes, float(hit_ratio), hit_mode, miss_mode
        )
        ended = time.perf_counter_ns()
        operation = self.checked(f"update access-policy window {label}", status)
        return {
            "label": label,
            "stream_value": stream,
            "base_ptr": pointer,
            "num_bytes": num_bytes,
            "hit_ratio": float(hit_ratio),
            "hit_property": "cudaAccessPropertyPersisting" if persisting else "cudaAccessPropertyNormal",
            "miss_property": "cudaAccessPropertyStreaming" if persisting else "cudaAccessPropertyNormal",
            "persisting": bool(persisting),
            "cpu_update_ns": ended - started,
            "operation": operation,
        }


def qweight_region(module, tensor_name):
    tensor = module.qweight
    tensor_bytes = tensor.numel() * tensor.element_size()
    storage = tensor.untyped_storage()
    return {
        "tensor_name": tensor_name,
        "dtype": str(tensor.dtype),
        "shape": list(tensor.shape),
        "numel": tensor.numel(),
        "element_size_bytes": tensor.element_size(),
        "bytes": tensor_bytes,
        "data_ptr": tensor.data_ptr(),
        "storage_offset_elements": tensor.storage_offset(),
        "storage_offset_bytes": tensor.storage_offset() * tensor.element_size(),
        "contiguous": tensor.is_contiguous(),
        "storage_nbytes": storage.nbytes(),
        "exact_tensor_span_begin": tensor.data_ptr(),
        "exact_tensor_span_end_exclusive": tensor.data_ptr() + tensor_bytes,
    }
