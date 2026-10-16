#!/usr/bin/python3
"""Plot a Lane-5 hash-bound partial/full WB packet; keep missing/failed rows visible."""
import argparse
import json
from pathlib import Path
import os
from result_intake import read_published_packet, summarize, WORKLOADS


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("adapter", type=Path, help="Local file containing exact published receipt/bundle bindings")
    p.add_argument("--framework-repo", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    a = p.parse_args()
    spec = json.loads(a.adapter.read_text())
    if "native_pairs" in spec:
        from native_pair_intake import read_native_packet
        packet = read_native_packet(a.framework_repo, spec)
    else:
        packet_path = Path(spec["packet_file"])
        if not packet_path.is_absolute(): packet_path = a.adapter.resolve().parent / packet_path
        packet = read_published_packet(a.framework_repo, spec["publication_commit"], spec["receipt_path"],
                                      spec["receipt_sha256"], spec["bundle_path"], spec["bundle_sha256"], packet_path)
    results = summarize(packet)
    if a.output_dir.exists(): raise ValueError("Use a new immutable result revision directory")
    a.output_dir.mkdir(parents=True)
    os.environ.setdefault("MPLBACKEND", "Agg")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 7.5, "svg.fonttype": "none", "svg.hashsalt": "EP_L2_LANE6_R2_PAIRS"})
    fig, ax = plt.subplots(figsize=(3.35, 2.55))
    lookup = {r["workload"]: r for r in results["pairs"]}
    for i, w in enumerate(WORKLOADS):
        if w in lookup:
            ax.bar(i, lookup[w]["speedup"], width=.6, color="#336b8e")
        else:
            ax.text(i, .04, "pending/\nfailed", rotation=90, ha="center", va="bottom", fontsize=6.5)
    ax.axhline(1, color="black", linewidth=.6)
    ax.set_xticks(range(5), ["conv.", "FWT7", "cfd", "vectorAdd", "sad"], rotation=25)
    ax.set_ylim(0, max([1.1] + [r["speedup"] * 1.15 for r in results["pairs"]]))
    ax.set_ylabel("B16 cycles / U_WB16 cycles")
    ax.set_title(f"R0 WB implementation: {len(lookup)}/5 pairs", fontsize=8)
    fig.tight_layout(pad=.6)
    for ext in ("svg", "pdf"):
        dest = a.output_dir / ("WB_PAIRS." + ext)
        fig.savefig(dest, metadata={"Date": None} if ext == "svg" else {"CreationDate": None, "ModDate": None})
        if ext == "svg": dest.write_text("\n".join(x.rstrip() for x in dest.read_text().splitlines()) + "\n")
    plt.close(fig)
    results["publication_binding"] = spec
    results["normalized_runtime_packet"] = packet  # preserve full original native identity vectors
    (a.output_dir / "FIGURE_INPUT_MANIFEST.json").write_text(json.dumps(results, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"pairs": len(lookup), "whole_group_geomean": results["whole_group_geomean"]}))


if __name__ == "__main__": main()
