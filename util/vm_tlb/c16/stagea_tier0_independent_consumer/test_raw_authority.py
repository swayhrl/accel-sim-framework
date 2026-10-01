import json
import tempfile
import unittest
from hashlib import sha256
from pathlib import Path

from adapter import read_contract_tsv, verify_frozen_token_bindings
from raw_authority import load_final_contract, load_producer_raw_authority


class RawAuthorityTests(unittest.TestCase):
    def test_checked_in_final_contract(self):
        parents = Path(__file__).resolve().parents
        if len(parents) <= 4:
            self.skipTest("standalone staging directory; repository test runs this")
        repo = parents[4]
        pack = repo / "docs/vm_tlb/review_packs/C16_STAGEA_DENSE_FIRST_TIER0_CONTRACT_FINALIZATION_174NEW_V1"
        if not pack.exists():
            self.skipTest("standalone staging directory; repository test runs this")
        contract = load_final_contract(pack)
        self.assertEqual(contract["point_allowlist_in_order"], ["MP01", "MP02", "MP03", "MP05"])
        binding_rows = read_contract_tsv(pack / "POINT_TOKEN_BINDINGS.tsv",
            ["point_id", "model_key", "source_text_id", "source_utf8_sha256", "tokenizer_revision",
             "prompt_token_count", "token_ids_sha256", "token_id_file_sha256", "token_ids_relative_path"],
            ["point_id", "source_text_id"])
        receipt = repo / "docs/vm_tlb/review_packs/C16_MEASUREMENT_CAMPAIGN_STAGEA_ASSET_INPUT_CLOSURE_174NEW_V1/TOKENIZATION_RECEIPTS.tsv"
        receipt_rows = read_contract_tsv(receipt,
            ["model_key", "source_text_id", "source_utf8_sha256", "tokenizer_revision",
             "prompt_token_count", "token_ids_sha256", "token_id_file_sha256", "token_ids_relative_path"],
            ["model_key", "source_text_id"])
        self.assertEqual(verify_frozen_token_bindings(binding_rows, receipt_rows, contract), {"status": "PASS", "binding_rows": 7})

    def test_contract_fail_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp)
            (p / "C16_STAGEA_DENSE_FIRST_TIER0_109_CONTRACT_V1.json").write_text("{}", encoding="utf-8")
            with self.assertRaises(ValueError):
                load_final_contract(p)

    def test_producer_status_and_raw_hash(self):
        with tempfile.TemporaryDirectory() as temp:
            pack = Path(temp) / "pack"
            run = Path(temp) / "durable" / "R1"
            pack.mkdir()
            run.mkdir(parents=True)
            raw = run / "POINT_IDENTITY.tsv"
            raw.write_text("x\n", encoding="utf-8")
            digest = sha256(raw.read_bytes()).hexdigest()
            index = ("artifact\tnode109_path\tbytes\tsha256\tnode164_path\n"
                     f"POINT_IDENTITY.tsv\t/data/raw/POINT_IDENTITY.tsv\t2\t{digest}\t{raw}\n")
            (pack / "RAW_INDEX.tsv").write_text(index, encoding="utf-8")
            (pack / "FINAL_DECISION.json").write_text(json.dumps({
                "status": "STAGEA_TIER0_PRODUCER_PARTIAL", "automatic_next_goal": False,
                "run_id": "R1"}), encoding="utf-8")
            contract = {"durable_publish": {"durable_root": str(run)}}
            # The production guard forbids arbitrary roots, so synthetic
            # fixtures must fail before any point can be admitted.
            with self.assertRaises(ValueError):
                load_producer_raw_authority(pack, contract)
            (pack / "FINAL_DECISION.json").write_text(json.dumps({
                "status": "PENDING", "automatic_next_goal": False, "run_id": "R1"}), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_producer_raw_authority(pack, contract)


if __name__ == "__main__":
    unittest.main()
