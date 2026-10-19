"""SOURCE_PREPARED_NOT_EXECUTED: exactly four targeted pure-parser cases.

All stdout/guard objects below are DECLARED_SYNTHETIC in-memory fixtures, not
actual execution/identity evidence. No raw reads, CLI, process or file APIs.
The parent binds the parser object to the supplied frozen source bytes before
calling qualify_targeted once under its separate CPU release/admission.
"""
from copy import deepcopy
import hashlib
import json


PARSER_SHA256 = "9039c1d0df66210ad9c8fba325bc5e6d9ae10bd67981d7668c18a4576b81b3e4"
FIXED_POINTS = (
    ("AE_GEMM", "77cbc367-150c-418d-85e0-3be23d952498"),
    ("AE_Gaussian", "f9295c5b-29b9-4e6c-9b9c-531c21acfc99"),
    ("AD_GEMM", "fe022881-b5b2-4d99-9229-d7940761fc66"),
    ("AD_Gaussian", "182cfb53-32c3-428d-a964-44e4f47d9727"),
)


def check(ok, why):
    if not ok:
        raise AssertionError(why)


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def rejects(call, reason):
    try:
        call()
    except ValueError as error:
        check(str(error) == reason, "WRONG_REJECTION:" + repr(error))
        return
    raise AssertionError("ACCEPTED_DECLARED_BAD_INPUT:" + reason)


def declared_traffic():
    lines = ["L2_cache_stats_breakdown[GLOBAL_ACC_R][" + outcome + "] = 0"
             for outcome in ("HIT", "HIT_RESERVED", "MISS", "SECTOR_MISS", "TOTAL_ACCESS")]
    for controller in range(20):
        lines.extend(("DRAM[" + str(controller) + "]: DECLARED_SYNTHETIC",
                      "n_cmd=0 n_nop=0 n_act=0 n_pre=0 n_req=0 n_rd=0 n_rd_L2_A=0 n_write=0 n_wr_bk=0"))
    return "\n".join(lines) + "\n"


def declared_block(parser, row, ordinal, total_insns, total_ctas, total_cycles, own_cycles, pib):
    metrics = {
        "kernel_launch_uid": ordinal, "gpu_sim_insn": int(row["active_thread_instructions"]),
        "gpu_tot_sim_insn": total_insns, "gpu_tot_issued_cta": total_ctas,
        "gpu_sim_cycle": own_cycles, "gpu_tot_sim_cycle": total_cycles,
    }
    keys = ("oo_pib_occupancy", "oo_inflight_current", "oo_active_refs", "lower_outstanding",
            "lower_credit_acquired", "lower_credit_released", "oo_lower_created", "oo_lower_issued",
            "oo_lower_responses", "oo_completion_dependency_count", "oo_completion_dependency_closed",
            "oo_valid_hits", "oo_pending_hits", "oo_new_misses", "m4_store_admits", "m4_atomic_admits",
            "m4_bypass_load_admits", "m4_proxy_fence_admits", "m4_source_completions",
            "m4_observation_retires", "oo_physical_allocated", "oo_immediate_reclaims", "oo_final_ref_reclaims")
    metrics.update({"DTC_L1_" + key: 0 for key in keys})
    metrics.update({"DTC_SERVICE_V1_" + key: 0 for key in parser.FINITE})
    metrics.update(DTC_SERVICE_V1_samples=64 * total_cycles, DTC_SERVICE_V1_pib_integral=pib)
    lines = ["kernel_name = " + row["kernel"], "DTC_L1_mode = PAPER_OO"]
    lines.extend(key + " = " + str(value) for key, value in metrics.items())
    return "\n".join(lines) + "\n" + declared_traffic()


def declared_ad_frame(cycles):
    lines = ["DTC_PROGRESSIVE_WAKE_V1_SNAPSHOT_BEGIN version=1 cycle=" + str(cycles) + " sms=64"]
    for sm in range(64):
        lines.append("DTC_PROGRESSIVE_WAKE_V1 sm=" + str(sm) +
                     " broadcasts=0 first_notify_cycle_sum=0 last_notify_cycle_sum=0 span_sum=0")
        lines.extend("DTC_PROGRESSIVE_WAKE_V1_FANOUT sm=" + str(sm) + " bin=" + str(bucket) + " count=0"
                     for bucket in range(33))
        lines.append("DTC_PROGRESSIVE_WAKE_V1_LDST sm=" + str(sm) + " retired=0")
    lines.append("DTC_PROGRESSIVE_WAKE_V1_SNAPSHOT_END version=1")
    return "\n".join(lines) + "\n"


def declared_run(parser, spec, rows):
    """Only GEMM one-kernel declarations; never load or reconstruct real raw."""
    check(spec["workload"] == "GEMM" and len(rows) == 1, "FIXTURE_IS_GEMM_ONLY")
    copies = [{"path": "/DECLARED_SYNTHETIC/config-" + str(i) + ".config", "sha256": entry["sha256"]}
              for i, entry in enumerate(spec["configs"])]
    argv = [spec["runtime_path"], "-trace", spec["trace_list"]]
    for entry in copies:
        argv.extend(("-config", entry["path"]))
    start = dict(point=spec["point"], attempt_uuid=spec["attempt_uuid"], order=spec["order"],
                 source_core=spec["core_commit"], timeout_seconds=7200, retries=0,
                 config_copies=copies, argv=argv, fixture="DECLARED_SYNTHETIC_NOT_ACTUAL_RUN")
    engine = dict(status="PASS_GUARDED_NATURAL_EXIT0", purpose="SIMULATION", root_pid=424242,
                  returncode=0, forced_reason=None, exception=None, identity_pass=True,
                  simulator_starts=1, snapshots=1, owned_children_live=0, unconfirmed_wait_pids=[],
                  ownership=dict(confirmed=[], pending=[], retired=[dict(pid=424242, start_ticks=123)]),
                  owned_process_exit_instances=[dict(pid=424242, start_ticks=123, returncode=0)],
                  owned_process_exits={"424242": 0}, fixture="DECLARED_SYNTHETIC_NOT_ACTUAL_GUARD")
    terminal = dict(returncode=0, forced_reason=None, identity_pass=True, engine=engine)
    prefix = "DECLARED_SYNTHETIC_STDOUT_NOT_ACTUAL_EVIDENCE\n" + spec["expected_embedded_core_version"] + "\n"
    prefix += spec["expected_embedded_framework_version"] + "\n"
    prefix += "\n".join(key + " " + " ".join(value) + " # DECLARED_SYNTHETIC"
                        for key, value in spec["expected_full_effective_options"].items()) + "\n"
    prefix += "performance model initialization complete.\n"
    prefix += "\n".join(("launching memcpy command : " + command if command.startswith("Memcpy")
                         else "Processing kernel " + rows[0]["path"])
                        for command in spec["expected_commands"]) + "\n"
    text = prefix + declared_block(parser, rows[0], 1, spec["expected_instructions"],
                                   spec["expected_CTA"], 13, 13, 91)
    if spec["arm"] == "AD":
        text += declared_ad_frame(13)
    text += "GPGPU-Sim: *** exit detected ***\nGPGPU-Sim: *** simulation thread exiting ***\n"
    return dict(stdout=text.encode(), stderr=b"", run_start=encoded(start),
                run_terminal=encoded(terminal), engine_terminal=encoded(engine))


def checked_report(parser, point, frozen, run):
    result = parser.parse_attempt(point, **frozen, **run)
    check(result["performance_accepted"] is False, "SYNTHETIC_BYTES_MUST_NEVER_ADMIT_PERFORMANCE")
    return result


def case_frozen_contract(parser, frozen):
    prereg = parser.json_bytes(frozen["preregistration"])
    check(tuple((row["point"], row["attempt_uuid"]) for row in prereg["ordered_points"]) == FIXED_POINTS,
          "EXPECTED_FOUR_UUID_METADATA")
    spec, rows, _ = parser.frozen_inputs("AE_GEMM", **frozen)
    check(spec["attempt_uuid"] == FIXED_POINTS[0][1] and len(rows) == 1,
          "EXPECTED_FROZEN_GEMM_METADATA")
    proposal = parser.json_bytes(frozen["science_manifest"])["ordered_arms"][0]
    check(spec["cohort"] == "AG6_DISCOVERY_V2_ORIGINAL174_FOUR_START_ONLY" and
          proposal["cohort"] == "AG6_V2_FOUR_ARM_DISCOVERY_WITH_TWO_QUALIFIED_IMPORTED_BASES" and
          proposal["new_attempt_uuid"] == "UNASSIGNED_BA_ONLY",
          "FIXED_PROPOSAL_TO_ACTUAL_REGISTRATION_LABEL_JOIN")
    changed = dict(frozen)
    changed["preregistration"] = frozen["preregistration"].replace(
        FIXED_POINTS[0][1].encode(), b"00000000-0000-4000-8000-000000000000", 1)
    check(changed["preregistration"] != frozen["preregistration"], "MUTATION_MUST_CHANGE_BYTES")
    rejects(lambda: parser.frozen_inputs("AE_GEMM", **changed), "FROZEN_INPUT_BYTES_CHANGED")
    rejects(lambda: parser.frozen_inputs("BASE_GEMM", **frozen), "FOREIGN_OR_BASE_POINT")
    return "FIXED_HASH_MUTATION_AND_FOREIGN_POINT_REJECTED_FOUR_UUIDS_EXACT"


def case_guard_reserved_boundary(parser, frozen):
    spec, rows, _ = parser.frozen_inputs("AE_GEMM", **frozen)
    run = declared_run(parser, spec, rows)
    engine = parser.json_bytes(run["engine_terminal"])
    engine["ownership"]["pending"] = [{"fixture": "DECLARED_SYNTHETIC_PENDING"}]
    changed = dict(run, engine_terminal=encoded(engine),
                   run_terminal=encoded(dict(returncode=0, forced_reason=None, identity_pass=True, engine=engine)))
    result = checked_report(parser, "AE_GEMM", frozen, changed)
    check(result["scientific_strict_pass"] is False and
          result["failure"] == "ValueError:GUARD_CURRENT_OWNERSHIP_NOT_DRAINED",
          "PENDING_GUARD_MUST_REJECT")
    check(result["budget_observation"]["reserved_start_slots"] == 1 and
          result["budget_observation"]["actual_fork_children_from_guard"] == 1,
          "BAD_TERMINAL_MUST_RETAIN_RESERVED_START_AND_DECLARED_POSITIVE_ROOT_FORK")
    failed = dict(status="STOP_GUARDED_PROCESS", purpose="SIMULATION", root_pid=None, returncode=None,
                  forced_reason="FORK_FAILED:DECLARED_SYNTHETIC", identity_pass=False,
                  owned_children_live=0, simulator_starts=0, actual_fork_children=0)
    for explicit_zero in (True, False):
        candidate = deepcopy(failed)
        if not explicit_zero:
            del candidate["actual_fork_children"]
        changed = dict(run, engine_terminal=encoded(candidate),
                       run_terminal=encoded(dict(returncode=None, forced_reason=candidate["forced_reason"],
                                                 identity_pass=False, engine=candidate)))
        result = checked_report(parser, "AE_GEMM", frozen, changed)
        budget = result["budget_observation"]
        check(result["scientific_strict_pass"] is False and budget["reserved_start_slots"] == 1 and
              budget["failed_or_partial_start_refunded"] is False and
              budget["actual_fork_children_from_guard"] == (0 if explicit_zero else parser.UNAVAILABLE),
              "NO_SLOT_REFUND_NO_INVENTED_ACTUAL_FORK")
    return "PENDING_REJECTED_RESERVED1_FORK0_ONLY_WHEN_EXPLICIT_ELSE_UNAVAILABLE"


def case_final_cumulative_and_off(parser, frozen):
    _, _, dictionary = parser.frozen_inputs("AE_GEMM", **frozen)
    rows = [dict(kernel="DECLARED_FIRST", path="/DECLARED_SYNTHETIC/kernel-1.traceg",
                 active_thread_instructions="2", complete_ctas="1"),
            dict(kernel="DECLARED_SECOND", path="/DECLARED_SYNTHETIC/kernel-2.traceg",
                 active_thread_instructions="3", complete_ctas="1")]
    spec = dict(expected_commands=["kernel-1.traceg", "kernel-2.traceg"],
                expected_instructions=5, expected_CTA=2)
    text = "performance model initialization complete.\n"
    for index, (cycles, own_cycles, pib, instructions) in enumerate(((7, 7, 35, 2), (13, 6, 91, 5)), 1):
        text += "Processing kernel " + rows[index - 1]["path"] + "\n"
        text += declared_block(parser, rows[index - 1], index, instructions, index, cycles, own_cycles, pib)
    text += "GPGPU-Sim: *** exit detected ***\nGPGPU-Sim: *** simulation thread exiting ***\n"
    parsed = parser.parse_full(text, spec, rows)
    off = parser.pipeline_contract(text, "AE", parsed["final_metrics"])
    typed = {row["field"]: row for row in parser.typed_statistics(
        parsed["final_metrics"], parsed["traffic"], off, dictionary)}
    check(parsed["cycles"] == 13 and parsed["final_metrics"]["DTC_SERVICE_V1_samples"] == 832,
          "USE_FINAL_CUMULATIVE_NOT_SUM_7_PLUS_13")
    check(typed["PIB_integral"]["value"] == 91 and typed["mean_PIB_per_SM"]["numerator"] == 91 and
          typed["mean_PIB_per_SM"]["denominator_value"] == 832,
          "NO_SUM_35_PLUS_91_OR_CUMULATIVE_SAMPLE_DOUBLE_COUNT")
    check(typed["AD_notification_span"]["value"] is None and
          typed["AD_notification_span"]["status"] == parser.UNAVAILABLE and
          typed["collection_WB_actual_overlap"]["value"] is None,
          "OFF_OR_UNEXPORTED_NOT_NUMERIC_ZERO")
    return "FINAL13_PIB91_SAMPLES832_OFF_AND_UNEXPORTED_NULL"


def case_exact_options_and_single_arm(parser, frozen):
    runs = {}
    for point in ("AE_GEMM", "AD_GEMM"):
        spec, rows, _ = parser.frozen_inputs(point, **frozen)
        run = declared_run(parser, spec, rows)
        result = checked_report(parser, point, frozen, run)
        check(result["scientific_strict_pass"] is True and len(result["effective_options"]) == 270,
              "DECLARED_MINIMAL_POSITIVE_MUST_REACH_270_AND_ARM_CHECKS:" + point)
        runs[point] = run
    run = runs["AE_GEMM"]
    line = b"-gpgpu_dtc_l1_tag_hash_bankrow 1 # DECLARED_SYNTHETIC\n"
    check(run["stdout"].count(line) == 1, "EXACT_OPTION_MUTATION_LOCATION")
    for changed_stdout in (run["stdout"].replace(line, b"", 1),
                           run["stdout"].replace(
                               b"-gpgpu_dtc_l1_progressive_wakeup 0 # DECLARED_SYNTHETIC\n",
                               b"-gpgpu_dtc_l1_progressive_wakeup 1 # DECLARED_SYNTHETIC\n", 1)):
        check(changed_stdout != run["stdout"], "OPTION_MUTATION_MUST_CHANGE_BYTES")
        result = checked_report(parser, "AE_GEMM", frozen, dict(run, stdout=changed_stdout))
        check(result["scientific_strict_pass"] is False and result["failure"] ==
              "ValueError:all_270_effective_options_exact_population_and_values",
              "MISSING_OPTION_OR_AE_PLUS_AD_MUST_REJECT")
    return "DECLARED_AE_AD_POSITIVES_270_MISSING_OR_JOINT_ON_REJECTED"


def qualify_targeted(parser, *, parser_source, preregistration, science_manifest,
                    kernel_audit, metric_dictionary):
    """Parent-only finite four cases; no runtime admission is implemented here."""
    check(type(parser_source) is bytes and hashlib.sha256(parser_source).hexdigest() == PARSER_SHA256,
          "FROZEN_PARSER_SOURCE_BYTES_REQUIRED_PARENT_MUST_BIND_MODULE")
    frozen = dict(preregistration=preregistration, science_manifest=science_manifest,
                  kernel_audit=kernel_audit, metric_dictionary=metric_dictionary)
    cases = []
    for function in (case_frozen_contract, case_guard_reserved_boundary,
                     case_final_cumulative_and_off, case_exact_options_and_single_arm):
        try:
            result = function(parser, frozen)
        except Exception as error:
            cases.append(dict(case=function.__name__, status="FAIL", error=repr(error)))
            break
        cases.append(dict(case=function.__name__, status="PASS", expected_observed=result))
    return dict(status=("PASS_FOUR_DECLARED_SYNTHETIC_INTERFACE_CASES_ONLY" if
                       len(cases) == 4 and all(row["status"] == "PASS" for row in cases)
                       else "FAIL_TARGETED_PARSER_QUALIFICATION"),
                expected_case_count=4, actual_case_count=len(cases), cases=cases,
                parser_source_sha256=PARSER_SHA256,
                fixture_scope="DECLARED_SYNTHETIC_NOT_ACTUAL_STDOUT_GUARD_OR_SCIENTIFIC_EVIDENCE",
                actual_parser_execution_status="CALLER_MUST_RECORD_ACTUAL_RELEASE_START_TERMINAL",
                real_stdout_controls_read=0, new_simulations_started=0,
                native_numeric_value_or_actual_identity_qualified=False)
