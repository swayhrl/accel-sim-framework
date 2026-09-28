#!/usr/bin/env python3
import unittest

from audit import config_binding


class AuditArithmeticTests(unittest.TestCase):
    def test_exact_config_arithmetic(self):
        config = {
            "num_attention_heads": 16,
            "num_key_value_heads": 16,
            "kv_lora_rank": 512,
            "qk_nope_head_dim": 128,
            "qk_rope_head_dim": 64,
            "v_head_dim": 128,
            "use_cache": True,
            "torch_dtype": "bfloat16",
            "transformers_version": "4.33.1",
        }
        result = config_binding(config)
        self.assertEqual(result["source_implied_latent_bytes_per_token_bf16"], 1152)
        self.assertEqual(result["accepted_runtime_cache_bytes_per_token_bf16"], 10240)
        self.assertAlmostEqual(result["runtime_over_latent_ratio"], 80 / 9)

    def test_context_endpoint_ratio(self):
        self.assertAlmostEqual(8193 / 2049, 3.998535871156662)


if __name__ == "__main__":
    unittest.main(verbosity=2)
