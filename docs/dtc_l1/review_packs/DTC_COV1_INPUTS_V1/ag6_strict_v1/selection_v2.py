"""SOURCE_PREPARED_NOT_EXECUTED: pure fixed four-point AG6 global selection.

Only supplied immutable bytes/integers are consumed. No I/O, CLI, launch,
selection-file mutation or runtime permission. The parent independently binds
actual accepted STRICT receipt bytes to their published attempt evidence.
"""
from fractions import Fraction
import hashlib
import json


PREREG_SHA256 = "844591f608ff99203b22f7f7cb958e1c7633726c3e351da7b7407dd53edee38e"
BASE_DECISION_SHA256 = "a8e834093bc3da494190798cc87eee6c39edbe34efa04d38a5ab6771cea37f9a"
OLD_SELECTION_SHA256 = "d4c9011017f6720b4740c80f6abaeb435fbbc30c702a1c60913ad8bb8c796bf3"
POINTS = (
    ("AE_GEMM", "AE", "GEMM", "77cbc367-150c-418d-85e0-3be23d952498"),
    ("AE_Gaussian", "AE", "Gaussian", "f9295c5b-29b9-4e6c-9b9c-531c21acfc99"),
    ("AD_GEMM", "AD", "GEMM", "fe022881-b5b2-4d99-9229-d7940761fc66"),
    ("AD_Gaussian", "AD", "Gaussian", "182cfb53-32c3-428d-a964-44e4f47d9727"),
)
BASES = {"GEMM": (1071405, "8b6006aa-610e-41cf-82f0-135f80e449cf"),
         "Gaussian": (3278356, "87daf914-1730-4012-8053-7cb3c9536636")}
MINIMUM = Fraction(49, 50)
MINIMUM_PRODUCT = Fraction(51, 50)**2
TIE_PRODUCT_RATIO = Fraction(201, 200)**2


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def sha(value):
    require(type(value) is bytes, "EXACT_IMMUTABLE_BYTES_REQUIRED")
    return hashlib.sha256(value).hexdigest()


def load(value):
    def unique(pairs):
        result = {}
        for key, entry in pairs:
            require(key not in result, "DUPLICATE_JSON_FIELD:" + key)
            result[key] = entry
        return result
    require(type(value) is bytes, "EXACT_IMMUTABLE_BYTES_REQUIRED")
    return json.loads(value.decode("utf-8"), object_pairs_hook=unique)


def ratio(value):
    return {"numerator": value.numerator, "denominator": value.denominator}


def _arithmetic(speeds):
    """Exact arithmetic only, never an actual receipt/provenance qualification."""
    require(set(speeds) == {"AE", "AD"} and all(len(speeds[arm]) == 2 for arm in speeds),
            "BOTH_TWO_INPUT_ARMS_REQUIRED")
    require(all(type(value) is Fraction and value > 0 for values in speeds.values() for value in values),
            "POSITIVE_EXACT_FRACTIONS_REQUIRED")
    products = {arm: values[0] * values[1] for arm, values in speeds.items()}
    evaluations = {}
    for arm in ("AE", "AD"):
        minimum = min(speeds[arm])
        qualified = minimum >= MINIMUM and products[arm] >= MINIMUM_PRODUCT
        evaluations[arm] = dict(per_input_speedups=[ratio(value) for value in speeds[arm]],
            minimum=ratio(minimum), speedup_product=ratio(products[arm]),
            geometric_mean_exact=dict(operation="POSITIVE_SQUARE_ROOT", radicand=ratio(products[arm])),
            minimum_pass=minimum >= MINIMUM, geomean_pass=products[arm] >= MINIMUM_PRODUCT,
            qualified=qualified)
    qualified = [arm for arm in ("AE", "AD") if evaluations[arm]["qualified"]]
    tie = False
    separation = None
    if not qualified:
        choice, reason = "O", "NEITHER_COMPLETE_ARM_MEETS_FIXED_THRESHOLDS"
    elif len(qualified) == 1:
        choice, reason = qualified[0], "ONLY_ONE_COMPLETE_ARM_QUALIFIES"
    else:
        separation = max(products.values()) / min(products.values())
        tie = separation < TIE_PRODUCT_RATIO
        if tie:
            choice, reason = "AE", "STRICT_RATIO_TIE_IMPLEMENTATION_PREFERENCE_NOT_MEASURED_AREA"
        else:
            choice = "AE" if products["AE"] > products["AD"] else "AD"
            reason = "LARGER_COMPLETE_ARM_GEOMETRIC_MEAN"
    return dict(scope="ARITHMETIC_ONLY_NOT_RECEIPT_ACCEPTANCE", choice=choice, reason=reason,
                arms=evaluations, tie_applied=tie,
                max_min_product_ratio=ratio(separation) if separation is not None else None,
                tie_product_ratio_strict_upper_bound=ratio(TIE_PRODUCT_RATIO))


def _frozen(preregistration, base_decision, old_selection, base_cycles):
    require(sha(preregistration) == PREREG_SHA256 and sha(base_decision) == BASE_DECISION_SHA256 and
            sha(old_selection) == OLD_SELECTION_SHA256, "FROZEN_PREREG_BASE_OR_OLD_SELECTION_CHANGED")
    prereg, bases = load(preregistration), load(base_decision)
    require(set(base_cycles) == set(BASES) and all(type(base_cycles[key]) is int and
            base_cycles[key] == BASES[key][0] for key in BASES), "EXACT_TWO_INTEGER_BASE_CYCLES_REQUIRED")
    require(prereg["old_selection_sha256"] == OLD_SELECTION_SHA256 and
            tuple((row["point"], row["arm"], row["workload"], row["attempt_uuid"])
                  for row in prereg["ordered_points"]) == POINTS, "FIXED_FOUR_UUID_ORDER_REQUIRED")
    require(bases["status"] == "PASS_BOTH_SCOPED_IMPORTED_BASES_FOR_AG6_ONLY_NO_DISPATCH_PERMISSION",
            "BOTH_INDEPENDENT_SCOPED_BASES_REQUIRED")
    for spec in prereg["ordered_points"]:
        workload = spec["workload"]
        cycles, uuid = BASES[workload]
        base = bases["bases"][workload]
        require(spec["BASE_eligibility_decision_sha256"] == BASE_DECISION_SHA256 and
                spec["imported_BASE_cycles"] == base["cycles"] == cycles and
                spec["imported_BASE_UUID"] == base["old_UUID_reference_only"] == uuid and
                base["decision"] == "PASS_BA_INDEPENDENT_SCOPED_IMPORT_EXACT_AG6_V2_TUPLE_ONLY",
                "EXACT_INPUT_BASE_COMPARISON_JOIN_REQUIRED")
    return prereg, bases


def _receipt(content, expected, index, base_cycles):
    data = load(content)
    point, arm, workload, uuid = POINTS[index]
    require(data["point"] == point and data["arm"] == arm and data["workload"] == workload and
            data["attempt_uuid"] == uuid == expected["attempt_uuid"], "STRICT_POINT_UUID_OR_ORDER_CHANGED")
    require(data["status"] == "PASS_ACTUAL_REGISTERED_AG6_FULL_STRICT_EVIDENCE" and
            data["performance_accepted"] is True and data["scientific_strict_pass"] is True and
            data["acceptance_scope"] == "ACTUAL_OWN_SOURCE_BOUND_REGISTERED_ATTEMPT",
            "ACTUAL_ACCEPTED_FULL_STRICT_REQUIRED")
    cycles = data["cycles"]
    require(type(cycles) is int and cycles > 0 and type(data["BASE_cycles"]) is int and
            data["BASE_cycles"] == base_cycles[workload], "POSITIVE_INTEGER_CYCLES_REQUIRED")
    require(all(type(data["speedup_exact"][key]) is int for key in ("numerator", "denominator")) and
            data["speedup_exact"] == dict(numerator=base_cycles[workload], denominator=cycles),
            "ACCEPTED_BASE_ON_INTEGER_RATIO_CHANGED")
    require(all(type(data[key]) is int for key in ("kernel_count", "CTA", "active_instructions")) and
            data["kernel_count"] == expected["expected_kernels"] and data["CTA"] == expected["expected_CTA"] and
            data["active_instructions"] == expected["expected_instructions"], "FULL_INPUT_POPULATION_REQUIRED")
    for key in ("input_runtime_identity_sha256", "mapping_closure_sha256", "runtime_resource_monitor_sha256",
                "final_resource_sha256"):
        value = data[key]
        require(isinstance(value, str) and len(value) == 64 and all(char in "0123456789abcdef" for char in value),
                "ACTUAL_EVIDENCE_CLOSURE_HASH_REQUIRED:" + key)
    require(isinstance(data["publication_head"], str) and len(data["publication_head"]) == 40 and
            all(char in "0123456789abcdef" for char in data["publication_head"]) and
            type(data["resource_samples"]) is int and data["resource_samples"] > 0,
            "ACTUAL_PUBLICATION_AND_RUNTIME_OBSERVATION_REQUIRED")
    return data, Fraction(base_cycles[workload], cycles)


def select_v2(strict_receipts, *, base_cycles, preregistration, base_decision, old_selection):
    """Ordered four STRICT byte strings -> pure candidate publication dict.

    Missing/failed/malformed/reordered receipts retain provisional O with no
    nominated arm. All four accepted same-input results are required even when
    one whole arm has finished. Parent publishes a new SELECTION_V2 only after
    binding these exact input hashes to actual immutable execution evidence.
    """
    result = dict(status="PROVISIONAL_O_WITH_INCOMPLETE_OPT_SCREEN", final_F=None,
        nominated_arm=None, working_design="O", complete_four_point_screen=False,
        preserved_old_selection_sha256=OLD_SELECTION_SHA256, old_selection_write_performed=False,
        evidence=[], issues=[], arm_evaluations=None, actual_provenance_requires_parent_immutable_join=True,
        dispatch_permission=False, no_per_input_cherry_pick=True, no_AE_AD_combination=True,
        rule=dict(minimum_speedup=ratio(MINIMUM), minimum_geomean=ratio(Fraction(51, 50)),
                  tie_rule="MAX_GM_OVER_MIN_GM_STRICTLY_LESS_THAN_201_OVER_200", tie_priority="AE",
                  screen_inputs=["GEMM", "Gaussian"]))
    try:
        prereg, bases = _frozen(preregistration, base_decision, old_selection, base_cycles)
        result["input_sha256"] = dict(preregistration=sha(preregistration),
                                     BASE_decision=sha(base_decision), old_selection=sha(old_selection))
        result["BASE_comparators"] = {name: dict(cycles=row["cycles"], UUID=row["old_UUID_reference_only"],
            producer_dossier_sha256=row["producer_dossier_sha256"], scope=row["scope"],
            old_executor_scope=row["old_executor_scope"])
            for name, row in bases["bases"].items()}
        require(type(strict_receipts) in (list, tuple) and len(strict_receipts) <= 4,
                "ONLY_FOUR_ORDERED_RECEIPT_SLOTS_ALLOWED")
        if len(strict_receipts) != 4:
            result["issues"].append("MISSING_REGISTERED_STRICT_RECEIPT_SLOTS")
        speeds = {"AE": [], "AD": []}
        for index, content in enumerate(strict_receipts):
            row = dict(point=POINTS[index][0], expected_UUID=POINTS[index][3], accepted=False)
            try:
                row["STRICT_sha256"] = sha(content)
                data, speedup = _receipt(content, prereg["ordered_points"][index], index, base_cycles)
                row.update(accepted=True, cycles=data["cycles"], speedup_exact=ratio(speedup),
                           publication_head=data["publication_head"])
                speeds[POINTS[index][1]].append(speedup)
            except (ValueError, KeyError, TypeError, IndexError) as error:
                row["failure"] = type(error).__name__ + ":" + str(error)
                result["issues"].append(row["point"] + ":" + row["failure"])
            result["evidence"].append(row)
        if result["issues"]:
            return result
        arithmetic = _arithmetic(speeds)
        result.update(status="FINAL_F_FROM_COMPLETE_FOUR_POINT_AG6_SCREEN", final_F=arithmetic["choice"],
            nominated_arm=arithmetic["choice"] if arithmetic["choice"] != "O" else None,
            working_design=arithmetic["choice"], complete_four_point_screen=True,
            selection_reason=arithmetic["reason"], arm_evaluations=arithmetic["arms"],
            tie_applied=arithmetic["tie_applied"],
            max_min_product_ratio=arithmetic["max_min_product_ratio"],
            tie_product_ratio_strict_upper_bound=arithmetic["tie_product_ratio_strict_upper_bound"])
    except (ValueError, KeyError, TypeError, IndexError) as error:
        result["issues"].append(type(error).__name__ + ":" + str(error))
    return result
