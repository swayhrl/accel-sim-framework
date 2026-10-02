#!/usr/bin/env python3
"""CPU-only exact OAM-S package and all-frame sitraj input authority freeze."""

import csv
import hashlib
import json
import math
import re
import subprocess
import zipfile
from pathlib import Path


ROOT = Path("/data/c16/awma/r21a_oeq_graph_readiness_20261002")
WORKTREE = Path("/home/huangrulin/workspace/worktrees/accel-sim-awma-r21a-oeq-graph-readiness-109-v1")
PACK = WORKTREE / "docs/vm_tlb/review_packs/AWMA_R21A_OEQ_GRAPH_READINESS_109_V1"
SOURCE = ROOT / "source/nequip-tutorial/sitraj.xyz"
MODEL = ROOT / "model/NequIP-OAM-S-0.1.nequip.zip"
EXPECTED = {
    "nequip": "27d9d2182da918ab7be0017d8300e53278f5e00e",
    "OpenEquivariance": "dc9979099c65113adcc016977c5c60974f9ddafb",
    "nequip-tutorial": "8f90935ba42fd9e03df323cf03428c456d87b881",
}


def sha(blob):
    return hashlib.sha256(blob).hexdigest()


def det3(v):
    a, b, c, d, e, f, g, h, i = v
    return a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)


def parse_frames(blob):
    lines = blob.splitlines(keepends=True)
    index = 0
    rows = []
    while index < len(lines):
        start = index
        count = int(lines[index].decode().strip())
        if count <= 0 or index + count + 2 > len(lines):
            raise RuntimeError(f"Malformed frame at line {index+1}")
        header = lines[index + 1].decode()
        lattice = re.search(r'Lattice="([^"]+)"', header)
        pbc = re.search(r'pbc="([^"]+)"', header)
        energy = re.search(r'(?:^|\s)energy=([^\s]+)', header)
        stress = re.search(r'stress="([^"]+)"', header)
        if not (lattice and pbc and energy and stress):
            raise RuntimeError(f"Missing required extended-XYZ metadata in frame {len(rows)}")
        cell = [float(x) for x in lattice.group(1).split()]
        stress_label = [float(x) for x in stress.group(1).split()]
        if len(cell) != 9 or len(stress_label) != 9 or not all(math.isfinite(x) for x in cell + stress_label):
            raise RuntimeError(f"Invalid cell/stress metadata in frame {len(rows)}")
        pbc_tokens = pbc.group(1).split()
        if pbc_tokens != ["T", "T", "T"] or abs(det3(cell)) <= 0:
            raise RuntimeError(f"Non-periodic or empty cell in frame {len(rows)}")
        coords = []
        force_labels = []
        for atom_line in lines[index + 2:index + 2 + count]:
            fields = atom_line.decode().split()
            if len(fields) != 7 or fields[0] != "Si":
                raise RuntimeError(f"Non-Si or wrong atom fields in frame {len(rows)}")
            xyzf = [float(x) for x in fields[1:]]
            if not all(math.isfinite(x) for x in xyzf):
                raise RuntimeError(f"Nonfinite atom data in frame {len(rows)}")
            coords.append(xyzf[:3])
            force_labels.append(xyzf[3:])
        e = float(energy.group(1))
        if not math.isfinite(e):
            raise RuntimeError(f"Nonfinite label energy in frame {len(rows)}")
        raw = b"".join(lines[start:index + 2 + count])
        rows.append({"index": len(rows), "atom_count": count, "species": "Si", "periodic": True,
                     "cell_det_A3": det3(cell), "raw_frame_sha256": sha(raw),
                     "positions_sha256": sha(json.dumps(coords, separators=(",", ":")).encode()),
                     "cell": cell, "provided_energy_label": e,
                     "provided_force_label_sha256": sha(json.dumps(force_labels, separators=(",", ":")).encode()),
                     "provided_stress_label_sha256": sha(json.dumps(stress_label, separators=(",", ":")).encode())})
        index += 2 + count
    if index != len(lines):
        raise RuntimeError("Trailing unparsed source bytes")
    return rows


def main():
    PACK.mkdir(parents=True, exist_ok=True)
    for name, commit in EXPECTED.items():
        observed = subprocess.check_output(["git", "-C", str(ROOT / "source" / name), "rev-parse", "HEAD"], text=True).strip()
        if observed != commit:
            raise RuntimeError(f"{name} source revision changed")
    blob = SOURCE.read_bytes()
    git_blob = subprocess.check_output(["git", "-C", str(ROOT / "source/nequip-tutorial"), "hash-object", "sitraj.xyz"], text=True).strip()
    if len(blob) != 784661 or git_blob != "baac4e23364d00d29b2410fa60a92ade0cbf35a3":
        raise RuntimeError("Frozen sitraj bytes do not match Git authority")
    frames = parse_frames(blob)
    n = len(frames)
    if n < 12:
        raise RuntimeError("N < 12")
    chosen = [("DISCOVERY", n // 2), ("HOLDOUT_1", n // 6), ("HOLDOUT_2", n // 3),
              ("HOLDOUT_3", (2 * n) // 3), ("HOLDOUT_4", (5 * n) // 6)]
    if len({i for _, i in chosen}) != 5 or any(not 0 <= i < n for _, i in chosen):
        raise RuntimeError("Frozen index formula not five distinct legal frames")
    with (PACK / "FRAME_SELECTION.tsv").open("w", newline="") as stream:
        fields = ("role", "frame_index", "frame_sha256", "atom_count", "species", "periodic", "cell_det_A3", "provided_energy_label")
        writer = csv.DictWriter(stream, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for role, i in chosen:
            r = frames[i]
            writer.writerow({"role": role, "frame_index": i, "frame_sha256": r["raw_frame_sha256"],
                             "atom_count": r["atom_count"], "species": r["species"],
                             "periodic": int(r["periodic"]), "cell_det_A3": r["cell_det_A3"],
                             "provided_energy_label": r["provided_energy_label"]})
    authority = {"repo": "mir-group/nequip-tutorial", "commit": EXPECTED["nequip-tutorial"],
                 "file": "sitraj.xyz", "git_blob": git_blob, "bytes": len(blob),
                 "sha256": sha(blob), "frame_count": n, "frame_order_interpreted_as_time": False,
                 "selection_formula": "N//2; N//6,N//3,2*N//3,5*N//6",
                 "selected": [{"role": role, **frames[i]} for role, i in chosen],
                 "all_frames_parsed_and_finite_periodic_Si": True,
                 "provided_energy_force_stress_are_provenance_only": True}
    (PACK / "INPUT_AUTHORITY.json").write_text(json.dumps(authority, indent=2, sort_keys=True) + "\n")
    model_blob = MODEL.read_bytes()
    with zipfile.ZipFile(MODEL) as z:
        names = z.namelist()
        metadata_name = next(x for x in names if x.endswith("/model/package_metadata.txt"))
        config_name = next(x for x in names if x.endswith("/model/config.yaml"))
        metadata = z.read(metadata_name)
        config = z.read(config_name)
        if b"Si" not in metadata or b"available_models:" not in metadata:
            raise RuntimeError("OAM-S package metadata missing Si/model entries")
    model = {"requested_id": "nequip.net:mir-group/NequIP-OAM-S:0.1",
             "official_api": "https://www.nequip.net/api/models/download/mir-group%2FNequIP-OAM-S%3A0.1",
             "official_artifact": "https://zenodo.org/api/records/18775904/files/NequIP-OAM-S-0.1.nequip.zip/content",
             "zenodo_record": "18775904", "zenodo_declared_md5": "399a98bf36fc4550bc85d48f35451c6c",
             "bytes": len(model_blob), "sha256": sha(model_blob),
             "md5": hashlib.md5(model_blob).hexdigest(),
             "package_metadata_sha256": sha(metadata), "package_config_sha256": sha(config),
             "package_metadata_text": metadata.decode(), "loaded_runtime_object_verified": False}
    if model["bytes"] != 5638676 or model["md5"] != model["zenodo_declared_md5"]:
        raise RuntimeError("Official OAM-S package checksum/size mismatch")
    (PACK / "MODEL_AUTHORITY.json").write_text(json.dumps(model, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"N": n, "selected": chosen, "input_sha256": sha(blob),
                      "model_sha256": sha(model_blob), "model_bytes": len(model_blob)}, sort_keys=True))


if __name__ == "__main__":
    main()
