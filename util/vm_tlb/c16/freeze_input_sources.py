#!/usr/bin/env python3
"""Freeze natural text bytes only; no tokenization, inference, or GPU use."""
from __future__ import annotations

import argparse
import hashlib
import json
import time
import urllib.parse
import urllib.request
from urllib.error import HTTPError
from pathlib import Path


WIKITEXT_REVISION='b08601e04326c79dfdd32d625aee71d232d685c3'
WIKITEXT_DATASET='Salesforce/wikitext'
WIKITEXT_CONFIG='wikitext-103-raw-v1'
PG19_OBJECT='validation/11155.txt'
PG19_PREFIX_BYTES=200000
WIKITEXT_ROWS_PER_INPUT=128


def get(url: str) -> bytes:
    request=urllib.request.Request(url,headers={'User-Agent':'C16-CPU-input-freeze/1.0'})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(request,timeout=50) as response:
                return response.read()
        except HTTPError as error:
            if error.code!=429 or attempt==3:
                raise
            time.sleep(4*(attempt+1))
    raise AssertionError('unreachable')


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def dump(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value,indent=2,sort_keys=True,ensure_ascii=False)+'\n',encoding='utf-8')


def wikitext_rows(start: int, length: int=WIKITEXT_ROWS_PER_INPUT) -> tuple[bytes,str]:
    rows=[]; urls=[]
    for offset in range(start,start+length,100):
        count=min(100,start+length-offset)
        query=urllib.parse.urlencode(dict(dataset=WIKITEXT_DATASET,config=WIKITEXT_CONFIG,
                                          split='train',offset=offset,length=count))
        url='https://datasets-server.huggingface.co/rows?'+query
        value=json.loads(get(url))
        rows.extend(value['rows']); urls.append(url)
    if len(rows)!=length or [r['row_idx'] for r in rows]!=list(range(start,start+length)):
        raise AssertionError(f'row identity mismatch at {start}')
    data=''.join(r['row']['text']+'\n' for r in rows).encode('utf-8')
    return data,';'.join(urls)


def row_url(start: int, length: int) -> str:
    query=urllib.parse.urlencode(dict(dataset=WIKITEXT_DATASET,config=WIKITEXT_CONFIG,
                                      split='train',offset=start,length=length))
    return 'https://datasets-server.huggingface.co/rows?'+query


def build(out: Path) -> dict:
    out.mkdir(parents=True,exist_ok=True)
    text_dir=out/'input_sources'
    text_dir.mkdir(parents=True,exist_ok=True)
    old=json.loads((out/'INPUT_SOURCE_FREEZE.json').read_bytes()) if (out/'INPUT_SOURCE_FREEZE.json').is_file() else None
    old_entries={item['source_text_id']:item for item in old['entries']} if old else {}
    dataset_info=json.loads(get('https://huggingface.co/api/datasets/Salesforce/wikitext'))
    if dataset_info['sha']!=WIKITEXT_REVISION:
        raise AssertionError('WikiText repository revision changed before freeze')
    entries=[]
    specs=[(f'TRAIN_A_DISCOVERY_{i:02}',10000+256*i,'DISCOVERY_INPUT') for i in range(4)]
    specs += [(f'TRAIN_B_SEALED_{i:02}',20000+512*(i-1),'HOLDOUT_INPUT') for i in range(1,16)]
    for name,start,role in specs:
        path=text_dir/(name+'.txt')
        prior=old_entries.get(name)
        if prior and path.is_file():
            data=path.read_bytes()
            if prior['row_end_inclusive']==start+WIKITEXT_ROWS_PER_INPUT-1 and digest(data)==prior['utf8_sha256']:
                url=prior['source_url']
            elif prior['row_end_inclusive']==start+63 and digest(data[:prior['byte_count']])==prior['utf8_sha256']:
                second_url=row_url(start+64,64)
                if len(data)==prior['byte_count']:
                    value=json.loads(get(second_url))
                    rows=value['rows']
                    if [r['row_idx'] for r in rows]!=list(range(start+64,start+128)):
                        raise AssertionError('resume row identity')
                    data+=''.join(r['row']['text']+'\n' for r in rows).encode('utf-8')
                url=prior['source_url']+';'+second_url
            else:
                raise AssertionError(f'cached source byte mismatch {name}')
        else:
            data,url=wikitext_rows(start)
        path.write_bytes(data)
        entries.append(dict(source_text_id=name,role=role,source='WikiText-103 raw',
                            dataset_repository=WIKITEXT_DATASET,observed_dataset_revision=WIKITEXT_REVISION,
                            revision_association='VIEWER_ROWS_NOT_COMMIT_ADDRESSABLE;FROZEN_BYTES_ARE_AUTHORITY',
                            split='train',row_start=start,row_end_inclusive=start+WIKITEXT_ROWS_PER_INPUT-1,
                            source_url=url,relative_path=str(path.relative_to(out)).replace('\\','/'),
                            byte_count=len(data),utf8_sha256=digest(data),
                            selection_rule='fixed 128-row intervals before any model output;preserve each row text then append LF'))
    encoded=urllib.parse.quote(PG19_OBJECT,safe='')
    meta_url=f'https://storage.googleapis.com/storage/v1/b/deepmind-gutenberg/o/{encoded}'
    name='PG19_VALIDATION_11155_PREFIX'
    path=text_dir/(name+'.txt')
    if old and name in old_entries and path.is_file() and digest(path.read_bytes())==old_entries[name]['utf8_sha256']:
        excerpt=path.read_bytes();end=old['pg19_excerpt_byte_end']
        pg_generation=old['pg19_object_generation']
        pg_full_size=old['pg19_full_object_size']
        pg_full_sha=old['pg19_full_object_sha256']
        source_url=old_entries[name]['source_url']
    else:
        meta=json.loads(get(meta_url))
        if meta['name']!=PG19_OBJECT:
            raise AssertionError('PG19 object identity')
        source_url=f'https://storage.googleapis.com/deepmind-gutenberg/{PG19_OBJECT}?generation={meta["generation"]}'
        full=get(source_url)
        if len(full)!=int(meta['size']):
            raise AssertionError('PG19 object size')
        end=PG19_PREFIX_BYTES
        while True:
            try:
                excerpt=full[:end].decode('utf-8').encode('utf-8')
                break
            except UnicodeDecodeError as e:
                end=e.start
        if end<PG19_PREFIX_BYTES-4:
            raise AssertionError('unexpected PG19 UTF8 boundary')
        path.write_bytes(excerpt)
        pg_generation=meta['generation'];pg_full_size=int(meta['size']);pg_full_sha=digest(full)
    entries.append(dict(source_text_id=name,role='LONG_CONTEXT_HOLDOUT_INPUT',source='PG-19',
                        dataset_repository='google-deepmind/pg19',observed_dataset_revision='GCS_OBJECT_GENERATION_'+str(pg_generation),
                        revision_association='GCS_GENERATION_AND_FROZEN_BYTES',split='validation',
                        row_start=PG19_OBJECT,row_end_inclusive=f'UTF8_byte_prefix_{end}',
                        source_url=source_url,relative_path=str(path.relative_to(out)).replace('\\','/'),
                        byte_count=len(excerpt),utf8_sha256=digest(excerpt),
                        selection_rule='fixed validation/11155.txt;first 200000 bytes trimmed only to UTF8 boundary;no result-based excerpt choice'))
    result=dict(schema='C16_INPUT_SOURCE_FREEZE_V1',wikitext_repository_revision_observed=WIKITEXT_REVISION,
                wikitext_viewer_revision_pinning='UNSUPPORTED_BY_ROWS_API',
                pg19_object_generation=pg_generation,pg19_full_object_size=pg_full_size,
                pg19_full_object_sha256=pg_full_sha,pg19_excerpt_byte_end=end,
                entries=entries,tokenizer_executed=False,model_executed=False,
                tokenization_receipt='FUTURE_AFTER_PINNED_TOKENIZER_LOAD')
    dump(out/'INPUT_SOURCE_FREEZE.json',result)
    print(f'frozen {len(entries)} public natural input byte streams; no tokenization')
    return result


def main() -> None:
    p=argparse.ArgumentParser()
    p.add_argument('--out',type=Path,required=True)
    args=p.parse_args()
    build(args.out)


if __name__=='__main__':
    main()
