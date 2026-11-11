#!/usr/bin/env python3
"""Select four WildChat discovery sessions without publishing IDs or text."""

import hashlib
import json
import os
from pathlib import Path

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import duckdb  # noqa: E402
from transformers import AutoTokenizer  # noqa: E402

ROOT = Path("/data/c16/aiarch_hybrid_asset_qualification_20261110_v1")
DATA = ROOT / "datasets/wildchat/train-00005-of-00006.parquet"
MODEL = ROOT / "models/qwen3_5_4b"

# Identical candidate filter to the published asset qualification script.
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


def main() -> None:
    con = duckdb.connect(":memory:")
    con.execute("SET threads=2")
    identifiers = [row[0] for row in con.execute(CANDIDATES, [str(DATA)]).fetchall()]
    assert len(identifiers) == 27628
    discovery = []
    holdout_count = 0
    for identifier in identifiers:
        digest = hashlib.sha256(identifier.encode("utf-8")).digest()
        if int.from_bytes(digest[:8], "big") % 5 == 0:
            holdout_count += 1
        else:
            discovery.append((digest, identifier))
    assert len(discovery) == 22079 and holdout_count == 5549
    selected = sorted(discovery)[:4]
    rows = con.execute(
        "SELECT conversation_id, conversation FROM read_parquet(?) WHERE conversation_id = ANY(?)",
        [str(DATA), [identifier for _, identifier in selected]],
    ).fetchall()
    assert len(rows) == 4
    row_by_id = {identifier: conversation for identifier, conversation in rows}
    tokenizer = AutoTokenizer.from_pretrained(
        str(MODEL), local_files_only=True, trust_remote_code=False
    )
    input_counts = []
    gpt_history_counts = []
    for _, identifier in selected:
        messages = [
            {"role": message["role"], "content": message["content"]}
            for message in row_by_id[identifier]
        ]
        first = tokenizer.apply_chat_template(
            messages[:1], tokenize=True, add_generation_prompt=True
        )
        second_with_original_history = tokenizer.apply_chat_template(
            messages[:3], tokenize=True, add_generation_prompt=True
        )
        input_counts.append(len(first["input_ids"]))
        gpt_history_counts.append(len(second_with_original_history["input_ids"]))
    import torch

    assert not torch.cuda.is_initialized()
    digest_list = "\n".join(digest.hex() for digest, _ in selected) + "\n"
    print(json.dumps({
        "scope": "four_candidate_discovery_sessions_cpu_only_no_content_or_ids_published",
        "selection_rule": "lowest four full SHA256(conversation_id UTF-8) among filtered mod-5 discovery",
        "selected_digest_list_sha256": hashlib.sha256(digest_list.encode()).hexdigest(),
        "candidate_count": len(identifiers),
        "discovery_count": len(discovery),
        "holdout_count": holdout_count,
        "first_user_prompt_tokens": input_counts,
        "second_user_with_original_gpt_history_tokens_diagnostic_only": gpt_history_counts,
        "tokenizer_class": type(tokenizer).__name__,
        "cuda_initialized": False,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
