#!/usr/bin/env python3
"""Disassemble selected unique JIT cubins; static counts never pose as dynamic."""
from __future__ import annotations

import csv
import hashlib
import json
import re
import shutil
import subprocess
from collections import Counter
from pathlib import Path

ROOT = Path('/data/c16/awma/r101r2_s128_native_profile_20260929')
CACHE = ROOT / 'cache/triton'
DISASM = Path('/usr/local/cuda-12.8/bin/nvdisasm')
EXPECTED = {
    'ns5_smem_kernel': 'F128_FUSED_NS5',
    'triton_red_fused_linalg_vector_norm_0': 'K128_NORMALIZATION',
    'XXT_kernel': 'K128_XXT',
    'ba_plus_cAA_kernel': 'K128_BA',
    'bmm_add_kernel': 'K128_BMM_ADD',
}
INSTRUCTION = re.compile(r'/\*[0-9a-fA-F]+\*/\s+([A-Z][A-Z0-9_.]*)\s')


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    cubins = list(CACHE.rglob('*.cubin'))
    assert len(cubins) == 5 and {p.stem for p in cubins} == set(EXPECTED)
    (ROOT / 'raw/cubin').mkdir(parents=True, exist_ok=True)
    (ROOT / 'raw/sass').mkdir(parents=True, exist_ok=True)
    rows = []
    opcodes = []
    for cubin in sorted(cubins):
        name = cubin.stem
        metadata = cubin.with_suffix('.json')
        assert metadata.is_file()
        record = json.loads(metadata.read_text())
        assert record['name'] == name and record['target']['arch'] == 89
        source_copy = ROOT / 'raw/cubin' / cubin.name
        meta_copy = ROOT / 'raw/cubin' / metadata.name
        shutil.copy2(cubin, source_copy)
        shutil.copy2(metadata, meta_copy)
        sass = ROOT / 'raw/sass' / f'{name}.sass.txt'
        result = subprocess.run([str(DISASM), '-c', str(source_copy)], check=True,
                                capture_output=True, text=True)
        sass.write_text(result.stdout)
        names = INSTRUCTION.findall(result.stdout)
        assert names
        counts = Counter(names)
        cat = Counter()
        for opcode in names:
            base = opcode.split('.')[0]
            if base.startswith(('BAR', 'DEPBAR', 'LDGDEPBAR', 'MEMBAR')):
                cat['sync_barrier'] += 1
            elif base == 'LDGSTS':
                cat['global_to_shared_dual'] += 1
            elif base.startswith('LDG'):
                cat['global_load'] += 1
            elif base.startswith('STG'):
                cat['global_store'] += 1
            elif base.startswith(('LDS', 'LDSM')):
                cat['shared_load'] += 1
            elif base.startswith('STS'):
                cat['shared_store'] += 1
            elif base.startswith(('HMMA', 'MMA', 'IMMA', 'BMMA')):
                cat['tensor_mma'] += 1
            elif base.startswith(('IADD', 'IMAD', 'LEA', 'SHF', 'LOP', 'ISETP', 'UISETP',
                                  'BRA', 'EXIT', 'MOV', 'S2R', 'CS2R', 'ULDC', 'IMNMX',
                                  'SEL', 'PRMT', 'IMAD', 'UIADD', 'UMOV', 'USEL')):
                cat['integer_address_control'] += 1
            else:
                cat['fp_or_other'] += 1
        assert sum(cat.values()) == len(names)
        registers = re.search(r'SHI_REGISTERS=(\d+)', result.stdout)
        row = {'family': EXPECTED[name], 'kernel_name': name,
               'cubin_sha256': sha(source_copy), 'metadata_sha256': sha(meta_copy),
               'sass_sha256': sha(sass), 'static_instruction_count': len(names),
               'static_global_load': cat['global_load'],
               'static_global_store': cat['global_store'],
               'static_global_to_shared_dual': cat['global_to_shared_dual'],
               'static_shared_load': cat['shared_load'],
               'static_shared_store': cat['shared_store'],
               'static_tensor_mma': cat['tensor_mma'],
               'static_integer_address_control': cat['integer_address_control'],
               'static_sync_barrier': cat['sync_barrier'],
               'static_fp_or_other': cat['fp_or_other'],
               'registers_per_thread_from_cubin': int(registers.group(1)) if registers else '',
               'shared_bytes_from_jit_metadata': record['shared'],
               'num_warps': record['num_warps'], 'num_stages': record['num_stages'],
               'static_count_not_dynamic': True,
               'static_global_load_including_LDGSTS': cat['global_load'] + cat['global_to_shared_dual'],
               'static_shared_store_including_LDGSTS': cat['shared_store'] + cat['global_to_shared_dual']}
        rows.append(row)
        for opcode, count in sorted(counts.items()):
            opcodes.append({'family': EXPECTED[name], 'kernel_name': name,
                            'opcode': opcode, 'static_count': count})
    rows.append({'family': 'GRAPH_RUNTIME_OTHER', 'kernel_name': 'at::native::FillFunctor<long>',
                 'cubin_sha256': 'UNAVAILABLE_LIBRARY_CUBIN',
                 'metadata_sha256': 'UNAVAILABLE_LIBRARY_CUBIN',
                 'sass_sha256': 'UNAVAILABLE_LIBRARY_CUBIN',
                 'static_instruction_count': 'UNAVAILABLE',
                 'static_global_load': 'UNAVAILABLE', 'static_global_store': 'UNAVAILABLE',
                 'static_global_to_shared_dual': 'UNAVAILABLE',
                 'static_shared_load': 'UNAVAILABLE', 'static_shared_store': 'UNAVAILABLE',
                 'static_tensor_mma': 'UNAVAILABLE',
                 'static_integer_address_control': 'UNAVAILABLE',
                 'static_sync_barrier': 'UNAVAILABLE', 'static_fp_or_other': 'UNAVAILABLE',
                 'registers_per_thread_from_cubin': 'UNAVAILABLE',
                 'shared_bytes_from_jit_metadata': 'UNAVAILABLE',
                 'num_warps': 'UNAVAILABLE', 'num_stages': 'UNAVAILABLE',
                 'static_count_not_dynamic': True,
                 'static_global_load_including_LDGSTS': 'UNAVAILABLE',
                 'static_shared_store_including_LDGSTS': 'UNAVAILABLE'})
    with (ROOT / 'STATIC_SASS_SUMMARY.tsv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), delimiter='\t', lineterminator='\n')
        writer.writeheader(); writer.writerows(rows)
    with (ROOT / 'STATIC_SASS_OPCODE_COUNTS.tsv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(opcodes[0]), delimiter='\t', lineterminator='\n')
        writer.writeheader(); writer.writerows(opcodes)
    (ROOT / 'STATIC_SASS_RECEIPT.json').write_text(json.dumps({
        'selected_cubin_count': 5, 'static_disassembly_pass': True,
        'unique_kernels': [row['kernel_name'] for row in rows[:5]],
        'runtime_fill_library_cubin_unavailable': True,
        'nvdisasm_path': str(DISASM),
        'static_counts_do_not_weight_dynamic_recurrence': True,
    }, indent=2, sort_keys=True) + '\n')
    print(json.dumps({row['family']: row['static_instruction_count'] for row in rows}, sort_keys=True))


if __name__ == '__main__':
    main()
