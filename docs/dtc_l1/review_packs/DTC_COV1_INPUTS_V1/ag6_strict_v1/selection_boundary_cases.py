"""SOURCE_PREPARED_NOT_EXECUTED: four finite pure selection boundary cases.

Any receipt generated here is DECLARED_SYNTHETIC, never actual AG6 evidence.
No imports of production modules, CLI, I/O, process or execution permissions.
Parent separately binds source/imports and admits a future call, if needed.
"""
from fractions import Fraction
import json


def check(ok, reason):
    if not ok:
        raise AssertionError(reason)


def declared_receipts(selection, preregistration, baseline_speed=False):
    specs = selection.load(preregistration)["ordered_points"]
    rows = []
    for spec in specs:
        base = spec["imported_BASE_cycles"]
        cycles = base if baseline_speed else base // 2
        value = dict(point=spec["point"], arm=spec["arm"], workload=spec["workload"],
            attempt_uuid=spec["attempt_uuid"], status="PASS_ACTUAL_REGISTERED_AG6_FULL_STRICT_EVIDENCE",
            performance_accepted=True, scientific_strict_pass=True,
            acceptance_scope="ACTUAL_OWN_SOURCE_BOUND_REGISTERED_ATTEMPT", cycles=cycles, BASE_cycles=base,
            speedup_exact=dict(numerator=base, denominator=cycles), kernel_count=spec["expected_kernels"],
            CTA=spec["expected_CTA"], active_instructions=spec["expected_instructions"],
            input_runtime_identity_sha256="0" * 64, mapping_closure_sha256="0" * 64,
            runtime_resource_monitor_sha256="0" * 64, final_resource_sha256="0" * 64,
            publication_head="0" * 40, resource_samples=1,
            fixture="DECLARED_SYNTHETIC_NO_ACTUAL_PROVENANCE")
        rows.append(json.dumps(value).encode())
    return rows


def case_thresholds(selection, frozen):
    floor, product = Fraction(49, 50), Fraction(51, 50)**2
    epsilon = Fraction(1, 10**24)
    other = [Fraction(1), Fraction(1)]
    exact = selection._arithmetic({"AE": [floor, product / floor], "AD": other})
    check(exact["choice"] == "AE" and exact["arms"]["AE"]["qualified"], "INCLUSIVE_MIN_GM_BOUNDARIES")
    low_min = selection._arithmetic({"AE": [floor - epsilon, product / (floor - epsilon)], "AD": other})
    check(not low_min["arms"]["AE"]["minimum_pass"] and low_min["choice"] == "O", "EXACT_BELOW_MINIMUM")
    low_gm = selection._arithmetic({"AE": [Fraction(1), product - epsilon], "AD": other})
    check(not low_gm["arms"]["AE"]["geomean_pass"] and low_gm["choice"] == "O", "EXACT_BELOW_GEOMEAN")


def case_tie_boundary(selection, frozen):
    ae = Fraction(51, 50)
    limit, epsilon = Fraction(201, 200), Fraction(1, 10**24)
    for difference, expected, tie in ((-epsilon, "AE", True), (Fraction(0), "AD", False),
                                      (epsilon, "AD", False)):
        ad = ae * (limit + difference)
        result = selection._arithmetic({"AE": [ae, ae], "AD": [ad, ad]})
        check(result["choice"] == expected and result["tie_applied"] is tie,
              "STRICT_0_POINT_5_PERCENT_RATIO_BOUNDARY")


def case_four_complete_before_nomination(selection, frozen):
    rows = declared_receipts(selection, frozen["preregistration"])
    bases = {key: row[0] for key, row in selection.BASES.items()}
    partial = selection.select_v2(rows[:2], base_cycles=bases, **frozen)
    check(partial["status"] == "PROVISIONAL_O_WITH_INCOMPLETE_OPT_SCREEN" and
          partial["final_F"] is None and partial["nominated_arm"] is None and
          partial["arm_evaluations"] is None and len(partial["evidence"]) == 2 and
          all(row["accepted"] for row in partial["evidence"]), "NO_COMPLETE_AE_ONLY_PROMOTION")
    complete = selection.select_v2(rows, base_cycles=bases, **frozen)
    check(complete["complete_four_point_screen"] and complete["final_F"] == "AE" and
          complete["actual_provenance_requires_parent_immutable_join"] and
          complete["old_selection_write_performed"] is False, "COMPLETE_ARITHMETIC_RESULT_ONLY")


def case_no_arm_or_invalid_receipt(selection, frozen):
    rows = declared_receipts(selection, frozen["preregistration"], baseline_speed=True)
    bases = {key: row[0] for key, row in selection.BASES.items()}
    complete = selection.select_v2(rows, base_cycles=bases, **frozen)
    check(complete["complete_four_point_screen"] and complete["final_F"] == "O" and
          complete["nominated_arm"] is None, "COMPLETE_VALID_NEGATIVE_RESULTS_SELECT_O")
    for mutation in ("FLOAT_CYCLES", "WRONG_UUID"):
        wrong = selection.load(rows[0])
        if mutation == "FLOAT_CYCLES":
            wrong["cycles"] = float(wrong["cycles"])
        else:
            wrong["attempt_uuid"] = "00000000-0000-4000-8000-000000000000"
        report = selection.select_v2([json.dumps(wrong).encode(), *rows[1:]], base_cycles=bases, **frozen)
        check(report["status"] == "PROVISIONAL_O_WITH_INCOMPLETE_OPT_SCREEN" and
              report["final_F"] is None and report["nominated_arm"] is None and report["issues"],
              "FAILED_FOURTH_GATE_CANNOT_NOMINATE:" + mutation)


def run_boundary_cases(selection, *, preregistration, base_decision, old_selection):
    """Pure four-case callable; all resulting fixture decisions are synthetic."""
    frozen = dict(preregistration=preregistration, base_decision=base_decision, old_selection=old_selection)
    cases = []
    for function in (case_thresholds, case_tie_boundary, case_four_complete_before_nomination,
                     case_no_arm_or_invalid_receipt):
        try:
            function(selection, frozen)
        except Exception as error:
            cases.append(dict(case=function.__name__, status="FAIL", error=repr(error)))
            break
        cases.append(dict(case=function.__name__, status="PASS"))
    return dict(status="PASS_FOUR_PURE_SELECTION_BOUNDARIES_ONLY" if len(cases) == 4 and
                all(row["status"] == "PASS" for row in cases) else "FAIL_SELECTION_BOUNDARIES",
                cases=cases, actual_case_count=len(cases), expected_case_count=4,
                fixture_scope="DECLARED_SYNTHETIC_NOT_ACTUAL_AG6_SELECTION_OR_PROVENANCE",
                actual_AG6_result_qualified=False, old_selection_written=False, simulation_starts=0)
