#!/usr/bin/env python3
"""Inspect fixed Parquet assets without emitting message content."""

import argparse
import hashlib
import json

import duckdb


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    parser.add_argument("--kind", choices=["schema", "exgentic", "wildchat"], default="schema")
    args = parser.parse_args()
    con = duckdb.connect(":memory:")
    con.execute("SET threads=2")
    schema = con.execute("DESCRIBE SELECT * FROM read_parquet(?)", [args.path]).fetchall()
    rows = con.execute("SELECT COUNT(*) FROM read_parquet(?)", [args.path]).fetchone()[0]
    result = {"rows": rows, "columns": [[r[0], r[1]] for r in schema]}
    if args.kind == "exgentic":
        span_sql = """
        WITH s AS (
          SELECT session_id, benchmark, harness, u.span AS span
          FROM read_parquet(?) AS t, UNNEST(t.spans) AS u(span)
        )
        SELECT COUNT(*) AS spans, COUNT(DISTINCT session_id) AS sessions,
          COUNT(*) FILTER (WHERE span.attributes."gen_ai.operation.name" = 'chat') AS chat_spans,
          COUNT(*) FILTER (WHERE span.attributes."gen_ai.input.messages" IS NOT NULL) AS input_payloads,
          COUNT(*) FILTER (WHERE span.attributes."gen_ai.output.messages" IS NOT NULL) AS output_payloads,
          COUNT(*) FILTER (WHERE json_valid(span.attributes."gen_ai.input.messages")) AS valid_input_json,
          COUNT(*) FILTER (WHERE json_valid(span.attributes."gen_ai.output.messages")) AS valid_output_json,
          COUNT(*) FILTER (WHERE list_contains(span.attributes."gen_ai.response.finish_reasons", 'stop')) AS stop_finish,
          COUNT(*) FILTER (WHERE span.status.code = 1) AS status_one,
          COUNT(*) FILTER (WHERE span.status.code = 2) AS status_two
        FROM s
        """
        names = ["spans", "sessions", "chat_spans", "input_payloads", "output_payloads", "valid_input_json", "valid_output_json", "stop_finish", "status_one", "status_two"]
        result["span_counts"] = dict(zip(names, con.execute(span_sql, [args.path]).fetchone()))
        sessions_sql = """
        WITH s AS (
          SELECT session_id, u.span AS span
          FROM read_parquet(?) AS t, UNNEST(t.spans) AS u(span)
        ), per_session AS (
          SELECT session_id,
            COUNT(*) FILTER (WHERE span.attributes."gen_ai.operation.name" = 'chat') AS chat_calls,
            COUNT(*) FILTER (WHERE json_valid(span.attributes."gen_ai.input.messages")
              AND json_valid(span.attributes."gen_ai.output.messages")) AS paired_json_calls,
            COUNT(*) FILTER (WHERE list_contains(span.attributes."gen_ai.response.finish_reasons", 'stop')) AS stop_calls
          FROM s GROUP BY session_id
        )
        SELECT COUNT(*) FILTER (WHERE chat_calls >= 2) AS multi_chat_sessions,
          COUNT(*) FILTER (WHERE paired_json_calls >= 2) AS multi_paired_json_sessions,
          COUNT(*) FILTER (WHERE chat_calls >= 2 AND stop_calls >= 2) AS multi_stop_sessions
        FROM per_session
        """
        names = ["multi_chat_sessions", "multi_paired_json_sessions", "multi_stop_sessions"]
        result["session_counts"] = dict(zip(names, con.execute(sessions_sql, [args.path]).fetchone()))
        result["benchmarks"] = con.execute(
            "SELECT benchmark, COUNT(*) FROM read_parquet(?) GROUP BY benchmark ORDER BY benchmark",
            [args.path],
        ).fetchall()
        result["harnesses"] = con.execute(
            "SELECT harness, COUNT(*) FROM read_parquet(?) GROUP BY harness ORDER BY harness",
            [args.path],
        ).fetchall()
        result["model_lists"] = con.execute(
            "SELECT models, COUNT(*) FROM read_parquet(?) GROUP BY models ORDER BY COUNT(*) DESC",
            [args.path],
        ).fetchall()
        result["message_array_lengths"] = con.execute(
            """
            WITH s AS (
              SELECT u.span AS span FROM read_parquet(?) AS t, UNNEST(t.spans) AS u(span)
            )
            SELECT MIN(json_array_length(span.attributes."gen_ai.input.messages")),
              MEDIAN(json_array_length(span.attributes."gen_ai.input.messages")),
              MAX(json_array_length(span.attributes."gen_ai.input.messages")),
              MIN(LENGTH(span.attributes."gen_ai.input.messages")),
              MEDIAN(LENGTH(span.attributes."gen_ai.input.messages")),
              MAX(LENGTH(span.attributes."gen_ai.input.messages"))
            FROM s
            """,
            [args.path],
        ).fetchone()
    if args.kind == "wildchat":
        names = [
            "distinct_ids", "multi_turn", "four_or_more_messages", "multi_turn_last_assistant",
            "turn_message_count_equal", "redacted_rows", "toxic_rows", "empty_or_null_content_messages",
            "redacted_messages", "toxic_messages",
        ]
        counts = con.execute(
            """
            WITH c AS (
              SELECT *, ARRAY_LENGTH(conversation) AS n_messages,
                LIST_EXTRACT(conversation, -1).role AS last_role
              FROM read_parquet(?)
            ), m AS (
              SELECT u.msg AS msg FROM c, UNNEST(c.conversation) AS u(msg)
            )
            SELECT (SELECT COUNT(DISTINCT conversation_id) FROM c),
              (SELECT COUNT(*) FROM c WHERE turn >= 2),
              (SELECT COUNT(*) FROM c WHERE n_messages >= 4),
              (SELECT COUNT(*) FROM c WHERE turn >= 2 AND n_messages >= 4 AND last_role = 'assistant'),
              (SELECT COUNT(*) FROM c WHERE n_messages = 2 * turn),
              (SELECT COUNT(*) FROM c WHERE redacted),
              (SELECT COUNT(*) FROM c WHERE toxic),
              (SELECT COUNT(*) FROM m WHERE msg.content IS NULL OR LENGTH(TRIM(msg.content)) = 0),
              (SELECT COUNT(*) FROM m WHERE msg.redacted),
              (SELECT COUNT(*) FROM m WHERE msg.toxic)
            """,
            [args.path],
        ).fetchone()
        result["counts"] = dict(zip(names, counts))
        result["turn_range"] = con.execute(
            "SELECT MIN(turn), MEDIAN(turn), MAX(turn), MIN(ARRAY_LENGTH(conversation)), MEDIAN(ARRAY_LENGTH(conversation)), MAX(ARRAY_LENGTH(conversation)) FROM read_parquet(?)",
            [args.path],
        ).fetchone()
        result["roles"] = con.execute(
            "SELECT u.msg.role, COUNT(*) FROM read_parquet(?) t, UNNEST(t.conversation) AS u(msg) GROUP BY 1 ORDER BY 1",
            [args.path],
        ).fetchall()
        candidate_sql = """
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
        candidate_ids = [row[0] for row in con.execute(candidate_sql, [args.path]).fetchall()]
        buckets = {"discovery": 0, "holdout": 0}
        for identifier in candidate_ids:
            digest = hashlib.sha256(identifier.encode("utf-8")).digest()
            bucket = "holdout" if int.from_bytes(digest[:8], "big") % 5 == 0 else "discovery"
            buckets[bucket] += 1
        result["candidate_filter"] = {
            "count": len(candidate_ids),
            "split": buckets,
            "rule": "SHA256(conversation_id UTF-8) first 8 bytes big-endian mod 5: 0=holdout",
        }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
