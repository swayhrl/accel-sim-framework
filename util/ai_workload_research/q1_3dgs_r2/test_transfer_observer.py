import os
os.sched_setaffinity(0, {22, 23})
import unittest
import torch
from transfer_observer import TransferObserver


class TransferObserverTests(unittest.TestCase):
    def setUp(self):
        torch.set_num_threads(1)
        self.observer = TransferObserver(lambda: 15140)

    def test_copy_exact_output_alias_return_payload(self):
        source = torch.arange(12, dtype=torch.float32).reshape(3, 4)
        target = torch.zeros_like(source)
        result = self.observer.copy_(target, source, non_blocking=False)
        self.assertIs(result, target)
        self.assertTrue(torch.equal(source, target))
        row = self.observer.rows[-1]
        self.assertEqual(row["logical_payload_bytes"], 48)
        self.assertEqual(row["step"], 15140)
        self.assertTrue(row["returns_receiver"])
        self.assertEqual(row["src"]["data_ptr"], source.data_ptr())
        self.assertEqual(row["dst"]["data_ptr"], target.data_ptr())
        self.assertEqual(row["src"]["stride"], [4, 1])
        self.assertFalse(row["src"]["cpu_pinned"])

    def test_to_noop_returns_exact_original_object(self):
        source = torch.arange(3, dtype=torch.float32)
        result = self.observer.to(source, "cpu")
        self.assertIs(result, source)
        row = self.observer.rows[-1]
        self.assertEqual("RETURNED_ORIGINAL_OBJECT", row["noop_label"])
        self.assertTrue(row["src_dst_same_object"])

    def test_to_dtype_conversion_is_original_dtype_result(self):
        source = torch.tensor([1.125, 2.25], dtype=torch.float32)
        expected = source.to(torch.float64)
        result = self.observer.to(source, torch.float64)
        self.assertEqual(result.dtype, torch.float64)
        self.assertTrue(torch.equal(result, expected))
        row = self.observer.rows[-1]
        self.assertEqual(row["src_operand_payload_bytes"], 8)
        self.assertEqual(row["dst_operand_payload_bytes"], 16)
        self.assertIsNone(row["logical_payload_bytes"])

    def test_to_other_tensor_overload(self):
        source = torch.arange(3, dtype=torch.float32)
        other = torch.empty(3, dtype=torch.float64)
        result = self.observer.to(source, other, True)
        self.assertEqual(result.dtype, other.dtype)
        self.assertEqual(result.device, other.device)
        self.assertTrue(self.observer.rows[-1]["non_blocking"])

    def test_copy_broadcast_does_not_fabricate_matched_payload(self):
        source = torch.tensor([2.0])
        target = torch.zeros(2, 3)
        self.observer.copy_(target, source)
        self.assertTrue(torch.equal(target, torch.full((2, 3), 2.0)))
        row = self.observer.rows[-1]
        self.assertEqual("BROADCAST_OR_SHAPE_MISMATCH", row["payload_shape_scope"])
        self.assertIsNone(row["logical_payload_bytes"])

    def test_noncontiguous_stride_kept(self):
        source = torch.arange(12, dtype=torch.float32).reshape(3, 4).T
        target = torch.empty_like(source)
        self.observer.copy_(target, source)
        row = self.observer.rows[-1]
        self.assertEqual(list(source.stride()), row["src"]["stride"])
        self.assertTrue(torch.equal(source, target))

    def test_self_copy_is_labeled_without_new_object(self):
        source = torch.arange(3, dtype=torch.float32)
        self.assertIs(source, self.observer.copy_(source, source))
        self.assertEqual("SELF_OR_IDENTICAL_VIEW_COPY",
                         self.observer.rows[-1]["noop_label"])

    def test_copy_true_positional_nonblocking_preserved(self):
        source, target = torch.ones(4), torch.zeros(4)
        self.observer.copy_(target, source, True)
        row = self.observer.rows[-1]
        self.assertTrue(row["non_blocking"])
        self.assertEqual("positional", row["non_blocking_binding"])

    def test_to_copy_true_returns_distinct_original_method_result(self):
        source = torch.arange(3, dtype=torch.float32)
        result = self.observer.to(source, copy=True)
        self.assertIsNot(result, source)
        self.assertTrue(torch.equal(result, source))
        self.assertEqual("NO_NOOP_CLAIM", self.observer.rows[-1]["noop_label"])

    def test_autograd_semantics_unchanged(self):
        source = torch.tensor([1.0, 2.0], requires_grad=True)
        result = self.observer.to(source, torch.float64)
        (result * 3).sum().backward()
        self.assertTrue(torch.equal(source.grad, torch.tensor([3.0, 3.0])))

    def test_original_error_propagates_and_is_recorded(self):
        source, target = torch.zeros(2), torch.zeros(3)
        with self.assertRaises(RuntimeError):
            self.observer.copy_(target, source)
        row = self.observer.rows[-1]
        self.assertEqual("RuntimeError", row["original_call_error_type"])
        self.assertIsNone(row["logical_payload_bytes"])

    def test_time_scope_and_empty_payload(self):
        source, target = torch.empty(0), torch.empty(0)
        self.observer.copy_(target, source)
        row = self.observer.rows[-1]
        self.assertEqual(0, row["logical_payload_bytes"])
        self.assertGreaterEqual(row["end_host_monotonic_ns"],
                                row["begin_host_monotonic_ns"])
        self.assertGreater(row["tid"], 0)
        self.assertIn("NOT_DMA_OR_DRAM", row["measurement_scope"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
