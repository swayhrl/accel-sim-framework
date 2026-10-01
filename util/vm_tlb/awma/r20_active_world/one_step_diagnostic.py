#!/usr/bin/env python3
"""B1024 same-entry one-step restore versus contact-order diagnosis."""

import hashlib
import json
import os
from pathlib import Path

import mujoco
import numpy as np
import warp as wp

from state_utils import make_gpu_snapshot, restore_gpu_snapshot, sha_numpy


ROOT = Path("/data/c16/awma/r20_active_world_native_v1")
SCENE = ROOT / "scene/unitree_g1_hfield"
RAW = ROOT / "raw"


def canonical_coverage(data):
    from mujoco_warp._src.types import ConstraintType

    first_contact_type = int(ConstraintType.CONTACT_FRICTIONLESS)
    ncon = int(data.nacon.numpy().reshape(-1)[0])
    contact_world = data.contact.worldid.numpy()[:ncon]
    contact_geom = data.contact.geom.numpy()[:ncon]
    contact_gc = data.contact.geomcollisionid.numpy()[:ncon]
    contact_dim = data.contact.dim.numpy()[:ncon]
    contact_type = data.contact.type.numpy()[:ncon]
    nefc = data.nefc.numpy()
    efc_type = data.efc.type.numpy()
    efc_id = data.efc.id.numpy()
    contacts_by_world = [[] for _ in range(len(nefc))]
    contact_key_by_pooled_id = []
    for pooled in range(ncon):
        key = (
            int(contact_geom[pooled, 0]), int(contact_geom[pooled, 1]),
            int(contact_gc[pooled]), int(contact_dim[pooled]), int(contact_type[pooled]),
        )
        contact_key_by_pooled_id.append(key)
        contacts_by_world[int(contact_world[pooled])].append(key)
    contacts_digest = []
    constraints_digest = []
    for world, count in enumerate(nefc):
        contacts = sorted(contacts_by_world[world])
        contacts_digest.append(hashlib.sha256(json.dumps(contacts).encode()).hexdigest())
        constraints = []
        for efcid in range(int(count)):
            kind = int(efc_type[world, efcid])
            cid = int(efc_id[world, efcid])
            # Contact efc.id is a nondeterministically allocated global contact index.
            identity = contact_key_by_pooled_id[cid] if kind >= first_contact_type and 0 <= cid < ncon else cid
            constraints.append((kind, identity))
        constraints_digest.append(hashlib.sha256(json.dumps(sorted(constraints)).encode()).hexdigest())
    return {
        "nacon": ncon,
        "pooled_contact_worldid_sha256": sha_numpy(contact_world),
        "canonical_contact_hashes": contacts_digest,
        "canonical_constraint_hashes": constraints_digest,
        "nefc": nefc,
    }


def main():
    assert os.environ.get("R20_GPU_LOCK_HELD") == "1"
    wp.config.kernel_cache_dir = str(ROOT / "cache/warp")
    wp.init()
    import mujoco_warp as mjw
    from mujoco_warp._src.cli import _ctrl_noise
    from mujoco_warp._src.io import load_trajectory, override_model

    device = wp.get_device("cuda:0")
    mjm = mujoco.MjSpec.from_file(str(SCENE / "scene_hfield.xml")).compile()
    mjd = mujoco.MjData(mjm)
    ctrls = load_trajectory(str(SCENE / "shuffle_dance.npz"), mjm, mjd)
    with wp.ScopedDevice(device):
        model = mjw.put_model(mjm)
        override_model(model, ["opt.warn_overflow=~ITERATIONS|~LS_ITERATIONS"])
        d1 = mjw.put_data(mjm, mjd, nworld=1024, nconmax=48, njmax=192)
        with wp.ScopedCapture() as g1:
            mjw.step(model, d1)

        def ctrl_step(data, step):
            center = wp.array(ctrls[step], dtype=wp.float32, device=device)
            wp.launch(
                _ctrl_noise, dim=(data.nworld, model.nu),
                inputs=[model.opt.timestep, model.actuator_ctrllimited, model.actuator_ctrlrange,
                        data.ctrl, center, step, 0.01, 0.1], outputs=[data.ctrl],
            )
            wp.synchronize()

        for step in range(128):
            ctrl_step(d1, step)
            wp.capture_launch(g1.graph)
            wp.synchronize()
        snapshot = make_gpu_snapshot(d1)
        d2 = mjw.put_data(mjm, mjd, nworld=1024, nconmax=48, njmax=192)
        with wp.ScopedCapture() as g2:
            mjw.step(model, d2)
        wp.synchronize()
        results = []
        for name, data, graph in (("same_graph_0", d1, g1.graph), ("same_graph_1", d1, g1.graph),
                                  ("same_graph_2", d1, g1.graph), ("fresh_graph", d2, g2.graph)):
            restore_gpu_snapshot(data, snapshot)
            ctrl_step(data, 128)
            ctrl = data.ctrl.numpy()
            wp.capture_launch(graph)
            wp.synchronize()
            qpos = data.qpos.numpy()
            qvel = data.qvel.numpy()
            warm = data.qacc_warmstart.numpy()
            niter = data.solver_niter.numpy()
            overflow = data.overflow.numpy()
            coverage = canonical_coverage(data)
            results.append({
                "name": name,
                "qpos": qpos.copy(),
                "qvel": qvel.copy(),
                "qacc_warmstart": warm.copy(),
                "ctrl": ctrl.copy(),
                "niter": niter.copy(),
                "overflow": overflow.copy(),
                "coverage": coverage,
            })
        np.savez_compressed(RAW / "BASELINE_ONE_STEP_REPEAT_STATES.npz", **{
            f"{row['name']}_{key}": row[key] for row in results
            for key in ("qpos", "qvel", "qacc_warmstart", "ctrl", "niter", "overflow")
        })
        baseline = results[0]
        comparisons = []
        for peer in results[1:]:
            contact_diff = sum(a != b for a, b in zip(baseline["coverage"]["canonical_contact_hashes"], peer["coverage"]["canonical_contact_hashes"]))
            constraint_diff = sum(a != b for a, b in zip(baseline["coverage"]["canonical_constraint_hashes"], peer["coverage"]["canonical_constraint_hashes"]))
            comparisons.append({
                "peer": peer["name"],
                "ctrl_bitwise_equal": bool(np.array_equal(baseline["ctrl"], peer["ctrl"])),
                "niter_different_worlds": int(np.count_nonzero(baseline["niter"] != peer["niter"])),
                "overflow_different_worlds": int(np.count_nonzero(baseline["overflow"] != peer["overflow"])),
                "nefc_different_worlds": int(np.count_nonzero(baseline["coverage"]["nefc"] != peer["coverage"]["nefc"])),
                "canonical_contact_set_different_worlds": contact_diff,
                "canonical_constraint_set_different_worlds": constraint_diff,
                "pooled_contact_order_sha256_differs": baseline["coverage"]["pooled_contact_worldid_sha256"] != peer["coverage"]["pooled_contact_worldid_sha256"],
                "qpos_max_abs": float(np.max(np.abs(baseline["qpos"].astype(np.float64) - peer["qpos"].astype(np.float64)))),
                "qvel_max_abs": float(np.max(np.abs(baseline["qvel"].astype(np.float64) - peer["qvel"].astype(np.float64)))),
                "qacc_warmstart_max_abs": float(np.max(np.abs(baseline["qacc_warmstart"].astype(np.float64) - peer["qacc_warmstart"].astype(np.float64)))),
            })
        output = {
            "stage": "AWMA_R20_ACTIVE_WORLD_NATIVE_109_V1",
            "classification": "SAME_FROZEN_ENTRY_ONE_STEP_BASELINE_DIVERGENCE_DIAGNOSTIC",
            "absolute_step": 128,
            "same_graph_repeats": 3,
            "independent_graph_repeats": 1,
            "baseline_nacon": baseline["coverage"]["nacon"],
            "baseline_qpos_sha256": sha_numpy(baseline["qpos"]),
            "comparisons": comparisons,
            "coverage_key": "sorted per-world contact (geom pair,geomcollisionid,dim,type) and sorted constraint (type,contact key or native id)",
            "note": "Source uses global atomic contact allocation and per-world atomic efc row allocation; semantic multiset is distinct from pooled index order.",
        }
        (RAW / "BASELINE_ONE_STEP_CAUSAL_DIAGNOSTIC.json").write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
        print(json.dumps(output, sort_keys=True))


if __name__ == "__main__":
    main()
