#!/usr/bin/env python3
"""CPU-only, content-free public G0 check for four frozen WildChat rows."""
import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import duckdb  # noqa: E402
import torch  # noqa: E402
import transformers  # noqa: E402
from transformers import AutoTokenizer  # noqa: E402

ROOT = Path("/data/c16/aiarch_hybrid_asset_qualification_20261110_v1")
DATA = ROOT / "datasets/wildchat/train-00005-of-00006.parquet"
MODEL = ROOT / "models/qwen3_5_4b"
EXPECTED_LIST_SHA = "a5f4cfb551054561d6353d096143679bb8603c7ab0a2831d5f409ea86feee701"
CANDIDATES = """
WITH checks AS (
  SELECT t.conversation_id, t.turn, t.redacted, t.toxic,
    MAX(ARRAY_LENGTH(t.conversation)) AS n_messages,
    BOOL_AND(u.msg.role = CASE WHEN u.ord % 2 = 1 THEN 'user' ELSE 'assistant' END) AS roles_ok,
    BOOL_AND(u.msg.content IS NOT NULL AND LENGTH(TRIM(u.msg.content)) > 0) AS content_ok,
    BOOL_OR(COALESCE(u.msg.redacted, FALSE)) AS any_redacted,
    BOOL_OR(COALESCE(u.msg.toxic, FALSE)) AS any_toxic
  FROM read_parquet(?) AS t,
    UNNEST(t.conversation) WITH ORDINALITY AS u(msg, ord)
  GROUP BY t.conversation_id, t.turn, t.redacted, t.toxic
)
SELECT conversation_id FROM checks
WHERE turn >= 2 AND n_messages = 2 * turn AND roles_ok AND content_ok
  AND NOT COALESCE(redacted, TRUE) AND NOT COALESCE(toxic, TRUE)
  AND NOT any_redacted AND NOT any_toxic
"""


def sha256_file(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def restricted_json(path, value):
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    if path.parent.stat().st_mode & 0o077:
        raise RuntimeError("private directory has group/other permissions")
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(value, f, ensure_ascii=False, indent=2)


def signals(s):
    patterns = {
        "history_reference": r"(?i)\b(above|previous|earlier|you said|your list|as discussed|continue|that list|the third|based on your|revise it)\b|上(?:面|文|述)|刚才|之前|继续|第三项|你(?:说|提|列)|按.*(?:列表|建议)",
        "url_or_web_reference": r"(?i)https?://|www\.|\b(?:website|webpage|link|网页|链接)\b",
        "image_or_attachment_reference": r"(?i)!\[|<img\b|\b(?:attached|attachment|image|photo|screenshot|file)\b|附件|图片|截图|文件",
        "tool_or_external_action_reference": r"(?i)\b(?:browse|search online|run code|execute|open the link)\b|联网|运行代码|执行命令|打开链接",
        "code_or_markup": r"```|<\w+|\{\s*\"|\|.*\|",
    }
    return sorted(k for k, p in patterns.items() if re.search(p, s or ""))


def template_len(tok, messages):
    tokens = tok.apply_chat_template(messages, tokenize=True, add_generation_prompt=True, return_dict=True)
    return len(tokens["input_ids"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--private-dir", required=True, type=Path)
    ap.add_argument("--public-out", required=True, type=Path)
    a = ap.parse_args()
    os.umask(0o077)
    if a.public_out.is_relative_to(a.private_dir):
        raise RuntimeError("public output inside private directory")
    if not DATA.is_file() or not MODEL.is_dir():
        raise RuntimeError("frozen assets missing")
    con = duckdb.connect(":memory:")
    con.execute("SET threads=2")
    ids = [r[0] for r in con.execute(CANDIDATES, [str(DATA)]).fetchall()]
    if len(ids) != 27628:
        raise RuntimeError("candidate count drift")
    discovery = []
    holdout_count = 0
    for identifier in ids:
        digest = hashlib.sha256(identifier.encode("utf-8")).digest()
        if int.from_bytes(digest[:8], "big") % 5 == 0:
            holdout_count += 1
        else:
            discovery.append((digest, identifier))
    if len(discovery) != 22079 or holdout_count != 5549:
        raise RuntimeError("pool counts drift")
    selected = sorted(discovery)[:4]
    digest_list_sha = hashlib.sha256(("\n".join(d.hex() for d, _ in selected) + "\n").encode()).hexdigest()
    if digest_list_sha != EXPECTED_LIST_SHA:
        raise RuntimeError("frozen selection drift")
    rows = con.execute(
        "SELECT conversation_id, turn, language, redacted, toxic, conversation FROM read_parquet(?) WHERE conversation_id = ANY(?)",
        [str(DATA), [identifier for _, identifier in selected]],
    ).fetchall()
    if len(rows) != 4 or len({r[0] for r in rows}) != 4:
        raise RuntimeError("selected rows not unique")
    by_id = {r[0]: r for r in rows}
    tok = AutoTokenizer.from_pretrained(str(MODEL), local_files_only=True, trust_remote_code=False)
    public = []
    private = []
    for rank, (_, identifier) in enumerate(selected, 1):
        _, turn, lang, row_redacted, row_toxic, msgs = by_id[identifier]
        ref = f"S{rank:02d}"
        roles = [m["role"] for m in msgs]
        role_ok = roles == ["user" if i % 2 == 0 else "assistant" for i in range(len(msgs))]
        first_four = msgs[:4]
        users = [first_four[0], first_four[2]]
        nonempty = all(isinstance(m["content"], str) and m["content"].strip() for m in first_four)
        flags_clear = not row_redacted and not row_toxic and all(not m["redacted"] and not m["toxic"] for m in msgs)
        structure_pass = bool(turn >= 2 and len(msgs) == 2 * turn and role_ok and nonempty and flags_clear)
        u1, u2 = [m["content"] for m in users]
        u1_raw = len(tok.encode(u1, add_special_tokens=False))
        u2_raw = len(tok.encode(u2, add_special_tokens=False))
        first_prompt = template_len(tok, [{"role": "user", "content": u1}])
        second_empty = template_len(tok, [{"role": "user", "content": u1}, {"role": "assistant", "content": ""}, {"role": "user", "content": u2}])
        old_gpt_diag = template_len(tok, [{"role": m["role"], "content": m["content"]} for m in first_four[:3]])
        budget_est = second_empty + 256 + 32 + 256
        item = {
            "anonymous_ref": ref,
            "source": {"dataset_revision": "f66566ceaaeb619dd98ffb0f3bf3ce1f86775ac4", "shard": "train-00005-of-00006.parquet", "selection_rank": rank, "selection_commitment_sha256": EXPECTED_LIST_SHA},
            "structure": {"message_count": len(msgs), "turn": turn, "role_alternation": role_ok, "first_two_user_nonempty": bool(u1.strip() and u2.strip()), "first_four_nonempty": bool(nonempty), "row_and_message_redacted_toxic_clear": flags_clear, "pass": structure_pass},
            "tokenizer": {"class": type(tok).__name__, "user1_raw_tokens": u1_raw, "user2_raw_tokens": u2_raw, "first_prompt_tokens": first_prompt, "first_prompt_template_overhead_tokens": first_prompt - u1_raw, "second_prompt_with_empty_assistant_tokens": second_empty, "second_prompt_empty_assistant_template_overhead_tokens": second_empty - u1_raw - u2_raw, "original_gpt_second_prompt_tokens_diagnostic_only": old_gpt_diag, "second_request_total_estimate_with_256_token_a1_and_a2_and_32_slack": budget_est, "max_model_len": 8192, "known_inevitable_overflow": budget_est > 8192},
            "format": {"row_language": lang, "user_languages": [m["language"] for m in users], "signals": {"user1": signals(u1), "user2": signals(u2)}},
            "original_gpt_dependency": "PENDING_HUMAN_REVIEW", "privacy_and_rights": "PENDING_HUMAN_REVIEW", "plain_text_applicability": "PENDING_HUMAN_REVIEW", "review_method": "CPU mechanical only; restricted local human dossier prepared", "authorized_human_confirmation": False, "final_classification": "PENDING_HUMAN_REVIEW", "reason_categories": ["HUMAN_SEMANTIC_REVIEW_PENDING", "HUMAN_PRIVACY_RIGHTS_REVIEW_PENDING", "TEXT_COMPLETENESS_REVIEW_PENDING"],
        }
        public.append(item)
        private.append({"anonymous_ref": ref, "conversation_id": identifier, "source_revision": "f66566ceaaeb619dd98ffb0f3bf3ce1f86775ac4", "user1": u1, "original_gpt_assistant1_FOR_DEPENDENCY_DIAGNOSIS_ONLY": first_four[1]["content"], "user2": u2, "review_form": {"original_gpt_dependency": None, "pii_and_sensitive_content": None, "rights_and_access": None, "plain_text_completeness": None, "reviewer_identity_and_authorization": None, "decision": None}})
    if [s["tokenizer"]["first_prompt_tokens"] for s in public] != [42, 15, 12, 855]:
        raise RuntimeError("first prompt counts drift from V1 commitment")
    if [s["tokenizer"]["original_gpt_second_prompt_tokens_diagnostic_only"] for s in public] != [212, 85, 33, 1095]:
        raise RuntimeError("original GPT diagnostic counts drift from V1 commitment")
    if torch.cuda.is_initialized():
        raise RuntimeError("CUDA was initialized during CPU-only G0")
    result = {"schema": "AI_ARCH_HYBRID_FOUR_SESSION_G0_CPU_V1", "authority_commit": "d058d4faf2d93e31976888808a608c4a8fa46714", "authority_tree": "fd6085fe75179143a764ed8aa050ef10a37112eb", "source_file_sha256": sha256_file(DATA), "source_file_bytes": DATA.stat().st_size, "selection": {"candidate_count": len(ids), "discovery_count": len(discovery), "holdout_count": holdout_count, "selected_digest_list_sha256": digest_list_sha}, "tokenizer": {"model_revision": "851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a", "class": type(tok).__name__, "files_sha256": {name: sha256_file(MODEL / name) for name in ("tokenizer.json", "tokenizer_config.json")}}, "cpu_runtime": {"python": sys.version.split()[0], "duckdb": duckdb.__version__, "transformers": transformers.__version__}, "sessions": public, "g0_decision": "G0_PARTIAL_PENDING_REVIEW", "gpu_eligible": False, "cuda_initialized": False}
    restricted_json(a.private_dir / "review_cases.json", private)
    a.public_out.parent.mkdir(parents=True, exist_ok=True)
    a.public_out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["g0_decision"], "selected_count": len(public), "selection_commitment_sha256": digest_list_sha, "public_out": str(a.public_out), "private_dossier_created": True, "cuda_initialized": False}))


if __name__ == "__main__":
    main()
