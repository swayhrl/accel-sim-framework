"""Exact original guard terminal validator; only approved wall constant differs. No receipt rewriting."""
def require(value, reason):
    if not value:
        raise ValueError(reason)

def guard_contract(start, terminal, engine, spec):
    require(start["point"] == spec["point"] and start["attempt_uuid"] == spec["attempt_uuid"] and
            start["order"] == spec["order"], "ACTUAL_START_NOT_THIS_RESERVED_POINT")
    require(start["source_core"] == spec["core_commit"] and start["timeout_seconds"] == 21600 and
            start["retries"] == 0, "ACTUAL_START_SOURCE_OR_BOUND_CHANGED")
    copies = start["config_copies"]
    require(len(copies) == len(spec["configs"]) and
            [entry["sha256"] for entry in copies] == [entry["sha256"] for entry in spec["configs"]],
            "ACTUAL_CONFIG_COPY_ORDER_AND_DIGESTS")
    require(len({entry["path"] for entry in copies}) == len(copies), "DUPLICATE_CONFIG_COPY_PATH")
    argv = [spec["runtime_path"], "-trace", spec["trace_list"]]
    for entry in copies:
        argv.extend(("-config", entry["path"]))
    require(start["argv"] == argv, "ACTUAL_START_EXACT_ARGV")
    require(terminal["engine"] == engine, "WRAPPER_ENGINE_RECEIPT_DISAGREES")
    require(terminal["returncode"] == 0 and terminal["forced_reason"] is None and
            terminal["identity_pass"] is True, "WRAPPER_NATURAL_EXIT0_AND_IDENTITY")
    require(engine["status"] == "PASS_GUARDED_NATURAL_EXIT0" and engine["purpose"] == "SIMULATION" and
            engine["returncode"] == 0 and engine["forced_reason"] is None and
            engine["exception"] is None and engine["identity_pass"] is True,
            "CANONICAL_GUARD_NATURAL_EXIT0_AND_IDENTITY")
    require(type(engine["root_pid"]) is int and engine["root_pid"] > 0 and
            engine["simulator_starts"] == 1 and engine["snapshots"] > 0,
            "ACTUAL_GUARDED_SIMULATOR_ROOT_REQUIRED")
    require(engine["owned_children_live"] == 0 and not engine["unconfirmed_wait_pids"] and
            not engine["ownership"]["confirmed"] and not engine["ownership"]["pending"],
            "GUARD_CURRENT_OWNERSHIP_NOT_DRAINED")
    exits = engine["owned_process_exit_instances"]
    keys = [(row["pid"], row["start_ticks"]) for row in exits]
    require(bool(exits) and len(keys) == len(set(keys)) and
            all(type(row["pid"]) is int and type(row["start_ticks"]) is int and
                row["start_ticks"] > 0 and row["returncode"] == 0 for row in exits),
            "ACTUAL_EXIT_INSTANCE_POPULATION")
    retired = {(row["pid"], row["start_ticks"]) for row in engine["ownership"]["retired"]}
    require(set(keys) == retired, "GUARD_RETIRED_EXIT_INSTANCE_JOIN")
    root = [row for row in exits if row["pid"] == engine["root_pid"]]
    require(len(root) == 1 and root[0]["returncode"] == 0, "NATURAL_ROOT_EXIT_INSTANCE")
    # Canonical exits is keyed only by PID and can lose a retired generation.
    # The source-bound instance list, not that PID-only dictionary, is primary.
    require(all(code == 0 for code in engine["owned_process_exits"].values()),
            "NONZERO_OWNED_PROCESS_EXIT")
    return dict(status="PASS_SUPPLIED_CANONICAL_GUARD_TERMINAL_FIELDS_ONLY",
                root_instance=root[0], exit_instances=exits,
                runtime_mapping_proof="PARENT_IMMUTABLE_CLOSURE_REQUIRED_NOT_PROVEN_BY_JSON")
