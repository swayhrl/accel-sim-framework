#!/usr/bin/env python3
"""Render paper-style C2P locality/admission mechanism figures.

These are extension figures, not replacements for C2P-Cache paper Fig. 10--14.
They read checked CSVs produced by the locality and remote-tag runners.
"""

import argparse
import csv
import warnings
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


STYLE = {
    "tag7": ("tag lookup = 7", "#e89b88", "xx"),
    "tag14": ("tag lookup = 14", "#9ecae1", "///"),
    "candidate": ("Candidates", "#9aa8b0", ""),
    "probe": ("Probes", "#e4a72c", "//"),
    "hit": ("Remote hits", "#dc8a7b", "xx"),
}
NAMES = {
    "btree": "Btree", "2DConvolution": "2D", "c2p-ispass-bfs": "BFS",
    "c2p-ispass-lps": "LPS", "gemm": "GEMM", "atax": "ATAx",
}


def rows(path):
    with open(path, newline="") as stream:
        return list(csv.DictReader(stream))


def setup():
    plt.rcParams.update({
        "font.family": "serif", "font.serif": ["Times New Roman", "DejaVu Serif"],
        "font.size": 9, "axes.linewidth": 0.8, "pdf.fonttype": 42,
        "ps.fonttype": 42, "hatch.linewidth": 0.35,
    })


def save(fig, out, stem):
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="This figure includes Axes")
        fig.tight_layout(pad=0.55)
    for ext in ("pdf", "svg", "png"):
        fig.savefig(out / f"{stem}.{ext}", bbox_inches="tight", dpi=300)
    plt.close(fig)


def remote_tag_figure(canonical, out):
    cases = [r["case"] for r in canonical]
    labels = [NAMES[c] for c in cases]
    x, width = np.arange(len(cases)), 0.34
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.65), gridspec_kw={"wspace": 0.35})

    ipc14 = [int(r["tag7_cycles"]) / int(r["tag14_cycles"]) for r in canonical]
    axes[0].bar(x - width / 2, np.ones(len(cases)), width, label=STYLE["tag7"][0],
                color=STYLE["tag7"][1], hatch=STYLE["tag7"][2], edgecolor="black")
    axes[0].bar(x + width / 2, ipc14, width, label=STYLE["tag14"][0],
                color=STYLE["tag14"][1], hatch=STYLE["tag14"][2], edgecolor="black")
    axes[0].axhline(1, color="black", linewidth=0.8)
    axes[0].set_ylim(0.96, 1.01)
    axes[0].set_ylabel("Normalized IPC\n(tag7 = 1)")
    axes[0].set_xticks(x, labels)
    axes[0].legend(frameon=False, fontsize=8, loc="lower left")
    axes[0].set_title("(a) Performance")

    hit14 = [int(r["tag14_hits"]) / int(r["tag7_hits"]) for r in canonical]
    l214 = [int(r["tag14_l2"]) / int(r["tag7_l2"]) for r in canonical]
    axes[1].bar(x - width / 2, hit14, width, label="Remote hits", color=STYLE["hit"][1],
                hatch=STYLE["hit"][2], edgecolor="black")
    axes[1].bar(x + width / 2, l214, width, label="L2 accesses", color="#9aa8b0",
                edgecolor="black")
    axes[1].axhline(1, color="black", linewidth=0.8)
    axes[1].set_ylabel("Tag14 / tag7")
    axes[1].set_xticks(x, labels)
    axes[1].legend(frameon=False, fontsize=8, loc="lower right")
    axes[1].set_title("(b) Realized remote opportunity")
    save(fig, out, "figx_remote_tag_sensitivity")


def locality_figure(locality, out):
    ordered = ["btree", "2DConvolution", "c2p-ispass-bfs", "c2p-ispass-lps", "gemm", "atax"]
    by_case = {r["case"]: r for r in locality}
    x, width = np.arange(len(ordered)), 0.24
    fig, ax = plt.subplots(figsize=(7.0, 2.65))
    for offset, key, local, outer in (
        (-width, "candidate", "candidates_local", "candidates_outer"),
        (0, "probe", "probes_local", "probes_outer"),
        (width, "hit", "hits_local", "hits_outer"),
    ):
        vals = [int(by_case[c][local]) / (int(by_case[c][local]) + int(by_case[c][outer])) for c in ordered]
        name, color, hatch = STYLE[key]
        ax.bar(x + offset, vals, width, label=name, color=color, hatch=hatch, edgecolor="black")
    ax.set_ylim(0, 0.62)
    ax.set_ylabel("Local share")
    ax.set_xticks(x, [NAMES[c] for c in ordered])
    ax.axhline(0.25, color="#666666", linestyle="--", linewidth=0.8, label="4-SM uniform share")
    ax.legend(frameon=False, ncol=4, fontsize=8, loc="upper center")
    ax.set_title("4-SM locality quality: local candidates, probes, and hits")
    save(fig, out, "figx_locality_quality")


def admission_figure(admission, out):
    cases = [r["case"] for r in admission]
    labels = [NAMES[c] for c in cases]
    x, width = np.arange(len(cases)), 0.34
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.65), gridspec_kw={"wspace": 0.35})
    ipc7 = [int(r["control7_cycles"]) / int(r["policy7_cycles"]) for r in admission]
    ipc14 = [int(r["control14_cycles"]) / int(r["policy14_cycles"]) for r in admission]
    axes[0].bar(x - width / 2, ipc7, width, label=STYLE["tag7"][0], color=STYLE["tag7"][1],
                hatch=STYLE["tag7"][2], edgecolor="black")
    axes[0].bar(x + width / 2, ipc14, width, label=STYLE["tag14"][0], color=STYLE["tag14"][1],
                hatch=STYLE["tag14"][2], edgecolor="black")
    axes[0].axhline(1, color="black", linewidth=0.8)
    axes[0].set_ylim(0.98, 1.04)
    axes[0].set_ylabel("Policy IPC / control IPC")
    axes[0].set_xticks(x, labels)
    axes[0].legend(frameon=False, fontsize=8, loc="upper left")
    axes[0].set_title("(a) Admission performance")

    probe7 = [int(r["policy7_probes"]) / int(r["control7_probes"]) for r in admission]
    probe14 = [int(r["policy14_probes"]) / int(r["control14_probes"]) for r in admission]
    axes[1].bar(x - width / 2, probe7, width, label=STYLE["tag7"][0], color=STYLE["tag7"][1],
                hatch=STYLE["tag7"][2], edgecolor="black")
    axes[1].bar(x + width / 2, probe14, width, label=STYLE["tag14"][0], color=STYLE["tag14"][1],
                hatch=STYLE["tag14"][2], edgecolor="black")
    axes[1].axhline(1, color="black", linewidth=0.8)
    axes[1].set_ylim(0, 1.05)
    axes[1].set_ylabel("Policy probes / control probes")
    axes[1].set_xticks(x, labels)
    axes[1].set_title("(b) Probe reduction")
    save(fig, out, "figx_outer_admission_sensitivity")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--remote-root", type=Path, required=True)
    parser.add_argument("--locality-csv", type=Path, nargs="+", required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    setup()
    args.out.mkdir(parents=True, exist_ok=True)
    canonical = rows(args.remote_root / "canonical" / "canonical.csv")
    admission = rows(args.remote_root / "admission" / "admission.csv")
    locality = [rows(path)[0] for path in args.locality_csv]
    remote_tag_figure(canonical, args.out)
    locality_figure(locality, args.out)
    admission_figure(admission, args.out)
    args.out.joinpath("figure_extension_audit.md").write_text(
        "# C2P locality/admission extension figures\n\n"
        "These figures use checked local measurements. They are paper-style extension "
        "figures, not claims of a direct counterpart in the C2P-Cache paper.\n\n"
        "- `figx_remote_tag_sensitivity`: global remote tag 7-to-14 sensitivity.\n"
        "- `figx_locality_quality`: 4-SM local candidate/probe/hit shares.\n"
        "- `figx_outer_admission_sensitivity`: policy vs local-first control; Btree is "
        "excluded because t3/t4 already establish it as an admission negative.\n"
    )


if __name__ == "__main__":
    main()
