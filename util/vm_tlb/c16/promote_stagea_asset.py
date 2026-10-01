#!/usr/bin/env python3
"""Atomically promote an independently verified NFS staging directory."""
from __future__ import annotations

import argparse
import os
from pathlib import Path


ALLOWED={
    'QWEN_BF16':('qwen2.5-3b-instruct','aa8e72537993ba99e69dfaafa59ed015b17504d1'),
    'QWEN_AWQ':('qwen2.5-3b-instruct-awq','3559b226e8ce77211e2c1bd7ddfb7686fec4d6dd'),
}


def main() -> None:
    p=argparse.ArgumentParser()
    p.add_argument('--model-key',choices=ALLOWED,required=True)
    p.add_argument('--durable-root',type=Path,default=Path('/root/share/mnt164/huangrulin/c16_ai_workload/assets/models'))
    args=p.parse_args()
    slug,revision=ALLOWED[args.model_key]
    root=args.durable_root.resolve(strict=True)
    staging_parent=(root/'.c16_stagea_transfer_v1'/slug).resolve(strict=True)
    target_parent=(root/slug)
    target_parent.mkdir(parents=True,exist_ok=True)
    target_parent=target_parent.resolve(strict=True)
    source=staging_parent/revision
    target=target_parent/revision
    if os.path.commonpath((str(root),str(staging_parent)))!=str(root):
        raise AssertionError('staging escapes durable root')
    if os.path.commonpath((str(root),str(target_parent)))!=str(root):
        raise AssertionError('target escapes durable root')
    if not source.is_dir() or target.exists():
        raise AssertionError('missing staged source or final target already exists')
    if source.stat().st_dev!=target_parent.stat().st_dev:
        raise AssertionError('not same-device atomic rename')
    os.rename(source,target)
    print('PROMOTED',args.model_key,str(target))


if __name__=='__main__':
    main()
