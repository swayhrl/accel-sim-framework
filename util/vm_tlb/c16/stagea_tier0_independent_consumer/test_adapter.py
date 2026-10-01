import unittest

from adapter import recompute_native_request_samples, verify_frozen_token_bindings, verify_point_identity


class AdapterTests(unittest.TestCase):
    def setUp(self):
        self.contract = {
            "points": {"MP02": {"target": "QWEN_BF16", "phase": "decode", "batch": 1,
                                "prompt_tokens_per_request": 512, "source_ids": ["S0"]}},
            "model_runtime_identity": {"vllm_source_commit": "v" * 40,
                                       "QWEN_BF16": {"revision": "m" * 40}},
        }
        self.binding = [{"point_id": "MP02", "source_text_id": "S0",
                         "model_key": "QWEN_BF16", "prompt_token_count": "512",
                         "source_utf8_sha256": "s" * 64, "tokenizer_revision": "t" * 40,
                         "token_ids_sha256": "i" * 64, "token_id_file_sha256": "f" * 64,
                         "token_ids_relative_path": "token_ids/QWEN_BF16/S0.json"}]
        self.identity = [{"point_id": "MP02", "source_text_id": "S0", "target": "QWEN_BF16",
                          "model_revision": "m" * 40, "vllm_source_commit": "v" * 40,
                          "phase": "decode", "batch_size": "1", "prompt_tokens": "512",
                          "source_utf8_sha256": "s" * 64, "tokenizer_revision": "t" * 40,
                          "token_ids_sha256": "i" * 64, "token_id_file_sha256": "f" * 64,
                          "correctness_status": "PASS"}]

    def test_point_identity(self):
        self.assertEqual(verify_point_identity(self.identity, self.binding, self.contract)["status"], "PASS")
        self.assertEqual(verify_point_identity(self.identity, self.binding, self.contract, {"MP02"})["status"], "PASS")
        self.assertEqual(verify_point_identity([], self.binding, self.contract, set())["status"], "PASS")
        with self.assertRaises(ValueError):
            verify_point_identity(self.identity + self.identity, self.binding, self.contract)
        with self.assertRaises(ValueError):
            verify_point_identity([{**self.identity[0], "batch_size": "4"}], self.binding, self.contract)

    def test_frozen_binding_against_asset_receipt(self):
        receipt = [{"model_key": "QWEN_BF16", "source_text_id": "S0",
                    **{key: self.binding[0][key] for key in (
                        "source_utf8_sha256", "tokenizer_revision", "prompt_token_count",
                        "token_ids_sha256", "token_id_file_sha256", "token_ids_relative_path")}}]
        self.assertEqual(verify_frozen_token_bindings(self.binding, receipt, self.contract)["status"], "PASS")
        with self.assertRaises(ValueError):
            verify_frozen_token_bindings([{**self.binding[0], "token_ids_sha256": "x" * 64}], receipt, self.contract)

    def test_native_recompute_and_duplicate(self):
        rows = []
        for arm in ("GRAPH_ON_NATIVE", "GRAPH_OFF_NATIVE"):
            for role, n in (("WARMUP", 1), ("MEASURED", 3)):
                for idx in range(n):
                    rows.append({"point_id": "MP02", "arm": arm, "sample_role": role,
                                 "sample_index": str(idx), "process_id": "1", "request_id": f"{arm}-{role}-{idx}",
                                 "request_cuda_event_ms": str(idx + 1), "host_wall_ms": str(idx + 2),
                                 "generated_token_count": "32", "token_ids_sha256": "z" * 64, "status": "PASS"})
        result = recompute_native_request_samples(rows, {"MP02"}, self.contract)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["cuda_median"], 2)
        with self.assertRaises(ValueError):
            recompute_native_request_samples(rows[:-1], {"MP02"}, self.contract)
        with self.assertRaises(ValueError):
            recompute_native_request_samples(rows + [rows[0]], {"MP02"}, self.contract)
        with self.assertRaises(ValueError):
            recompute_native_request_samples([{**rows[0], "generated_token_count": "31"}] + rows[1:], {"MP02"}, self.contract)


if __name__ == "__main__":
    unittest.main()
