"""Pure engineering-view qualification; no installation, authority writes or launches.

Canonical primary matrices stay unchanged. The existing R2 adapter sees exactly
its previous view after this outer adapter removes approved engineering rows.
"""
import copy
import hashlib
import json

ROLE = "ENGINEERING_OBSERVATION_CANARY"
MODES = {"DEFAULT_CONTROL", "BPF_REQUIRED"}
MARKER = "engineering_observation_dispatch_view"


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True,
                                    separators=(",", ":")).encode()).hexdigest()


class CanaryScope:
    def __init__(self, plan):
        self.plan = copy.deepcopy(plan)
        self.keys = tuple(plan["science_keys"])
        self.rows = {r["cohort"]: r for r in plan["rows"]}
        assert len(self.rows) == len(plan["rows"]) == 4
        assert plan["scientific_role"] == ROLE
        assert {r["mode"] for r in self.rows.values()} == MODES
        assert all(r["scientific_role"] == ROLE for r in self.rows.values())
        self.plan_sha = digest(plan)

    def check_primary(self, matrix, scope):
        for source in (matrix, scope):
            points = source["points"]
            assert len({p["cohort"] for p in points}) == len(points)
            assert not (set(self.rows) & {p["cohort"] for p in points})
            assert not any(p.get("scientific_role") == ROLE for p in points)
        return True

    def validate(self, cohort, spec, canonical_sha, authority):
        row = self.rows[cohort]
        assert spec["cohort"] == cohort and spec["scientific_role"] == ROLE
        assert spec["request"] == authority["request"]
        assert authority["admitted_specs"][cohort] == canonical_sha
        # l2_native.canonical requires an unbound CPU. CPU selection belongs
        # solely to the independently hashed dispatch-resolved copy.
        assert spec["host_cpu"] is None, "CANONICAL_CPU_MUST_BE_UNBOUND"
        # Official resource amendments may update current canonical identity;
        # the frozen scientific projection and role remain immutable.
        assert digest({k: spec[k] for k in self.keys}) == row["science_projection_sha256"]
        lineage = spec["engineering_observation_canary_lineage"]
        for key, expected in (("mode", row["mode"]), ("pair_id", row["pair_id"]),
                              ("reference_cohort", row["reference_cohort"]),
                              ("reference_result_sha256", row["reference_result_sha256"]),
                              ("reference_cycles", row["reference_cycles"]),
                              ("science_projection_sha256", row["science_projection_sha256"])):
            assert lineage[key] == expected, key
        assert lineage["primary_statistics_excluded"] is True
        assert lineage["validated_union_authorized"] is False
        records = authority.get("authorized_engineering_observation_canaries", [])
        matches = [r for r in records if r["cohort"] == cohort]
        assert len(matches) == 1
        authorization = matches[0]
        assert authorization["role"] == ROLE
        assert authorization["mode"] == row["mode"]
        assert authorization["science_projection_sha256"] == row["science_projection_sha256"]
        assert authorization["primary_statistics_excluded"] is True
        assert authorization["validated_union_authorized"] is False
        return dict(cohort=cohort, mode=row["mode"], role=ROLE,
                    canonical_sha256=canonical_sha,
                    science_projection_sha256=row["science_projection_sha256"])

    def dispatch_view(self, previous_view, matrix, scope, authority, canonical):
        self.check_primary(matrix, scope)
        assert MARKER not in previous_view
        assert not (set(self.rows) & {p["cohort"] for p in previous_view["points"]})
        result = copy.deepcopy(previous_view)
        added = []
        for cohort, row in self.rows.items():
            if cohort not in authority["admitted_specs"]:
                continue
            spec, sha = canonical(cohort)
            checked = self.validate(cohort, spec, sha, authority)
            result["points"].append(dict(cohort=cohort, input_digest=spec["input_digest"],
                program=spec["program"], suite=spec["suite"], profile=spec["profile"],
                cell=spec["cell"], scientific_role=ROLE, observation_mode=row["mode"]))
            added.append(checked)
        result[MARKER] = dict(schema="ENGINEERING_OBSERVATION_DISPATCH_ONLY_V1",
            plan_semantic_sha256=self.plan_sha, previous_view_semantic_sha256=digest(previous_view),
            cohorts=added, canonical_primary_unchanged=True)
        return result

    def primary_view(self, view, matrix, scope, authority, canonical):
        self.check_primary(matrix, scope)
        assert MARKER in view
        meta = view[MARKER]
        assert meta["schema"] == "ENGINEERING_OBSERVATION_DISPATCH_ONLY_V1"
        assert meta["plan_semantic_sha256"] == self.plan_sha
        expected = {x["cohort"]: x for x in meta["cohorts"]}
        assert len(expected) == len(meta["cohorts"])
        result = copy.deepcopy(view)
        kept, seen = [], set()
        for point in result["points"]:
            cohort = point["cohort"]
            if cohort in self.rows:
                assert point["scientific_role"] == ROLE and cohort in expected
                spec, sha = canonical(cohort)
                assert self.validate(cohort, spec, sha, authority) == expected[cohort]
                assert point["observation_mode"] == self.rows[cohort]["mode"]
                assert cohort not in seen
                seen.add(cohort)
            else:
                assert point.get("scientific_role") != ROLE, "UNKNOWN_ENGINEERING_ROLE"
                kept.append(point)
        assert seen == set(expected)
        result["points"] = kept
        del result[MARKER]
        assert digest(result) == meta["previous_view_semantic_sha256"]
        return result

    def assert_primary_summary(self, summary, matrix, scope):
        self.check_primary(matrix, scope)
        allowed = {p["cohort"] for p in matrix["points"]}
        for profiles in summary["table"].values():
            for cells in profiles.values():
                for row in cells.values():
                    assert row["cohort"] in allowed
                    assert row["cohort"] not in self.rows
                    assert row.get("scientific_role") != ROLE
        return True


def make_dispatch_reader(previous, scoped, current_sources, target_path):
    """A failed optional engineering view leaves the exact old queue available."""
    def reader(path):
        value = previous(path)
        if str(path) != str(target_path):
            return value
        try:
            matrix, scope, authority, canonical = current_sources()
            result = scoped.dispatch_view(value, matrix, scope, authority, canonical)
            reader.last_issue = None
            return result
        except Exception as error:
            reader.last_issue = repr(error)
            return value
    reader.last_issue = None
    return reader


def wrap_primary_adaptive(previous, scoped, current_sources, guard=None):
    """Compose outside the existing R2 wrapper; never widen R2's whitelist."""
    def recommend(summary, view, history=None):
        try:
            matrix, scope, authority, canonical = current_sources()
            scoped.assert_primary_summary(summary, matrix, scope)
            if MARKER in view:
                clean = scoped.primary_view(view, matrix, scope, authority, canonical)
            else:
                assert not any(p["cohort"] in scoped.rows or
                               p.get("scientific_role") == ROLE for p in view["points"])
                clean = view  # Exact old/R2 view when optional admission is held.
            decision = previous(summary, clean, history or {})
            for proposal in decision.get("proposals", []):
                for point in proposal.get("new_cells", []):
                    assert point.get("cohort") not in scoped.rows
                    assert point.get("scientific_role") != ROLE
            recommend.last_issue = None
            return decision
        except Exception as error:
            recommend.last_issue = repr(error)
            hold = dict(state="ENGINEERING_CANARY_PRIMARY_EXCLUSION_HOLD", proposals=[],
                        scientific_stage_complete=False, adoption_ready=False,
                        requires_engineering_review=True, healthy_models_continue=True,
                        error=repr(error))
            if guard is not None:
                try:
                    value = guard(copy.deepcopy(hold))
                    assert isinstance(value, dict)
                    return dict(value, **hold)
                except Exception as guard_error:
                    hold["registry_journal_status"] = dict(
                        safe_for_scientific_completion=False, error=repr(guard_error))
            return hold
    recommend.last_issue = None
    return recommend
