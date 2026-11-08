"""DIAG-only metadata around actual Tensor.to/copy_ calls.

Payload denotes actual call operands, NOT measured DMA/DRAM bytes. No tensor
values, synchronization, data conversion or alternate mathematical call occurs.
"""
import threading
import time
import torch


def _meta(tensor):
    if not isinstance(tensor, torch.Tensor):
        return {"is_tensor": False, "python_type": type(tensor).__name__}
    try:
        return {
            "is_tensor": True, "device": str(tensor.device),
            "dtype": str(tensor.dtype), "shape": list(tensor.shape),
            "stride": list(tensor.stride()), "numel": int(tensor.numel()),
            "element_size": int(tensor.element_size()),
            "data_ptr": int(tensor.data_ptr()),
            "cpu_pinned": bool(tensor.is_pinned())
                if tensor.device.type == "cpu" else None,
        }
    except Exception as error:
        return {"is_tensor": True, "metadata_gap": type(error).__name__}


def _non_blocking(operation, args, kwargs):
    if "non_blocking" in kwargs:
        return kwargs["non_blocking"], "keyword"
    if operation == "copy_":
        return (args[1], "positional") if len(args) > 1 else (False, "default")
    if args:
        first = args[0]
        # Tensor and dtype overloads put non_blocking immediately after first.
        index = 1 if isinstance(first, (torch.Tensor, torch.dtype)) else 2
        if len(args) > index:
            return args[index], "positional"
    return False, "default"


class TransferObserver:
    def __init__(self, step_fn):
        self.step_fn = step_fn
        self.rows = []

    def _record(self, operation, src, dst, result, begin, end, args, kwargs,
                error=None):
        # Metadata is collected outside the recorded original-call boundary.
        source, target = _meta(src), _meta(dst)
        row = {
            "operation": operation, "step": self.step_fn(),
            "tid": threading.get_native_id(), "thread_ident": threading.get_ident(),
            "begin_host_monotonic_ns": begin, "end_host_monotonic_ns": end,
            "host_call_elapsed_ns": end - begin,
            "src": source, "dst": target,
            "returns_receiver": result is (dst if operation == "copy_" else src),
            "src_dst_same_object": src is dst,
            "kwargs_non_blocking_present": "non_blocking" in kwargs,
            "kwargs_non_blocking": kwargs.get("non_blocking"),
            "measurement_scope": "ACTUAL_CALL_OPERAND_PAYLOAD_NOT_DMA_OR_DRAM",
            "host_boundary": "ONLY_ORIGINAL_TENSOR_CALL_NO_SYNC",
        }
        nb, where = _non_blocking(operation, args, kwargs)
        row["non_blocking"] = bool(nb)
        row["non_blocking_binding"] = where
        complete = ("metadata_gap" not in source and "metadata_gap" not in target
                    and source.get("is_tensor") and target.get("is_tensor"))
        if complete:
            same_shape = source["shape"] == target["shape"]
            same_dtype = source["dtype"] == target["dtype"]
            same_storage = (source["device"] == target["device"]
                            and source["data_ptr"] == target["data_ptr"])
            same_view = (same_storage and same_shape and same_dtype
                         and source["stride"] == target["stride"])
            row.update(
                same_shape=same_shape, same_dtype=same_dtype,
                same_data_pointer=same_storage, identical_tensor_view=same_view,
                noop_label=("RETURNED_ORIGINAL_OBJECT" if operation == "to"
                            and result is src else
                            "SELF_OR_IDENTICAL_VIEW_COPY" if operation == "copy_"
                            and same_view else "NO_NOOP_CLAIM"),
                payload_shape_scope=("MATCHED_SHAPE" if same_shape else
                                     "BROADCAST_OR_SHAPE_MISMATCH"),
            )
            if same_shape:
                row["src_operand_payload_bytes"] = (
                    source["numel"] * source["element_size"])
                row["dst_operand_payload_bytes"] = (
                    target["numel"] * target["element_size"])
                row["logical_payload_bytes"] = (
                    source["numel"] * source["element_size"]
                    if same_dtype else None)
                row["logical_payload_scope"] = (
                    "MATCHED_SHAPE_AND_DTYPE_CALL_OPERAND_BYTES" if same_dtype
                    else "DTYPE_CONVERSION_SEPARATE_SRC_DST_OPERAND_BYTES")
            else:
                row["logical_payload_bytes"] = None
                row["logical_payload_scope"] = "NO_MATCHED_SHAPE_PAYLOAD_ASSUMPTION"
        else:
            row["logical_payload_bytes"] = None
            row["logical_payload_scope"] = "METADATA_UNAVAILABLE"
        if error is not None:
            row["original_call_error_type"] = type(error).__name__
            row["logical_payload_bytes"] = None
            row["logical_payload_scope"] = "ORIGINAL_CALL_FAILED"
        self.rows.append(row)

    def copy_(self, dst, *args, **kwargs):
        src = args[0] if args else kwargs.get("src")
        begin = time.monotonic_ns()
        try:
            result = dst.copy_(*args, **kwargs)
        except Exception as error:
            end = time.monotonic_ns()
            self._record("copy_", src, dst, None, begin, end, args, kwargs, error)
            raise
        end = time.monotonic_ns()
        self._record("copy_", src, dst, result, begin, end, args, kwargs)
        return result

    def to(self, src, *args, **kwargs):
        begin = time.monotonic_ns()
        try:
            result = src.to(*args, **kwargs)
        except Exception as error:
            end = time.monotonic_ns()
            self._record("to", src, None, None, begin, end, args, kwargs, error)
            raise
        end = time.monotonic_ns()
        self._record("to", src, result, result, begin, end, args, kwargs)
        return result
