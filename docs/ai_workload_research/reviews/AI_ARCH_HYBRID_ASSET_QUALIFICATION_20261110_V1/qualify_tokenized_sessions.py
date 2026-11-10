#!/usr/bin/env python3
"""Bound natural-session prompt sizes with the fixed Qwen tokenizer, CPU only."""

import hashlib
import json
import os
from statistics import median

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import duckdb  # noqa: E402
from transformers import AutoTokenizer  # noqa: E402


ROOT = "/data/c16/aiarch_hybrid_asset_qualification_20261110_v1"
DATA = ROOT + "/datasets/wildchat/train-00005-of-00006.parquet"
MODEL = ROOT + "/models/qwen3_5_4b"

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


def summary(values: list[int]) -> dict[str, int | float]:
    ordered = sorted(values)
    return {"min": ordered[0], "median": median(ordered),
            "p90_nearest_rank": ordered[(9 * len(ordered) + 9) // 10 - 1],
            "max": ordered[-1]}


def main() -> None:
    con = duckdb.connect(":memory:")
    con.execute("SET threads=2")
    candidate_ids = [r[0] for r in con.execute(CANDIDATES, [DATA]).fetchall()]
    discovery = []
    for identifier in candidate_ids:
        digest = hashlib.sha256(identifier.encode("utf-8")).digest()
        if int.from_bytes(digest[:8], "big") % 5 != 0:
            discovery.append((digest, identifier))
    selected_ids = [identifier for _, identifier in sorted(discovery)[:64]]
    rows = con.execute(
        "SELECT conversation_id, conversation FROM read_parquet(?) WHERE conversation_id = ANY(?)",
        [DATA, selected_ids],
    ).fetchall()
    if len(rows) != 64:
        raise RuntimeError(f"expected 64 distinct selected sessions, found {len(rows)}")
    tokenizer = AutoTokenizer.from_pretrained(MODEL, local_files_only=True, trust_remote_code=False)
    second_turn, final_turn, turns = [], [], []
    for _, conversation in rows:
        messages = [{"role": item["role"], "content": item["content"]} for item in conversation]
        second = tokenizer.apply_chat_template(messages[:3], tokenize=True, add_generation_prompt=True)
        final = tokenizer.apply_chat_template(messages[:-1], tokenize=True, add_generation_prompt=True)
        second_turn.append(len(second["input_ids"]))
        final_turn.append(len(final["input_ids"]))
        turns.append(len(messages) // 2)
    import torch

    if torch.cuda.is_initialized():
        raise RuntimeError("CUDA was initialized")
    print(json.dumps({"selected_discovery_sessions": 64,
                      "selection": "lowest 64 SHA256(conversation_id UTF-8) among mod-5 discovery",
                      "tokenizer_class": type(tokenizer).__name__,
                      "second_turn_input_tokens": summary(second_turn),
                      "last_turn_input_tokens": summary(final_turn),
                      "turns": summary(turns), "cuda_initialized": False}, indent=2))


if __name__ == "__main__":
    main()
