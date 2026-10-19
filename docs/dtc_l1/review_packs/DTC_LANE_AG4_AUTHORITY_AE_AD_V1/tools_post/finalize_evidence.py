"""Post-terminal evidence packaging only. No runner imports or launch interface."""
from common import *
import shutil
import time


def main():
    terminal=RAW/'COHORT_TERMINAL.json'
    release=RAW/'AUTHORITY_RELEASE.json'
    if not terminal.is_file() or not release.is_file():
        raise ValueError('COHORT_NOT_TERMINAL_AND_RELEASED')
    os.nice(19)
    dest=PACK/'execution_receipts'
    dest.mkdir(exist_ok=True)
    copied=[]
    for name in ['PREREG_PUBLICATION_READBACK.json','COHORT_TERMINAL.json','AUTHORITY_RELEASE.json']:
        source=RAW/name;target=dest/name
        shutil.copyfile(source,target)
        copied.append(dict(source=str(source),destination=str(target.relative_to(PACK)),bytes=source.stat().st_size,sha256=sha(source)))
    selected=['RUN_START.json','RUN_TERMINAL.json','STRICT.json','ADMISSION.json',
              'WRAPPER_EXCEPTION.json','ACTUAL_EARLY_EFFECTIVE_OPTIONS.json',
              'ENGINE/FORK_CHILD.json','ENGINE/CHILD.json','ENGINE/START.json',
              'ENGINE/TERMINAL.json','KERNEL_STRICT.tsv']
    for run in sorted((RAW/'attempts').glob('*')):
        if not run.is_dir():continue
        for name in selected:
            source=run/name
            if not source.is_file():continue
            target=dest/run.name/name
            target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(source,target)
            copied.append(dict(source=str(source),destination=str(target.relative_to(PACK)),bytes=source.stat().st_size,sha256=sha(source)))
    write(PACK/'EXECUTION_RECEIPT_BINDINGS.json',dict(utc=now(),rows=copied,large_raw_in_Git=False,post_terminal_only=True))
    # Bounded namespace: only the newly owned raw root. SHA reads are low priority
    # and limited to8MiB/s; no external raw search and no decompressed trace copy.
    raw_index=RAW/'FINAL_FILES_SHA256.tsv';raw_rows=[]
    started=time.monotonic();read_bytes=0
    for path in sorted(RAW.rglob('*')):
        if not path.is_file() or path==raw_index:continue
        h=hashlib.sha256()
        with path.open('rb') as f:
            for block in iter(lambda:f.read(1024*1024),b''):
                h.update(block);read_bytes+=len(block)
                delay=read_bytes/(8*1024*1024)-(time.monotonic()-started)
                if delay>0:time.sleep(min(delay,1))
        raw_rows.append(dict(path=str(path.relative_to(RAW)),bytes=path.stat().st_size,sha256=h.hexdigest()))
    table(raw_index,raw_rows)
    write(PACK/'RAW_INDEX_BINDING.json',dict(snapshot_utc=now(),path=str(raw_index),sha256=sha(raw_index),files=len(raw_rows),read_bytes=read_bytes,scope='new AG4 raw at this pre-final-publication snapshot only',includes_ordinary_failed_CPU_receipts=True,excluded_self_only=str(raw_index),later_final_publication_receipt='written separately after push/fetch-back; cannot be part of its own preceding Git/index snapshot'))
    # This exact pathname is excluded; nested historical indices are included.
    pack_index=PACK/'FILES_SHA256.tsv'
    table(pack_index,[dict(path=str(p.relative_to(PACK)),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(PACK.rglob('*')) if p.is_file() and p!=pack_index and '__pycache__' not in p.parts])
    print(json.dumps(dict(status='PASS_POST_TERMINAL_EVIDENCE_PACKAGED',copied_receipts=len(copied),raw_files=len(raw_rows),pack_index_sha256=sha(pack_index))))


if __name__=='__main__':main()
