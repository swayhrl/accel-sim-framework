"""PREPARED_NOT_EXECUTED: three small declared-data usage cases, not live proof.

No /proc, process creation, compilation or actual-role query. Production's
binding rejection is reserved for a later query of the same actual live role.
"""
from copy import deepcopy
import unittest
from external_cpu_launch_view import ExternalCPULaunchView, ExternalCPUReject


ROLE = "COV1_TINY_MATH_REFERENCE_FOUR_TESTS"


def example():
    digest = "a" * 64
    manager = dict(boot_id="boot", pid=100, start_ticks=10, tgid=100,
                   ppid=1, tracer_pid=0, state="R", argv=["/fixed/python", "manager"],
                   cwd="/fixed/manager", exe="/fixed/python")
    child = dict(manager, pid=200, start_ticks=20, tgid=200, ppid=100,
                 argv=["/fixed/python", "tiny"], cwd="/fixed/worker")
    attrs = dict(cwd=child["cwd"], executable=child["exe"],
                 executable_sha256=digest, source_sha256={"/fixed/tiny.py": digest})
    trust = dict(release_sha256="1"*64, role_contract_sha256="2"*64,
                 admission_policy_sha256="3"*64, manager_role_sha256="4"*64,
                 manager=dict(attrs, instance=manager, argv=manager["argv"],
                              cwd=manager["cwd"], source_sha256={"/fixed/manager.py": digest}),
                 roles={ROLE: dict(attrs, phases={"test": dict(
                     argv=child["argv"], max_runtime_ns=1000, output_bound_bytes=1024)})})
    admissions = {ROLE: {"test": dict(receipt_sha256="5"*64, policy_sha256="3"*64,
        status="PASS", scope="CPU_ONLY", valid_from_monotonic_ns=900,
        valid_until_monotonic_ns=2000)}}
    launch = dict(role_name=ROLE, phase="test", instance=child,
        manager_instance=manager, actual_launch_id="direct-popen-1", state="ACTIVE",
        release_sha256="1"*64, role_contract_sha256="2"*64,
        admission_policy_sha256="3"*64, admission_sha256="5"*64,
        argv=child["argv"], cwd=child["cwd"], executable=child["exe"],
        launched_monotonic_ns=1000, deadline_monotonic_ns=2000, output_bound_bytes=1024)
    provider = dict(manager_instance=manager, manager_role_sha256="4"*64,
                    launches=[launch])
    processes = {100: manager, 200: child}
    reader = lambda pid: deepcopy(processes.get(pid))
    view = ExternalCPULaunchView(trusted=trust, admissions=admissions,
        provider=lambda: provider, identity_reader=reader, process_reader=reader,
        monotonic_ns=lambda: 1500, file_sha256_reader=lambda path: digest)
    return view, provider, processes


class DeclaredUsage(unittest.TestCase):
    def test_accepts_only_readonly_observation_without_mutation(self):
        view, provider, _ = example()
        before = deepcopy(provider)
        row = view.observe(ROLE, dict(pid=200, start_ticks=20), callback_sample_id="s1")
        self.assertTrue(row["live_observation"])
        self.assertFalse(row["ownership_granted"])
        self.assertEqual(provider, before)
        with self.assertRaises(TypeError):
            row["ownership_granted"] = True

    def test_provider_cannot_validate_its_own_changed_release(self):
        view, provider, _ = example()
        provider["launches"][0]["release_sha256"] = "9"*64
        with self.assertRaisesRegex(ExternalCPUReject, "EXTERNAL_BINDING_CHANGED"):
            view.observe(ROLE, dict(pid=200, start_ticks=20), callback_sample_id="s2")

    def test_natural_disappearance_is_not_a_cached_live_acceptance(self):
        view, _, processes = example()
        processes.pop(200)
        row = view.observe(ROLE, dict(pid=200, start_ticks=20), callback_sample_id="s3")
        self.assertEqual(row["classification"], "NOT_CURRENT")
        self.assertFalse(row["live_observation"])


if __name__ == "__main__":
    unittest.main()
