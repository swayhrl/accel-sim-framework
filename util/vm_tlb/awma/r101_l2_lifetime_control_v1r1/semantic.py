#!/usr/bin/env python3
"""Untimed bitwise/liveness gate before R101R1 profiling or formal timing."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import torch

from core import ROOT, R101, Discard, author_reference, capture, load_tiles


def tensor_sha(tensor: torch.Tensor) -> str:
    return hashlib.sha256(tensor.detach().contiguous().view(torch.uint8).cpu().numpy().tobytes()).hexdigest()


def main() -> None:
    prereg = json.loads((ROOT / 'PREREGISTRATION.json').read_text())
    assert prereg['bitwise_d1_b0_required'] is True
    discarder = Discard()
    records = []
    output_archive = {}
    with torch.no_grad():
        for edge in (128, 512):
            x = load_tiles('discovery', edge)
            reference = author_reference(x)
            b0_graph, b0 = capture(x, None)
            d1_graph, d1 = capture(x, discarder)
            b0_snapshot = b0.detach().clone()
            d1_snapshot = d1.detach().clone()
            author_close = bool(torch.allclose(b0_snapshot, reference, rtol=1e-2, atol=1e-2))
            bitwise = bool(torch.equal(b0_snapshot, d1_snapshot))
            baseline_repeat = []
            d1_repeat = []
            for _ in range(2):
                b0_graph.replay()
                d1_graph.replay()
                torch.cuda.synchronize()
                baseline_repeat.append(bool(torch.equal(b0, b0_snapshot)))
                d1_repeat.append(bool(torch.equal(d1, d1_snapshot)))
            old = x[0, 0, 0].clone()
            x[0, 0, 0] = old + 1.0
            b0_graph.replay()
            d1_graph.replay()
            torch.cuda.synchronize()
            changed_b0 = not bool(torch.equal(b0, b0_snapshot))
            changed_d1 = not bool(torch.equal(d1, d1_snapshot))
            x[0, 0, 0] = old
            b0_graph.replay()
            d1_graph.replay()
            torch.cuda.synchronize()
            restored_b0 = bool(torch.equal(b0, b0_snapshot))
            restored_d1 = bool(torch.equal(d1, d1_snapshot))
            finite_b0 = bool(torch.isfinite(b0_snapshot).all())
            finite_d1 = bool(torch.isfinite(d1_snapshot).all())
            record = {
                'fixture': 'discovery', 'edge': edge,
                'shape': str(tuple(x.shape)),
                'input_pointer_128_aligned': x.data_ptr() % 128 == 0,
                'b0_author_tolerance_pass': author_close,
                'b0_d1_bitwise_equal': bitwise,
                'baseline_repeat_bitwise': all(baseline_repeat),
                'd1_repeat_bitwise': all(d1_repeat),
                'baseline_perturb_changed': changed_b0,
                'd1_perturb_changed': changed_d1,
                'baseline_restore_bitwise': restored_b0,
                'd1_restore_bitwise': restored_d1,
                'baseline_finite': finite_b0,
                'd1_finite': finite_d1,
                'baseline_output_sha256': tensor_sha(b0_snapshot),
                'd1_output_sha256': tensor_sha(d1_snapshot),
            }
            records.append(record)
            output_archive[f'K{edge}_B0'] = b0_snapshot.cpu()
            output_archive[f'K{edge}_D1'] = d1_snapshot.cpu()
            print(json.dumps(record), flush=True)
            assert all((author_close, bitwise, all(baseline_repeat), all(d1_repeat),
                        changed_b0, changed_d1, restored_b0, restored_d1,
                        finite_b0, finite_d1))
    with (ROOT / 'SEMANTIC_RESULTS.tsv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(records[0]), delimiter='\t', lineterminator='\n')
        writer.writeheader()
        writer.writerows(records)
    (ROOT / 'SEMANTIC_RECEIPT.json').write_text(json.dumps({
        'discovery_bitwise_and_liveness_qualified': True,
        'accepted_author_tolerance_used_only_for_wrapper_vs_author_reference': True,
        'no_numeric_tolerance_used_for_B0_vs_D1': True,
    }, indent=2, sort_keys=True) + '\n')
    torch.save(output_archive, ROOT / 'raw/semantic_outputs.pt')


if __name__ == '__main__':
    main()
