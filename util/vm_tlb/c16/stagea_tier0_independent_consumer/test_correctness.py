import json
import tempfile
import unittest
from pathlib import Path

from correctness import compare_raw_graph_tokens


class CorrectnessTests(unittest.TestCase):
    def test_raw_token_mismatch(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp)
            def fixture(tokens):
                row = {"source_id": "S0", "input_file_sha256": "a" * 64,
                       "input_token_ids_sha256": "b" * 64,
                       "completion": {"tokens": tokens}}
                return {"point": "MP02", "samples": [{"rows": [row]} for _ in range(4)]}
            on, off = p / "on.json", p / "off.json"
            on.write_text(json.dumps(fixture([1, 2, 3])), encoding="utf-8")
            off.write_text(json.dumps(fixture([1, 9, 3])), encoding="utf-8")
            rows = compare_raw_graph_tokens(str(on), str(off), "MP02")
            self.assertEqual({r["status"] for r in rows}, {"TOKEN_MISMATCH_STOP_POINT"})
            self.assertEqual(rows[0]["first_mismatch_index_or_NA"], 1)
            off.write_text(json.dumps(fixture([1, 2, 3])), encoding="utf-8")
            self.assertEqual({r["status"] for r in compare_raw_graph_tokens(str(on), str(off), "MP02")}, {"MATCH"})


if __name__ == "__main__":
    unittest.main()
