"""Prepared opt-in composition of frozen resource Runtime, no signal/launch.

Only cgroup's exact old I/O persistence STOP reason becomes a bounded warning.
All other old host/cgroup decisions remain intact. Upstream exact ownership,
mapping/output bounds and actual stop/reap remain the BA guard's responsibility.
"""
import math

GIB = 1024 ** 3
OLD_CGROUP_IO_REASON = 'IO_FULL_PSI_GT25_THREE_GE30S_SAMPLES_AG_EXPLICIT_EXTENSION'
SAFETY_KEYS = ('authority', 'identity', 'mapper', 'output_limits', 'output_device',
               'expected_growth', 'explicit_abort_clear', 'ownership')
PROFILE = {'nominal_sample_s': 10, 'max_sample_gap_s': 30,
           'max_progress_age_s': 30, 'no_retirement_s': 600,
           'max_cgroup_high_episode_s': 1800, 'wall_deadline_s': 7200}
CLOSURE_KEYS = ('strict_complete', 'runtime_identity_complete', 'input_roi_complete',
                'source_options_complete', 'guard_safety_complete',
                'event_loader_complete', 'single_instance_lifetime_complete', 'no_prior_stop')


class TerminalClosure:
    """Pure terminal join. Late failures invalidate a completion candidate.

    No success state is a performance PASS. Inputs are independent authenticated
    guard/strict receipts, never values synthesized from a NATURAL packet.
    """
    def __init__(self):
        self.producer_natural = False
        self.state = 'PENDING_TERMINAL_CLOSURE'
        self.reason = 'WAITING_FOR_AUTHENTICATED_RECEIPTS'

    def observe(self, *, producer_end=None, run_ended=False,
                natural_exit_zero=None, actual_stop=False, closure=None):
        failure = None
        if type(actual_stop) is not bool or type(run_ended) is not bool:
            failure = 'INVALID_GUARD_TERMINAL_FLAGS'
        elif actual_stop:
            failure = 'ACTUAL_OR_LATE_GUARD_STOP'
        elif producer_end is not None and producer_end not in ('NONE', 'NATURAL', 'LIMIT', 'ERROR'):
            failure = 'UNKNOWN_PRODUCER_TERMINAL'
        elif producer_end in ('LIMIT', 'ERROR'):
            failure = 'NONNATURAL_PRODUCER_TERMINAL'
        elif run_ended and natural_exit_zero is not True:
            failure = 'NONNATURAL_OR_UNPROVEN_ACTUAL_EXIT'
        elif isinstance(closure, dict) and any(k in closure and closure[k] is not True for k in CLOSURE_KEYS):
            failure = 'NEGATIVE_OR_LATE_CONTRADICTORY_CLOSURE'
        if failure is not None:
            self.state, self.reason = 'STOP_UNACCEPTED', failure
        elif self.state != 'STOP_UNACCEPTED':
            if producer_end == 'NATURAL':
                self.producer_natural = True
            if run_ended:
                if (not self.producer_natural or not isinstance(closure, dict) or
                        any(closure.get(k) is not True for k in CLOSURE_KEYS)):
                    self.state, self.reason = 'STOP_UNACCEPTED', 'INCOMPLETE_FINAL_NATURAL_CLOSURE'
                else:
                    self.state, self.reason = 'COMPLETE_CANDIDATE', 'REQUIRES_EXTERNAL_SCIENTIFIC_ACCEPTANCE'
        return dict(state=self.state, reason=self.reason,
                    scientific_acceptance=False, performance_pass=False,
                    allocation=False)


class RuntimePolicyB:
    def __init__(self, baseline, output, *, resource_module, started_ns, opt_in=False):
        if opt_in is not True:
            raise ValueError('EXPLICIT_POLICY_B_OPT_IN_REQUIRED')
        if type(started_ns) is not int or started_ns <= 0:
            raise ValueError('EXACT_START_MONOTONIC_TIME_REQUIRED')
        self.original = resource_module.Runtime(baseline, output)
        self.started_ns = started_ns
        self.last_ns = started_ns
        self.high_since_ns = None
        self.last_retired_ns = started_ns
        self.completed = None
        self.last_producer_ns = None
        self.stop_reasons = []

    def quick_stop(self):
        return self.original.quick_stop()

    def _stop(self, reasons, domains=None, warnings=None):
        self.stop_reasons.extend(x for x in reasons if x not in self.stop_reasons)
        return dict(decision='STOP', stop_reasons=list(self.stop_reasons),
                    warnings=list(warnings or []), domains=domains or {},
                    next_full_sample_seconds=10, profile=dict(PROFILE),
                    scientific_acceptance=False, no_signal_in_this_policy_module=True)

    def observe(self, sample, own_faults, previous_faults, *, progress,
                safety_checks, io_impact):
        if self.stop_reasons:
            return self._stop([])
        reasons, warnings = [], []
        try:
            now = sample['monotonic_ns']
            if type(now) is not int or now <= self.last_ns or now - self.last_ns > 30 * 10**9:
                return self._stop(['INVALID_OR_MISSING_RESOURCE_SAMPLE_CADENCE'])
            # Execute the exact old full host and cgroup state machines first.
            host = self.original.host.observe(sample, own_faults, previous_faults)
            cg = self.original.cgroup.observe(self.original._project(sample), own_faults, previous_faults)
            old_io_stopped = OLD_CGROUP_IO_REASON in cg['stop_reasons']
            cg = dict(cg, stop_reasons=[x for x in cg['stop_reasons'] if x != OLD_CGROUP_IO_REASON])
            cg['decision'] = 'STOP' if cg['stop_reasons'] else 'WARN' if cg['warnings'] or old_io_stopped else 'CONTINUE'
            domains = {'host': host, 'cgroup': cg}
            reasons += [domain + ':' + reason for domain, value in domains.items() for reason in value['stop_reasons']]
            if sample['disk_free_bytes'] <= 5 * GIB:
                reasons.append('USER_OUTPUT_FILESYSTEM_AT_OR_BELOW_5GiB')
            if sample['output_filesystem_device'] != self.original.first['output_filesystem_device']:
                reasons.append('V2_OUTPUT_FILESYSTEM_CHANGED')
            if sample['host_oom_kill'] != self.original.first['host_oom_kill']:
                reasons.append('NEW_HOST_OOM_KILL')
            if (not isinstance(safety_checks, dict) or
                    any(type(safety_checks.get(k)) is not bool for k in SAFETY_KEYS)):
                reasons.append('UNKNOWN_REQUIRED_CURRENT_GUARD_EVIDENCE')
            else:
                reasons += ['CURRENT_GUARD:' + k for k in SAFETY_KEYS if safety_checks[k] is not True]
            # io_impact is not inferred from retirement or low host PSI. The
            # qualified adapter must explicitly accept conservative shared-scope
            # bounds, or provide measured harm=false. Unknown is a STOP.
            if not isinstance(io_impact, dict) or io_impact.get('known_scope') is not True:
                reasons.append('UNVERIFIABLE_IO_IMPACT_SCOPE')
            elif (io_impact.get('harm_detected') is not False or
                  io_impact.get('conservative_host_episode_profile_accepted') is not True):
                reasons.append('IO_IMPACT_OR_FAIRNESS_NOT_ACCEPTED')
            cg_io = float(sample['cgroup_pressure_parsed']['io']['full']['avg10'])
            host_io = float(sample['pressure']['io']['full']['avg10'])
            if any(not math.isfinite(x) or not 0 <= x <= 100 for x in (cg_io, host_io)):
                reasons.append('INVALID_CURRENT_HOST_OR_CGROUP_IO')
            if cg_io > 25:
                warnings.append('RUNTIME_IO_WARNING_CGROUP_SHARED_SCOPE')
                if self.high_since_ns is None:
                    self.high_since_ns = now
                if now - self.high_since_ns >= 1800 * 10**9:
                    reasons.append('MAXIMUM_CGROUP_HIGH_PSI_EPISODE_1800S')
            else:
                self.high_since_ns = None
            if host_io > 25:
                warnings.append('HOST_GLOBAL_IO_PRESSURE_ORIGINAL_PERSISTENCE_RETAINED')
            if now - self.started_ns >= 7200 * 10**9:
                reasons.append('WALL_DEADLINE_7200S')
            if progress is None:
                if now - self.started_ns > 30 * 10**9:
                    reasons.append('MISSING_INITIAL_PRODUCER_AFTER_30S')
            else:
                pn = progress['mono_ns']
                if type(pn) is not int or pn > now or now - pn > 30 * 10**9:
                    reasons.append('STALE_OR_FUTURE_PRODUCER')
                if self.last_producer_ns is not None and pn < self.last_producer_ns:
                    reasons.append('REVERSED_PRODUCER')
                self.last_producer_ns = pn
                if progress['end'] in ('LIMIT', 'ERROR'):
                    reasons.append('NONNATURAL_PRODUCER_RUN_END')
                value = progress['completed']
                if type(value) is not int or value < 0 or (self.completed is not None and value < self.completed):
                    reasons.append('INVALID_OR_REVERSED_COMPLETION_COUNTER')
                else:
                    if self.completed is not None and value > self.completed:
                        self.last_retired_ns = pn
                    self.completed = value
            # Phase changes and fresh same-valued records never renew this cap.
            if now - self.last_retired_ns >= 600 * 10**9:
                reasons.append('NO_SEMANTIC_RETIREMENT_600S')
            self.last_ns = now
        except (KeyError, TypeError, ValueError, OverflowError, AttributeError):
            return self._stop(['UNKNOWN_OR_MALFORMED_REQUIRED_EVIDENCE'])
        if reasons:
            return self._stop(reasons, domains, warnings)
        warnings += [domain + ':' + reason for domain, value in domains.items() for reason in value['warnings']]
        return dict(decision='WARN' if warnings else 'CONTINUE', stop_reasons=[],
                    warnings=warnings, domains=domains, next_full_sample_seconds=10,
                    profile=dict(PROFILE), scientific_acceptance=False,
                    no_signal_in_this_policy_module=True)
