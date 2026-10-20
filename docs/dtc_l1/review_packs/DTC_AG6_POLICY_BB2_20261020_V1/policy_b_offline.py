"""DESIGN_ONLY_NOT_SAFE_FOR_PRODUCTION: pure CPU/offline decision semantics.

No imports of BA, process access, IO, budget allocation, or monitoring. Frozen
safety predicates are supplied by an upstream adapter; this is NOT that adapter.
All new timing parameters are mandatory, illustrative, caller-supplied values.
"""

from dataclasses import dataclass
from math import isfinite

GIB = 1024 ** 3
SAFETY_KEYS = (
    "disk_growth", "memory", "oom", "swap", "identity", "authority",
    "deadline", "explicit_abort", "memory_psi_persistence", "io_impact",
    "outdevice",
)
IDENTITY_KEYS = ("pid", "start_ticks", "input_id", "roi_id", "generation")
METRICS = {"sim_instructions_committed", "completed_ctas", "completed_kernels"}
CLOSURE_KEYS = (
    "natural_exit_zero", "strict_runtime_complete", "identity_complete",
    "input_roi_complete", "frozen_safety_complete", "no_prior_stop",
)


def number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and isfinite(value)


@dataclass(frozen=True)
class Params:
    illustrative: bool
    max_sample_gap_s: float
    max_progress_age_s: float
    no_progress_watchdog_s: float
    long_phase_grace_s: float
    max_io_warning_s: float

    def __post_init__(self):
        if self.illustrative is not True:
            raise ValueError("Only explicitly illustrative offline parameters are accepted")
        for key in self.__dataclass_fields__:
            if key != "illustrative" and (not number(getattr(self, key)) or getattr(self, key) <= 0):
                raise ValueError("Each illustrative duration must be finite and positive")


class PolicyB:
    """Stateful pure evaluator. Runtime refusals and completion are absorbing.

    Input dictionaries are read without mutation. Epoch seconds here are any
    caller-owned MONOTONIC times, never wall clock. Unknown evidence stops the
    modeled runtime conservatively. PRELAUNCH_HOLD permits a new admission check.
    The max_io_warning_s fallback bounds one uninterrupted high-PSI episode even
    with verified progress; supplied io_impact=False is an earlier safety stop.
    """

    def __init__(self, params, *, offline_opt_in=False):
        if offline_opt_in is not True or not isinstance(params, Params):
            raise ValueError("Explicit offline opt-in and illustrative Params required")
        self.params = params
        self.admitted = False
        self.terminal = None
        self.identity = None
        self.last_sample = None
        self.last_progress_time = None
        self.last_observed = None
        self.progress_scope = None
        self.progress_value = None
        self.high_io_since = None

    def _result(self, state, reason, terminal=False):
        result = dict(state=state, reason=reason, offline_only=True,
                      allocation=False, performance_pass=False,
                      qualification="DESIGN_ONLY_NOT_SAFE_FOR_PRODUCTION")
        if terminal:
            self.terminal = result
        return dict(result)

    def _reject(self, prelaunch, reason, safety=False):
        state = "PRELAUNCH_HOLD" if prelaunch else (
            "RUNTIME_STOP_SAFETY" if safety else "RUNTIME_INSUFFICIENT_EVIDENCE")
        return self._result(state, reason, terminal=not prelaunch)

    def evaluate(self, sample):
        # A late actual-stop receipt invalidates a completion *candidate*;
        # the evaluator never upgrades an observed stopped run to success.
        if (self.terminal is not None and self.terminal['state'] == 'COMPLETE_CANDIDATE'
                and isinstance(sample, dict) and sample.get('actual_stop') is True):
            return self._reject(False, 'actual_stop_after_completion_candidate', safety=True)
        if self.terminal is not None:
            return dict(self.terminal)
        if not isinstance(sample, dict):
            return self._reject(not self.admitted, "missing_sample")
        phase = sample.get("phase")
        prelaunch = phase == "PRELAUNCH" and not self.admitted
        if phase not in ("PRELAUNCH", "RUNTIME") or (self.admitted and phase != "RUNTIME"):
            return self._reject(not self.admitted, "invalid_phase_or_reentry")
        if phase == "RUNTIME" and not self.admitted:
            return self._reject(False, "no_verified_prelaunch")
        now = sample.get("timestamp_s")
        if not number(now):
            return self._reject(prelaunch, "missing_timestamp")
        if self.last_sample is not None and (
                now <= self.last_sample or now - self.last_sample > self.params.max_sample_gap_s):
            return self._reject(prelaunch, "reversed_or_gap_timestamp")
        identity = sample.get("identity")
        if not isinstance(identity, dict) or any(
                identity.get(k) is None or identity.get(k) == "" for k in IDENTITY_KEYS):
            return self._reject(prelaunch, "missing_exact_identity")
        identity_tuple = tuple(identity[k] for k in IDENTITY_KEYS)
        if self.identity is not None and identity_tuple != self.identity:
            return self._reject(prelaunch, "identity_discontinuity", safety=True)
        safety = sample.get("safety_checks")
        if not isinstance(safety, dict) or any(type(safety.get(k)) is not bool for k in SAFETY_KEYS):
            return self._reject(prelaunch, "missing_frozen_safety_predicate")
        failed = [k for k in SAFETY_KEYS if safety[k] is False]
        if failed:
            return self._reject(prelaunch, "frozen_safety:" + ",".join(failed), safety=True)
        free = sample.get("output_free_bytes")
        writes = sample.get("expected_write_bytes")
        if not number(free) or not number(writes) or writes < 0:
            return self._reject(prelaunch, "missing_output_growth_measurement")
        if free <= 5 * GIB or free - writes <= 5 * GIB:
            return self._reject(prelaunch, "strict_disk_floor_or_projected_growth", safety=True)
        host_io = sample.get("host_io_full_avg10")
        cg_io = sample.get("cgroup_io_full_avg10")
        if any(not number(x) or not 0 <= x <= 100 for x in (host_io, cg_io)):
            return self._reject(prelaunch, "missing_paired_io_measurement")
        if prelaunch:
            r2 = sample.get("paired_r2")
            if not isinstance(r2, dict) or any(r2.get(k) is not True for k in (
                    "host", "cgroup", "oom_unchanged", "exact_role_authority_pass")):
                return self._reject(True, "paired_r2_not_passed")
            interval = r2.get("interval_s")
            if not number(interval) or interval < 10:
                return self._reject(True, "paired_r2_interval")
            if host_io > 25 or cg_io > 25:
                return self._reject(True, "strict_paired_preflight_io")
            for prefix in ("host", "cgroup"):
                headroom = sample.get(prefix + "_memory_headroom_bytes")
                psi = sample.get(prefix + "_memory_full_avg10")
                if not number(headroom) or not number(psi):
                    return self._reject(True, "missing_paired_memory_measurement")
                if headroom < 32 * GIB or not 0 <= psi <= 1:
                    return self._reject(True, "strict_paired_preflight_memory")
            self.admitted, self.identity, self.last_sample = True, identity_tuple, now
            return self._result("PRELAUNCH_READY", "offline_admission_only_no_launch_or_allocation")
        if sample.get("actual_stop") is True or (
                sample.get("run_ended") is True and sample.get("natural_complete") is not True):
            return self._reject(False, "actual_stop_or_unnatural_run_end", safety=True)
        progress = sample.get("semantic_progress")
        if not isinstance(progress, dict) or progress.get("status") != "AVAILABLE":
            return self._reject(False, "semantic_progress_unavailable")
        value, observed = progress.get("value"), progress.get("observed_at_s")
        metric, scope = progress.get("metric"), progress.get("scope_id")
        if (type(value) is not int or value < 0 or not number(observed)
                or metric not in METRICS or not isinstance(scope, str) or not scope):
            return self._reject(False, "invalid_semantic_progress")
        if observed > now or now - observed > self.params.max_progress_age_s:
            return self._reject(False, "stale_or_future_progress")
        if self.progress_scope is not None and self.progress_scope != (metric, scope):
            return self._reject(False, "metric_or_scope_discontinuity")
        if self.last_observed is not None and (observed < self.last_observed or value < self.progress_value):
            return self._reject(False, "reversed_or_reset_progress")
        if self.progress_value is not None and value > self.progress_value and observed <= self.last_observed:
            return self._reject(False, "progress_without_new_observation")
        if self.progress_value is None or value > self.progress_value:
            self.last_progress_time = observed
        self.last_sample, self.last_observed = now, observed
        self.progress_value, self.progress_scope = value, (metric, scope)
        high_io = cg_io > 25 or host_io > 25
        if high_io and self.high_io_since is None:
            self.high_io_since = now
        if not high_io:
            self.high_io_since = None
        if high_io and now - self.high_io_since >= self.params.max_io_warning_s:
            return self._reject(False, "bounded_io_impact_fallback", safety=True)
        grace = sample.get("legitimate_long_phase") is True
        if grace and not sample.get("long_phase_contract_id"):
            return self._reject(False, "unbound_long_phase")
        limit = max(self.params.no_progress_watchdog_s,
                    self.params.long_phase_grace_s if grace else 0)
        if now - self.last_progress_time >= limit:
            return self._result("RUNTIME_STOP_NOPROGRESS", "bounded_no_semantic_progress", terminal=True)
        if sample.get("natural_complete") is True:
            closure = sample.get("closure")
            if not isinstance(closure, dict) or any(closure.get(k) is not True for k in CLOSURE_KEYS):
                return self._reject(False, "incomplete_natural_completion_closure")
            return self._result("COMPLETE_CANDIDATE", "requires_external_scientific_acceptance", terminal=True)
        return self._result("RUNTIME_WARNING" if high_io or grace else "RUNTIME_OBSERVING",
                            "psi_or_bounded_grace" if high_io or grace else "verified_semantic_observation")
