"""Conservative own-process swap/affinity observations, separate from RSS policy.

Missing VmSwap is never zero. Only independently confirmed own terminated tasks
or double-confirmed disappearance may be censored. Partial observations survive
all failures so the caller can persist them before enforce_observation().
"""
import os
from pathlib import Path

from resource_monitor import MonitorStop

TERMINAL_PS = {"zombie", "dead"}
TERMINAL_PROC = {"Z", "X", "x"}


def _proc_read(pid, member):
    return Path("/proc", str(pid), member).read_text()


def _tasks(pid):
    return [int(p.name) for p in Path("/proc", str(pid), "task").iterdir()]


def _stat(text):
    # comm may contain spaces and ')'; state follows the final ')' delimiter.
    tail = text.rsplit(") ", 1)[1].split()
    if len(tail) < 20:
        raise ValueError("short proc stat")
    return {"state": tail[0], "start_ticks": int(tail[19])}


def _status(text):
    fields = {}
    for line in text.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            fields[key] = value.strip()
    result = {"state": fields.get("State", "").split(" ", 1)[0] or None,
              "VmSwap_bytes": None}
    if "VmSwap" in fields:
        parts = fields["VmSwap"].split()
        if len(parts) != 2 or parts[1] != "kB":
            raise ValueError("invalid VmSwap units")
        amount = int(parts[0])
        if amount < 0:
            raise ValueError("negative VmSwap")
        result["VmSwap_bytes"] = amount * 1024
    return result


def observe_processes(ps, row, identities, root_pid, worker_pid,
                      training_affinity, *, supervisor_affinity=None,
                      normal_worker_exit=None, proc_read=None, task_ids=None,
                      affinity_get=None):
    """Return complete partial evidence; no GPU, lock, signal or service calls.

    ps is psutil or a CPU mock. identities maps PID->accepted creation_time from
    the current OwnLifecycle. Only current RSS-own enumeration observations are
    eligible. normal_worker_exit, if used, must identify that exact worker:
    {pid, creation_time, returncode:0}; independent disappearance is rechecked here.
    The supervisor must still enforce sampled RSS, cgroup charged memory, gate
    and GPU conditions. This function does not broaden any RSS exit-race rule.
    """
    read = proc_read or _proc_read
    tasks = task_ids or _tasks
    affinity = affinity_get or os.sched_getaffinity
    result = {
        "observed_live_VmSwap_subtotal_bytes": 0,
        "censored": [], "affinity_violations": [], "gaps": [],
        "process_observations": [], "swap_observation_complete": True,
        "scope": "Observed own live VmSwap subtotal; missing/terminated values remain None, never zero. Not a complete process-tree swap peak.",
        "rss_policy_change": False,
    }
    inherited_gaps = list(row.get("monitor_gaps", []))
    for key in ("unknown_gpu_pids", "invalid_pid_rows",
                "unqualified_external_gpu_pids", "shared_gate_error"):
        if row.get(key):
            inherited_gaps.append("INDEPENDENT_" + key)
    result["inherited_monitor_gaps"] = inherited_gaps
    for gap in inherited_gaps:
        result["gaps"].append("INDEPENDENT_MONITOR_GAP:" + str(gap))
    accepted = {}
    for item in row.get("rss_observed_processes", []):
        pid = item.get("pid")
        if pid in accepted and accepted[pid] != item.get("creation_time"):
            result["gaps"].append("CONFLICTING_OWN_ENUMERATION:" + str(pid))
        accepted[pid] = item.get("creation_time")
    live = list(row.get("live_own_pids", []))
    if len(set(live)) != len(live):
        result["gaps"].append("DUPLICATE_LIVE_OWN_PID")

    def absent_twice(pid, evidence):
        try:
            evidence["pid_exists_recheck"] = bool(ps.pid_exists(pid))
            if evidence["pid_exists_recheck"]:
                return False
            try:
                fresh = ps.Process(pid)
                evidence["fresh_creation_time"] = fresh.create_time()
                return False
            except ps.NoSuchProcess:
                evidence["fresh_Process_NoSuchProcess"] = True
            for i in (1, 2):
                try:
                    evidence["proc_stat_recheck_%d" % i] = _stat(read(pid, "stat"))
                    return False
                except FileNotFoundError:
                    evidence["proc_stat_absent_%d" % i] = True
            return True
        except Exception as error:
            evidence["absence_recheck_error"] = type(error).__name__
            return False

    def healthy(pid, label):
        evidence = {"pid": pid, "classification": label}
        try:
            if pid is None or pid not in identities:
                evidence["error"] = "NO_ACCEPTED_IDENTITY"
                return False, evidence
            process = ps.Process(pid)
            evidence.update(creation_time=process.create_time(),
                            ps_status=process.status(), is_running=process.is_running())
            before = _stat(read(pid, "stat"))
            after = _stat(read(pid, "stat"))
            evidence.update(proc_stat_before=before, proc_stat_after=after)
            ok = (evidence["creation_time"] == identities[pid]
                  and evidence["is_running"]
                  and evidence["ps_status"] not in TERMINAL_PS
                  and before["state"] not in TERMINAL_PROC
                  and after["state"] not in TERMINAL_PROC
                  and before["start_ticks"] == after["start_ticks"]
                  and ps.Process(pid).create_time() == identities[pid])
            return bool(ok), evidence
        except Exception as error:
            evidence["error"] = type(error).__name__
            return False, evidence

    root_ok, root_health = healthy(root_pid, "ROOT_HEALTH")
    result["root_health"] = root_health
    if not root_ok:
        result["gaps"].append("ROOT_NOT_HEALTHY_FOR_PROCESS_OBSERVATION")
    worker_ok, worker_health = healthy(worker_pid, "WORKER_HEALTH")
    if not worker_ok and normal_worker_exit is not None:
        approved = normal_worker_exit
        exact = (isinstance(approved, dict) and approved.get("pid") == worker_pid
                 and type(approved.get("returncode")) is int
                 and approved["returncode"] == 0 and worker_pid in identities
                 and approved.get("creation_time") == identities[worker_pid])
        proof = {"pid": worker_pid, "approved_exit": approved}
        worker_ok = bool(exact and absent_twice(worker_pid, proof))
        worker_health = {"normal_exit_verified": worker_ok, **proof}
    result["worker_health_or_verified_normal_exit"] = worker_health
    if worker_pid is not None and not worker_ok:
        result["gaps"].append("WORKER_NOT_HEALTHY_OR_VERIFIED_NORMAL_EXIT")
    # A missing or not-yet-created worker is harmless when no censorship is needed;
    # it can never serve as the required healthy owner proof for censorship.

    for pid in live:
        observation = {
            "pid": pid, "accepted_creation_time": identities.get(pid),
            "enumerated_creation_time": accepted.get(pid),
            "VmSwap_bytes": None, "before": None, "after": None,
        }
        result["process_observations"].append(observation)
        if (pid not in accepted or pid not in identities
                or accepted[pid] != identities[pid]):
            observation["gap"] = "PID_NOT_VALID_CURRENT_OWN_ENUMERATION"
            result["gaps"].append(observation["gap"] + ":" + str(pid))
            continue
        missing = False
        termination_confirmed = False
        try:
            process = ps.Process(pid)
            before = {"creation_time": process.create_time(),
                      "ps_status": process.status(),
                      "proc_stat": _stat(read(pid, "stat"))}
            observation["before"] = before
            if before["creation_time"] != identities[pid]:
                raise ValueError("PID_REUSE_BEFORE_PROCESS_OBSERVATION")
            status = _status(read(pid, "status"))
            observation["status"] = status
            current = ps.Process(pid)
            after = {"creation_time": current.create_time(),
                     "ps_status": current.status(),
                     "proc_stat": _stat(read(pid, "stat"))}
            observation["after"] = after
            if (after["creation_time"] != identities[pid]
                    or after["proc_stat"]["start_ticks"] != before["proc_stat"]["start_ticks"]):
                raise ValueError("PID_REUSE_DURING_PROCESS_OBSERVATION")
            if status["VmSwap_bytes"] is None:
                missing = True
                recheck_process = ps.Process(pid)
                recheck = {"creation_time": recheck_process.create_time(),
                           "ps_status": recheck_process.status(),
                           "proc_stat": _stat(read(pid, "stat"))}
                observation["terminal_recheck"] = recheck
                if (recheck["creation_time"] != identities[pid]
                        or recheck["proc_stat"]["start_ticks"] != after["proc_stat"]["start_ticks"]):
                    raise ValueError("PID_REUSE_DURING_TERMINAL_RECHECK")
                termination_confirmed = (
                    after["ps_status"] in TERMINAL_PS
                    and recheck["ps_status"] in TERMINAL_PS
                    and after["proc_stat"]["state"] in TERMINAL_PROC
                    and recheck["proc_stat"]["state"] in TERMINAL_PROC
                    and status["state"] in TERMINAL_PROC)
                observation["missing_field_proof"] = {
                    "ps_and_proc_terminal_same_identity": termination_confirmed}
            else:
                observation["VmSwap_bytes"] = status["VmSwap_bytes"]
                result["observed_live_VmSwap_subtotal_bytes"] += status["VmSwap_bytes"]
        except (ps.NoSuchProcess, FileNotFoundError) as error:
            missing = True
            observation["read_error"] = type(error).__name__
            proof = {}
            termination_confirmed = absent_twice(pid, proof)
            observation["disappearance_proof"] = proof
        except Exception as error:
            # AccessDenied, malformed fields, identity conflicts and unknown errors
            # remain explicit fatal gaps. Never turn them into exit censorship.
            observation["gap"] = type(error).__name__ + ":" + str(error)
            result["gaps"].append("PROCESS_OBSERVATION:" + str(pid) + ":" + observation["gap"])
            continue
        if missing:
            if (pid != root_pid and termination_confirmed and root_ok and worker_ok
                    and not result["gaps"] and not inherited_gaps):
                censored = {
                    "pid": pid, "creation_time": identities[pid],
                    "VmSwap_bytes": None, "censored": True,
                    "classification": "OWN_TERMINATED_PROCESS_VMSWAP_CENSORED",
                    "reason": "confirmed_terminal_no_mm" if "missing_field_proof" in observation else "double_confirmed_disappearance",
                    "not_an_RSS_race_classification": True,
                }
                result["censored"].append(censored)
                observation["classification"] = censored["classification"]
                result["swap_observation_complete"] = False
                continue
            observation["gap"] = "MISSING_VMSWAP_NOT_SAFELY_CENSORED"
            result["gaps"].append(observation["gap"] + ":" + str(pid))
            continue
        affinity_tid = None
        try:
            allowed_set = (set(supervisor_affinity) if pid == root_pid and supervisor_affinity is not None
                           else None if pid == root_pid else set(training_affinity))
            for tid in tasks(pid):
                affinity_tid = tid
                allowed = set(affinity(tid))
                item = {"pid": pid, "tid": tid, "CPUs": sorted(allowed)}
                observation.setdefault("affinity", []).append(item)
                if allowed_set is not None and not allowed.issubset(allowed_set):
                    result["affinity_violations"].append(item)
        except Exception as error:
            observation["affinity_error"] = type(error).__name__
            observation["affinity_error_detail"] = {"tid": affinity_tid, "message": str(error), "classification": "UNQUALIFIED_THREAD_OBSERVATION_GAP_NO_CENSOR"}
            result["gaps"].append("AFFINITY_OBSERVATION:" + str(pid) + ":" + type(error).__name__)

    # A legal candidate must not erase another PID's failure discovered later.
    if result["gaps"] or result["affinity_violations"]:
        for item in result["censored"]:
            item["qualification_valid"] = False
        result["swap_observation_complete"] = False
    else:
        for item in result["censored"]:
            item["qualification_valid"] = True
    return result


def enforce_observation(result):
    """Call only after persisting result; never replaces other resource checks."""
    if result["gaps"]:
        raise MonitorStop("RESOURCE_STOP", "Own process VmSwap/identity observation gap: " + ";".join(result["gaps"]))
    if result["affinity_violations"]:
        raise MonitorStop("RESOURCE_STOP", "Owned thread left approved CPU affinity")
