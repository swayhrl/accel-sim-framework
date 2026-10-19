"""SOURCE_PREPARED_NOT_EXECUTED: pure AG6 four-point strict/statistics parser.

No common/CLI import, filesystem/process/network/clock access or write API.
Caller provides complete bytes plus separately published actual evidence
closure. A scientific PASS here cannot establish actual identity/authority.
Scientific checks derive from frozen AG4 strict_screen.py at d8d0401d.
"""
import csv
import hashlib
import io
import json
import re


PREREG_SHA256 = "844591f608ff99203b22f7f7cb958e1c7633726c3e351da7b7407dd53edee38e"
SCIENCE_SHA256 = "5e06ba311cb40bfde23153c6760df878a38d4d2e4bbefb2f793b424df203dd15"
AUDIT_SHA256 = "164157917d13768ae0ae4dbdd545b761d0a9bbd5e57c5b5480bb0bac7bed7ef5"
DICTIONARY_SHA256 = "5d24ac7aa85ca30eb9defd51c420876f4a4a4f2475ffe65346e1c355e38f47ec"
POINTS = (
    ("AE_GEMM", "77cbc367-150c-418d-85e0-3be23d952498"),
    ("AE_Gaussian", "f9295c5b-29b9-4e6c-9b9c-531c21acfc99"),
    ("AD_GEMM", "fe022881-b5b2-4d99-9229-d7940761fc66"),
    ("AD_Gaussian", "182cfb53-32c3-428d-a964-44e4f47d9727"),
)
FINITE = ("samples", "pib_integral", "physical_integral", "collected_sectors",
          "fully_ready_to_complete_sum", "retired", "ready_to_collect_sum",
          "collection_cycles", "wb_wait", "map_loss_to_free_sum", "map_loss_to_free_count")
FORBIDDEN = r"assertion failed|fatal error|deadlock detected|segmentation fault|core dumped|output mismatch"
UNAVAILABLE = "UNAVAILABLE_NOT_ZERO"


def require(ok, why):
    if not ok:
        raise ValueError(why)


def digest(value):
    require(type(value) is bytes, "EXACT_BYTES_REQUIRED")
    return hashlib.sha256(value).hexdigest()


def decoded(value):
    require(type(value) is bytes, "EXACT_BYTES_REQUIRED")
    return value.decode("utf-8", errors="strict")


def json_bytes(value):
    def pairs(items):
        result = {}
        for key, entry in items:
            require(key not in result, "DUPLICATE_JSON_KEY:" + key)
            result[key] = entry
        return result
    return json.loads(decoded(value), object_pairs_hook=pairs)


def echo(text):
    result = {}
    for line in text.splitlines():
        match = re.match(r"^(-\S+)\s+(.*?)\s*#", line)
        if match:
            key, values = match[1], match[2].split()
            require(key not in result or result[key] == values,
                    "conflicting_effective_option:" + key)
            result[key] = values
    return result


def numeric(block):
    result = {}
    for key, value in re.findall(r"^\s*(\w+)\s*=\s*(\d+)\s*$", block, re.M):
        if key in result:
            require(not key.startswith(("DTC_", "gpu_", "gpgpu_n_mem_", "icnt_total_")),
                    "duplicate_numeric_metric:" + key)
        result[key] = int(value)
    return result


def traffic(block):
    buckets = {}
    for kind, outcome, value in re.findall(
            r"^\s*L2_cache_stats_breakdown\[(\w+)\]\[(\w+)\]\s*=\s*(\d+)\s*$", block, re.M):
        key = kind + ":" + outcome
        require(key not in buckets, "duplicate_L2_bucket")
        buckets[key] = int(value)
    dram = re.findall(r"^DRAM\[(\d+)\]:[^\n]*\n(n_cmd=[^\n]+)", block, re.M)
    require(len(dram) == 20 and {int(i) for i, _ in dram} == set(range(20)),
            "DRAM_population_20_controllers")
    controllers = {}
    for index, line in dram:
        entries = re.findall(r"(n_cmd|n_nop|n_act|n_pre|n_req|n_rd|n_rd_L2_A|n_write|n_wr_bk)=(\d+)", line)
        row = {key: int(value) for key, value in entries}
        require(len(row) == len(entries), "duplicate_DRAM_field")
        controllers[str(int(index))] = row
    reads = sum(buckets["GLOBAL_ACC_R:" + key] for key in
                ("HIT", "HIT_RESERVED", "MISS", "SECTOR_MISS"))
    require(reads == buckets["GLOBAL_ACC_R:TOTAL_ACCESS"], "L2_accepted_read_bucket_partition")
    rd = sum(row["n_rd"] + row["n_rd_L2_A"] for row in controllers.values())
    wr = sum(row["n_write"] + row["n_wr_bk"] for row in controllers.values())
    return dict(L2_buckets=buckets, L2_accepted_read_32B_sectors=reads,
                L2_read_payload_bytes=32 * reads, DRAM_controllers=controllers,
                DRAM_atom_bytes=32, DRAM_issued_read_atoms=rd, DRAM_issued_write_atoms=wr,
                DRAM_read_payload_bytes=32 * rd, DRAM_write_payload_bytes=32 * wr,
                DRAM_n_ref_event="UNAVAILABLE_INHERITED_UNINITIALIZED_FIELD_RAW_PRESERVED")


def frozen_inputs(point, preregistration, science_manifest, kernel_audit, metric_dictionary):
    for content, expected in ((preregistration, PREREG_SHA256), (science_manifest, SCIENCE_SHA256),
                              (kernel_audit, AUDIT_SHA256), (metric_dictionary, DICTIONARY_SHA256)):
        require(digest(content) == expected, "FROZEN_INPUT_BYTES_CHANGED")
    prereg, science = json_bytes(preregistration), json_bytes(science_manifest)
    require(tuple((row["point"], row["attempt_uuid"]) for row in prereg["ordered_points"]) == POINTS,
            "ONLY_FOUR_REGISTERED_UUIDS")
    require(prereg["new_start_cap"] == 4 and science["new_start_cap"] == 4,
            "FOUR_POINT_COHORT_REQUIRED")
    require(prereg["typed_metrics"] == science["typed_metrics"], "TYPED_SCIENCE_CONTRACT_CHANGED")
    require(point in dict(POINTS), "FOREIGN_OR_BASE_POINT")
    spec = next(row for row in prereg["ordered_points"] if row["point"] == point)
    proposal = next(row for row in science["ordered_arms"] if row["point"] == point)
    # Proposal leaves new_attempt_uuid unassigned; compare every other science
    # field with the actual preregistration, including exact270 effective options.
    require(all(spec[key] == value for key, value in proposal.items() if key != "new_attempt_uuid"),
            "PREREG_SCIENCE_FIELD_MISMATCH")
    require(spec["attempt_uuid"] == spec["new_attempt_uuid"] == dict(POINTS)[point],
            "POINT_UUID_CHANGED")
    audit = list(csv.DictReader(io.StringIO(decoded(kernel_audit)), delimiter="\t"))
    rows = sorted((row for row in audit if row["workload"].lower() == spec["workload"].lower()),
                  key=lambda row: int(row["ordinal"]))
    require(len(rows) == spec["expected_kernels"] and
            [int(row["ordinal"]) for row in rows] == list(range(1, len(rows) + 1)),
            "FROZEN_ORDERED_KERNEL_POPULATION")
    dictionary = list(csv.DictReader(io.StringIO(decoded(metric_dictionary)), delimiter="\t"))
    require(len({row["field"] for row in dictionary}) == len(dictionary), "DUPLICATE_TYPED_FIELD")
    return spec, rows, dictionary


def parse_full(text, spec, expected):
    names = list(re.finditer(r"^kernel_name = (\S+)[ \t]*$", text, re.M))
    require(len(names) == len(expected), "full_ordered_kernel_count")
    require([match[1] for match in names] == [row["kernel"] for row in expected],
            "full_ordered_kernel_names")
    commands = []
    for line in text.splitlines():
        if line.startswith("Processing kernel "):
            commands.append(line[len("Processing kernel "):].rsplit("/", 1)[-1])
        elif line.startswith("launching memcpy command : "):
            commands.append(line[len("launching memcpy command : "):])
    require(commands == spec["expected_commands"], "all_original_commands_order_and_memcpy")
    require(re.findall(r"^Processing kernel (\S+)$", text, re.M) == [row["path"] for row in expected],
            "exact_original_member_paths")
    require(text.count("GPGPU-Sim: *** exit detected ***") == 1, "one_natural_exit_marker")
    require(text.count("GPGPU-Sim: *** simulation thread exiting ***") == 1,
            "one_simulation_thread_exit_marker")
    require("performance model initialization complete." in text, "real_model_initialization")
    require(not re.search(FORBIDDEN, text, re.I), "forbidden_runtime_signature")
    require(not re.search(r"^DTC_INVALIDATE_V1_(SNAPSHOT|SUMMARY)", text, re.M),
            "K0_has_no_K1_only_export")
    blocks = [text[match.start():names[i + 1].start() if i + 1 < len(names) else len(text)]
              for i, match in enumerate(names)]
    metrics, kernels = [], []
    insns = ctas = 0
    previous = None
    for ordinal, (block, row) in enumerate(zip(blocks, expected), 1):
        data = numeric(block)
        insns += int(row["active_thread_instructions"])
        ctas += int(row["complete_ctas"])
        require(data["kernel_launch_uid"] == ordinal, "ordered_launch_UID")
        require(data["gpu_sim_insn"] == int(row["active_thread_instructions"]) and
                data["gpu_tot_sim_insn"] == insns and data["gpu_tot_issued_cta"] == ctas,
                "per_kernel_full_instructions_CTA:" + str(ordinal))
        require("DTC_L1_mode = PAPER_OO" in block, "OO_mode")
        value = lambda key: data["DTC_L1_" + key]
        finite = lambda key: data["DTC_SERVICE_V1_" + key]
        require(all(value(key) == 0 for key in ("oo_pib_occupancy", "oo_inflight_current",
                    "oo_active_refs", "lower_outstanding")), "terminal_ownership_credit_drain")
        require(value("lower_credit_acquired") == value("lower_credit_released") ==
                value("oo_lower_created") == value("oo_lower_issued") == value("oo_lower_responses"),
                "lower_create_inject_response_credit_conservation")
        require(value("oo_completion_dependency_count") == value("oo_completion_dependency_closed") ==
                value("oo_valid_hits") + value("oo_pending_hits") + value("oo_new_misses"),
                "Ref_dependency_closed_population")
        require(sum(value("m4_" + key + "_admits") for key in
                    ("store", "atomic", "bypass_load", "proxy_fence")) ==
                value("m4_source_completions") == value("m4_observation_retires"),
                "source_sidecar_conservation")
        require(0 <= value("oo_physical_allocated") <= 640 * 64, "physical_640_per_SM_capacity")
        require(value("oo_new_misses") == value("oo_physical_allocated") +
                value("oo_immediate_reclaims") + value("oo_final_ref_reclaims"),
                "K0_physical_allocation_conservation")
        require(all("DTC_SERVICE_V1_" + key in data for key in FINITE), "all_common_finite_fields_present")
        require(finite("samples") == 64 * data["gpu_tot_sim_cycle"], "finite_population_64SM")
        require(finite("fully_ready_to_complete_sum") == finite("ready_to_collect_sum") +
                finite("collection_cycles") + finite("wb_wait"), "finite_postready_scope_decomposition")
        require(finite("map_loss_to_free_count") == value("oo_immediate_reclaims") +
                value("oo_final_ref_reclaims"), "K0_map_loss_reclaim_population")
        if previous is not None:
            require(all(finite(key) >= previous["DTC_SERVICE_V1_" + key] for key in FINITE),
                    "cumulative_finite_monotonic")
        previous = data
        metrics.append(data)
        kernels.append(dict(ordinal=ordinal, kernel=row["kernel"], cycles=data["gpu_sim_cycle"],
                            total_cycles=data["gpu_tot_sim_cycle"], active_instructions=data["gpu_sim_insn"],
                            cumulative_CTA=data["gpu_tot_issued_cta"]))
    require(insns == spec["expected_instructions"] and ctas == spec["expected_CTA"],
            "whole_input_instruction_CTA_totals")
    require(type(metrics[-1]["gpu_tot_sim_cycle"]) is int and metrics[-1]["gpu_tot_sim_cycle"] > 0,
            "positive_integer_GPU_cycles")
    return dict(kernel_count=len(expected), CTA=ctas, active_instructions=insns,
                cycles=metrics[-1]["gpu_tot_sim_cycle"], final_metrics=metrics[-1],
                kernels=kernels, traffic=traffic(blocks[-1]), effective_options=echo(text))


def pipeline_contract(text, arm, final, sms=64):
    require("DTC_COLLECT_WB_PIPELINE_V1" not in text, "AC_not_in_AG6")
    if arm != "AD":
        require("DTC_PROGRESSIVE_WAKE_V1" not in text, "AD_OFF_no_ON_only_export")
        return dict(status="UNAVAILABLE_OFF_NOT_PRINTED", direct_comparison=False)
    frames = list(re.finditer(r"^DTC_PROGRESSIVE_WAKE_V1_SNAPSHOT_BEGIN .*?^DTC_PROGRESSIVE_WAKE_V1_SNAPSHOT_END version=1$",
                              text, re.M | re.S))
    require(bool(frames), "AD_ON_complete_normal_export")
    require(len(frames) == len(re.findall(r"^DTC_PROGRESSIVE_WAKE_V1_SNAPSHOT_BEGIN ", text, re.M)) ==
            len(re.findall(r"^DTC_PROGRESSIVE_WAKE_V1_SNAPSHOT_END version=1$", text, re.M)),
            "AD_no_partial_extra_frame")
    summary, fanout, ldst = {}, {}, {}
    for line in frames[-1][0].splitlines():
        pairs = re.findall(r"(\w+)=(\d+)", line)
        values = {key: int(value) for key, value in pairs}
        require(len(values) == len(pairs), "AD_duplicate_field")
        if line.startswith("DTC_PROGRESSIVE_WAKE_V1_SNAPSHOT_BEGIN "):
            require(values["cycle"] == final["gpu_tot_sim_cycle"] and values["sms"] == sms,
                    "AD_public_frame_cycle_population")
        elif line.startswith("DTC_PROGRESSIVE_WAKE_V1 "):
            sm = values["sm"]
            require(sm not in summary, "AD_duplicate_summary")
            summary[sm] = values
        elif line.startswith("DTC_PROGRESSIVE_WAKE_V1_FANOUT "):
            key = (values["sm"], values["bin"])
            require(key not in fanout, "AD_duplicate_fanout")
            fanout[key] = values["count"]
        elif line.startswith("DTC_PROGRESSIVE_WAKE_V1_LDST "):
            sm = values["sm"]
            require(sm not in ldst, "AD_duplicate_LDST")
            ldst[sm] = values
    require(set(summary) == set(ldst) == set(range(sms)), "AD_all_SM_rows")
    require(set(fanout) == {(sm, bucket) for sm in range(sms) for bucket in range(33)},
            "AD_all_SM_fanout_bins")
    for sm, row in summary.items():
        require(sum(fanout[sm, bucket] for bucket in range(33)) == row["broadcasts"],
                "AD_fanout_partition")
        require(row["last_notify_cycle_sum"] - row["first_notify_cycle_sum"] == row["span_sum"],
                "AD_span_conservation")
    require(sum(row["retired"] for row in ldst.values()) == final["DTC_SERVICE_V1_retired"],
            "AD_common_retire_population_join")
    return dict(status="PASS_AD_ON_ONLY_DIAGNOSTIC", direct_comparison=False, summary=summary,
                fanout={str(sm) + ":" + str(bucket): value for (sm, bucket), value in fanout.items()},
                ldst=ldst, post_ready_condition="AD_OWN_NOTIFIED_READY_DIFFERENT_FROM_BASE_BROADCAST_DONE",
                OFF=UNAVAILABLE)


def guard_contract(start, terminal, engine, spec):
    require(start["point"] == spec["point"] and start["attempt_uuid"] == spec["attempt_uuid"] and
            start["order"] == spec["order"], "ACTUAL_START_NOT_THIS_RESERVED_POINT")
    require(start["source_core"] == spec["core_commit"] and start["timeout_seconds"] == 7200 and
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


def typed_statistics(final, traffic_data, pipeline, dictionary):
    """One final cumulative snapshot; missing/OFF never becomes numeric zero."""
    output = []
    for definition in dictionary:
        source = definition["source_key"]
        value = None
        if source.startswith("traffic."):
            value = traffic_data.get(source[len("traffic."):])
        elif source.startswith("DTC_PROGRESSIVE_WAKE_V1"):
            if pipeline["status"] == "PASS_AD_ON_ONLY_DIAGNOSTIC":
                if source == "DTC_PROGRESSIVE_WAKE_V1_FANOUT":
                    value = pipeline["fanout"]
                else:
                    prefix, _, key = source.partition(" ")
                    population = pipeline["ldst"] if prefix.endswith("_LDST") else pipeline["summary"]
                    if key and all(key in row for row in population.values()):
                        value = sum(row[key] for row in population.values())
        elif source != "UNAVAILABLE":
            value = final.get(source)
        result = dict(definition)
        if value is None:
            result.update(status=UNAVAILABLE, value=None)
        elif definition["denominator"] == "1":
            result.update(status="MEASURED_IN_SUPPLIED_FINAL_SNAPSHOT", value=value)
        else:
            denominator = final.get(definition["denominator"])
            if denominator is None:
                result.update(status=UNAVAILABLE, value=None)
            elif denominator == 0:
                result.update(status="UNDEFINED_ZERO_DENOMINATOR", value=None,
                              numerator=value, denominator_value=0)
            else:
                result.update(status="MEASURED_EXACT_RATIO_IN_SUPPLIED_FINAL_SNAPSHOT", value=None,
                              numerator=value, denominator_value=denominator)
        output.append(result)
    return output


def parse_attempt(point, *, stdout, stderr, run_start, run_terminal, engine_terminal,
                  preregistration, science_manifest, kernel_audit, metric_dictionary):
    """Pure bytes -> report; failures keep cycles unavailable and consume no retry.

    run_start/terminal and engine_terminal are actual receipt byte strings. The
    sole coordinator independently publishes their SHA256 and validates all
    actual identity/config/input/capability/resource evidence before consuming
    this scientific result. This function never creates that proof or budget.
    """
    report = dict(point=point, status="HOLD_AG6_STRICT_FAILED", scientific_strict_pass=False,
                  performance_accepted=False, cycles=UNAVAILABLE,
                  acceptance_scope="SUPPLIED_BYTES_SCIENTIFIC_CHECKS_ONLY",
                  parent_identity_authority_resource_closure_required=True,
                  no_dispatch_or_retry_permission=True,
                  common_metric_scope="LAST_CUMULATIVE_FINAL_SNAPSHOT_NOT_SUM_OF_KERNEL_SNAPSHOTS")
    try:
        spec, expected, dictionary = frozen_inputs(point, preregistration, science_manifest,
                                                   kernel_audit, metric_dictionary)
        report.update(attempt_uuid=spec["attempt_uuid"], arm=spec["arm"], workload=spec["workload"])
        start = json_bytes(run_start)
        require(start["attempt_uuid"] == spec["attempt_uuid"] and start["point"] == point,
                "FOREIGN_START_CANNOT_CONSUME_THIS_RESERVATION")
        # RUN_START is the conservative slot boundary, even if the later real
        # fork fails. Do not refund this slot because strict fails or root=None.
        report["budget_observation"] = dict(reserved_start_slots=1,
            actual_fork_children_from_guard=UNAVAILABLE,
            actual_fork_count_definition="ROOT_PID_PROVES_ONE_DIRECT_FORK_ELSE_ONLY_EXPLICIT_GUARD_FIELD",
            failed_or_partial_start_refunded=False, new_simulations_launched_by_parser=0)
        report["receipt_sha256"] = dict(stdout=digest(stdout), stderr=digest(stderr),
            RUN_START=digest(run_start), RUN_TERMINAL=digest(run_terminal),
            ENGINE_TERMINAL=digest(engine_terminal))
        terminal, engine = json_bytes(run_terminal), json_bytes(engine_terminal)
        fork_field = engine.get("actual_fork_children")
        actual_children = (1 if type(engine.get("root_pid")) is int and engine["root_pid"] > 0
                           else fork_field if type(fork_field) is int and fork_field in (0, 1)
                           else UNAVAILABLE)
        report["budget_observation"]["actual_fork_children_from_guard"] = actual_children
        guard = guard_contract(start, terminal, engine, spec)
        text = decoded(stdout)
        require(not re.search(FORBIDDEN, decoded(stderr), re.I), "forbidden_stderr_runtime_signature")
        require(spec["expected_embedded_core_version"] in text, "actual_Core_embedded_version")
        require(spec["expected_embedded_framework_version"] in text, "actual_Framework_embedded_version")
        parsed = parse_full(text, spec, expected)
        options = parsed["effective_options"]
        require(len(options) == 270 and options == spec["expected_full_effective_options"],
                "all_270_effective_options_exact_population_and_values")
        fixed = {"mode": "3", "invalidate_on_source_event": "0", "finite_service": "1",
                 "oo_pib_entries": "128", "logical_sets": "64", "logical_ways": "8",
                 "physical_lines": "640", "allocation_width": "4",
                 "tag_hash_bankrow": "1" if spec["arm"] == "AE" else "0",
                 "progressive_wakeup": "1" if spec["arm"] == "AD" else "0"}
        require(all(options["-gpgpu_dtc_l1_" + key] == [value] for key, value in fixed.items()),
                "K0_OO128_64x8_640_AE_ONLY_OR_AD_ONLY")
        pipeline = pipeline_contract(text, spec["arm"], parsed["final_metrics"])
        report.update(status="PASS_AG6_SUPPLIED_BYTES_SCIENTIFIC_STRICT_ONLY", scientific_strict_pass=True,
            cycles=parsed["cycles"], CTA=parsed["CTA"], active_instructions=parsed["active_instructions"],
            kernels=parsed["kernels"], kernel_count=parsed["kernel_count"],
            final_metrics=parsed["final_metrics"], traffic=parsed["traffic"],
            effective_options=options, guard_terminal_check=guard, AD_diagnostic=pipeline,
            typed_statistics=typed_statistics(parsed["final_metrics"], parsed["traffic"], pipeline, dictionary),
            K1_only_fields="UNAVAILABLE_K0_NOT_PRINTED", numeric_load_values="UNAVAILABLE",
            actual_collection_WB_overlap="UNAVAILABLE_NO_DIRECT_COUNTER",
            private_terminal_generation_sector_receipts="UNAVAILABLE")
    except (ValueError, KeyError, TypeError, IndexError, StopIteration) as error:
        report["failure"] = type(error).__name__ + ":" + str(error)
    return report
