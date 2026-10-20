"""DECLARED_SYNTHETIC: minimal CPU-only semantic tests, not observed AE_GEMM.

Run only after external CURRENT exact-role CPU test admission. No simulator,
fixture, GPU, process, BA imports, allocation, or performance measurements.
"""

from copy import deepcopy
import unittest

from policy_b_offline import CLOSURE_KEYS, GIB, Params, PolicyB, SAFETY_KEYS


def params():
    # DECLARED_SYNTHETIC scenario durations. No production window is proposed.
    return Params(illustrative=True, max_sample_gap_s=40, max_progress_age_s=3,
                  no_progress_watchdog_s=20, long_phase_grace_s=40,
                  max_io_warning_s=60)


def prelaunch():
    return dict(
        evidence_label="DECLARED_SYNTHETIC", phase="PRELAUNCH", timestamp_s=0,
        identity=dict(pid=123, start_ticks=456, input_id="synthetic-input",
                      roi_id="synthetic-roi", generation=0),
        safety_checks={key: True for key in SAFETY_KEYS},
        output_free_bytes=12 * GIB, expected_write_bytes=GIB,
        host_io_full_avg10=0, cgroup_io_full_avg10=0,
        host_memory_headroom_bytes=40 * GIB, cgroup_memory_headroom_bytes=40 * GIB,
        host_memory_full_avg10=0, cgroup_memory_full_avg10=0,
        paired_r2=dict(host=True, cgroup=True, interval_s=10,
                       oom_unchanged=True, exact_role_authority_pass=True))


def runtime(time, value, io=0):
    sample = prelaunch()
    sample.update(phase="RUNTIME", timestamp_s=time, cgroup_io_full_avg10=io,
                  semantic_progress=dict(status="AVAILABLE", value=value,
                      observed_at_s=time, metric="sim_instructions_committed",
                      scope_id="synthetic-input/synthetic-roi"))
    return sample


def admitted():
    policy = PolicyB(params(), offline_opt_in=True)
    assert policy.evaluate(prelaunch())["state"] == "PRELAUNCH_READY"
    return policy


class PolicyBSyntheticTests(unittest.TestCase):
    def test_explicit_offline_opt_in_and_no_defaults_or_budget(self):
        with self.assertRaises(TypeError):
            Params()
        with self.assertRaises(ValueError):
            PolicyB(params())
        policy = admitted()
        for result in (policy.evaluate(runtime(1, 0)), policy.evaluate(runtime(2, 1, 90))):
            self.assertIs(result["allocation"], False)
            self.assertIs(result["performance_pass"], False)
            self.assertIs(result["offline_only"], True)

    def test_strict_paired_preflight_boolean_and_actual_measurements(self):
        cases = (
            ("host_io_full_avg10", 25.01), ("cgroup_io_full_avg10", 25.01),
            ("host_memory_headroom_bytes", 32 * GIB - 1),
            ("cgroup_memory_full_avg10", 1.01), ("output_free_bytes", 5 * GIB),
        )
        for field, value in cases:
            with self.subTest(field=field):
                sample = prelaunch()
                sample[field] = value
                self.assertEqual(PolicyB(params(), offline_opt_in=True).evaluate(sample)["state"],
                                 "PRELAUNCH_HOLD")
        sample = prelaunch()
        sample["paired_r2"]["cgroup"] = False
        self.assertEqual(PolicyB(params(), offline_opt_in=True).evaluate(sample)["state"], "PRELAUNCH_HOLD")
        sample["paired_r2"]["cgroup"] = True
        sample["paired_r2"]["interval_s"] = 9.99
        self.assertEqual(PolicyB(params(), offline_opt_in=True).evaluate(sample)["state"], "PRELAUNCH_HOLD")

    def test_high_psi_with_semantic_progress_has_bounded_warning(self):
        policy = admitted()
        for time, value in ((1, 0), (21, 1), (41, 2)):
            self.assertEqual(policy.evaluate(runtime(time, value, 95))["state"], "RUNTIME_WARNING")
        result = policy.evaluate(runtime(61, 3, 95))
        self.assertEqual((result["state"], result["reason"]),
                         ("RUNTIME_STOP_SAFETY", "bounded_io_impact_fallback"))

    def test_no_progress_watchdog_and_explicit_bounded_long_phase(self):
        policy = admitted()
        self.assertEqual(policy.evaluate(runtime(1, 0, 90))["state"], "RUNTIME_WARNING")
        self.assertEqual(policy.evaluate(runtime(21, 0, 90))["state"], "RUNTIME_STOP_NOPROGRESS")
        policy = admitted()
        for time in (1, 21):
            sample = runtime(time, 0, 90)
            sample.update(legitimate_long_phase=True, long_phase_contract_id="SYNTHETIC_INITIAL_PHASE")
            self.assertEqual(policy.evaluate(sample)["state"], "RUNTIME_WARNING")
        sample["timestamp_s"] = sample["semantic_progress"]["observed_at_s"] = 41
        self.assertEqual(policy.evaluate(sample)["state"], "RUNTIME_STOP_NOPROGRESS")

    def test_missing_stale_reversed_reset_scope_and_gap_fail_closed(self):
        for defect in ("unavailable", "stale", "timestamp", "counter_reset", "scope", "gap"):
            with self.subTest(defect=defect):
                policy = admitted()
                policy.evaluate(runtime(1, 10))
                sample = runtime(2, 11)
                if defect == "unavailable":
                    sample["semantic_progress"] = {"status": "UNAVAILABLE"}
                elif defect == "stale":
                    sample["semantic_progress"]["observed_at_s"] = -10
                elif defect == "timestamp":
                    sample["timestamp_s"] = 0
                elif defect == "counter_reset":
                    sample["semantic_progress"]["value"] = 9
                elif defect == "scope":
                    sample["semantic_progress"]["scope_id"] = "other-roi"
                elif defect == "gap":
                    sample["timestamp_s"] = sample["semantic_progress"]["observed_at_s"] = 42
                self.assertEqual(policy.evaluate(sample)["state"], "RUNTIME_INSUFFICIENT_EVIDENCE")
                self.assertEqual(policy.evaluate(runtime(43, 12))["state"], "RUNTIME_INSUFFICIENT_EVIDENCE")

    def test_frozen_safety_storage_projection_and_identity(self):
        for predicate in SAFETY_KEYS:
            with self.subTest(predicate=predicate):
                sample = runtime(1, 1)
                sample["safety_checks"][predicate] = False
                self.assertEqual(admitted().evaluate(sample)["state"], "RUNTIME_STOP_SAFETY")
        for defect in ("disk", "growth", "identity", "missing_safety"):
            with self.subTest(defect=defect):
                sample = runtime(1, 1)
                if defect == "disk":
                    sample["output_free_bytes"] = 5 * GIB
                elif defect == "growth":
                    sample["expected_write_bytes"] = 7 * GIB
                elif defect == "identity":
                    sample["identity"]["start_ticks"] += 1
                else:
                    del sample["safety_checks"]["oom"]
                expected = "RUNTIME_INSUFFICIENT_EVIDENCE" if defect == "missing_safety" else "RUNTIME_STOP_SAFETY"
                self.assertEqual(admitted().evaluate(sample)["state"], expected)

    def test_prelaunch_recovery_warning_recovery_and_no_runtime_reentry(self):
        policy = PolicyB(params(), offline_opt_in=True)
        sample = prelaunch()
        sample["cgroup_io_full_avg10"] = 90
        self.assertEqual(policy.evaluate(sample)["state"], "PRELAUNCH_HOLD")
        self.assertEqual(policy.evaluate(prelaunch())["state"], "PRELAUNCH_READY")
        self.assertEqual(policy.evaluate(runtime(1, 0, 90))["state"], "RUNTIME_WARNING")
        self.assertEqual(policy.evaluate(runtime(2, 1))["state"], "RUNTIME_OBSERVING")
        self.assertEqual(policy.evaluate(prelaunch())["state"], "RUNTIME_INSUFFICIENT_EVIDENCE")
        self.assertEqual(policy.evaluate(runtime(3, 2))["state"], "RUNTIME_INSUFFICIENT_EVIDENCE")

    def test_natural_completion_requires_closure_and_actual_stop_never_succeeds(self):
        complete = runtime(1, 1)
        complete.update(natural_complete=True, run_ended=True,
                        closure={key: True for key in CLOSURE_KEYS})
        original = deepcopy(complete)
        policy = admitted()
        result = policy.evaluate(complete)
        self.assertEqual(result["state"], "COMPLETE_CANDIDATE")
        self.assertIs(result["performance_pass"], False)
        self.assertEqual(complete, original)
        self.assertEqual(policy.evaluate(dict(complete, actual_stop=True))["state"], "RUNTIME_STOP_SAFETY")
        policy = admitted()
        self.assertEqual(policy.evaluate(complete)['state'], 'COMPLETE_CANDIDATE')
        self.assertEqual(policy.evaluate(dict(complete, run_ended=True, natural_complete=False))['state'], 'RUNTIME_STOP_SAFETY')
        for defect in ("actual_stop", "unnatural_end", "incomplete_closure"):
            with self.subTest(defect=defect):
                policy = admitted()
                sample = deepcopy(complete)
                if defect == "actual_stop":
                    sample["actual_stop"] = True
                elif defect == "unnatural_end":
                    sample["natural_complete"] = False
                else:
                    sample["closure"]["strict_runtime_complete"] = False
                first = policy.evaluate(sample)
                self.assertNotEqual(first["state"], "COMPLETE_CANDIDATE")
                self.assertEqual(policy.evaluate(complete), first)

    def test_declared_synthetic_parent_to_simulator_root_handoff(self):
        child=dict(prelaunch()['identity'],pid=124,start_ticks=457)
        proof=dict(confirmed_by_owner=True,parent_pid=123,parent_start_ticks=456,
                   child_pid=124,child_start_ticks=457)
        policy=admitted()
        self.assertEqual(policy.bind_postfork_root(child,proof)['state'],'PRELAUNCH_READY')
        sample=runtime(1,1,90);sample['identity']=child
        self.assertEqual(policy.evaluate(sample)['state'],'RUNTIME_WARNING')
        for field in ['parent_pid','parent_start_ticks','child_pid','child_start_ticks']:
            with self.subTest(field=field):
                bad=dict(proof);bad[field]+=1
                self.assertEqual(admitted().bind_postfork_root(child,bad)['state'],'RUNTIME_STOP_SAFETY')
        policy=admitted();policy.bind_postfork_root(child,proof)
        self.assertEqual(policy.evaluate(runtime(1,1))['state'],'RUNTIME_STOP_SAFETY')
        # No actual fork, process or simulator is created by this synthetic test.


if __name__ == "__main__":
    unittest.main()
