#!/usr/bin/env python3
"""CPU-only deterministic asset packaging of the one approved G1 hfield scene."""

import hashlib
import json
import shutil
from pathlib import Path

import mujoco


ROOT = Path("/data/c16/awma/r20_active_world_native_v1")
SOURCE = ROOT / "source/mujoco_warp/benchmarks/unitree_g1"
MENAGERIE = ROOT / "source/mujoco_menagerie/unitree_g1/assets"
SCENE = ROOT / "scene/unitree_g1_hfield"
RAW = ROOT / "raw"


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1048576), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    SCENE.mkdir(parents=True, exist_ok=True)
    (SCENE / "assets").mkdir(parents=True, exist_ok=True)
    copied = []
    for source in (SOURCE / "scene_hfield.xml", SOURCE / "unitree_g1_mjlab.xml", SOURCE / "shuffle_dance.npz", SOURCE / "assets/hfield.png"):
        destination = (SCENE / "assets" / source.name) if source.name == "hfield.png" else (SCENE / source.name)
        shutil.copy2(source, destination)
        assert sha(source) == sha(destination)
        copied.append({"source": str(source), "derived_path": str(destination), "sha256": sha(destination), "bytes": destination.stat().st_size})
    for source in sorted(MENAGERIE.iterdir()):
        if not source.is_file():
            continue
        destination = SCENE / "assets" / source.name
        if destination.exists():
            raise RuntimeError(f"Menagerie/local asset name collision: {source.name}")
        shutil.copy2(source, destination)
        assert sha(source) == sha(destination)
        copied.append({"source": str(source), "derived_path": str(destination), "sha256": sha(destination), "bytes": destination.stat().st_size})
    spec = mujoco.MjSpec.from_file(str(SCENE / "scene_hfield.xml"))
    model = spec.compile()
    opt = model.opt
    receipt = {
        "stage": "AWMA_R20_ACTIVE_WORLD_NATIVE_109_V1",
        "classification": "RECONSTRUCTED_ASSET_LAYOUT_EXACT_SOURCE_BYTES",
        "scene_xml": str(SCENE / "scene_hfield.xml"),
        "scene_xml_sha256": sha(SCENE / "scene_hfield.xml"),
        "trajectory": str(SCENE / "shuffle_dance.npz"),
        "trajectory_sha256": sha(SCENE / "shuffle_dance.npz"),
        "asset_files": copied,
        "mujoco_version": mujoco.__version__,
        "model_nq": model.nq,
        "model_nv": model.nv,
        "model_nu": model.nu,
        "model_nbody": model.nbody,
        "model_ngeom": model.ngeom,
        "model_nmesh": model.nmesh,
        "model_nhfield": model.nhfield,
        "opt_timestep": float(opt.timestep),
        "opt_iterations": int(opt.iterations),
        "opt_ls_iterations": int(opt.ls_iterations),
        "opt_integrator": int(opt.integrator),
        "opt_solver": int(opt.solver),
        "opt_cone": int(opt.cone),
        "opt_jacobian": int(opt.jacobian),
        "opt_tolerance": float(opt.tolerance),
        "opt_ls_tolerance": float(opt.ls_tolerance),
        "opt_disableflags": int(opt.disableflags),
    }
    (RAW / "SCENE_MODEL_RECEIPT.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps({key: receipt[key] for key in (
        "classification", "mujoco_version", "model_nq", "model_nv", "model_nu",
        "opt_timestep", "opt_iterations", "opt_ls_iterations", "opt_integrator",
        "opt_solver", "opt_cone", "opt_jacobian", "opt_tolerance", "opt_ls_tolerance"
    )}, sort_keys=True))


if __name__ == "__main__":
    main()
