#!/usr/bin/env python3
import inspect, json
import importlib.metadata
import xgrammar as xgr
from transformers import AutoTokenizer, AutoConfig
from pathlib import Path

model=Path('/data/c16/models/.incoming/qwen2p5_0p5b_instruct/7ae557604adf67be50417f59c2c2f167def9a775')
tok=AutoTokenizer.from_pretrained(model,local_files_only=True)
cfg=AutoConfig.from_pretrained(model,local_files_only=True)
print('xgrammar',importlib.metadata.version('xgrammar'))
print('tokenizer_len',len(tok),'tokenizer_vocab_size',tok.vocab_size,'config_vocab_size',cfg.vocab_size)
for name in ['TokenizerInfo','GrammarCompiler','GrammarMatcher','allocate_token_bitmask','apply_token_bitmask_inplace','BatchGrammarMatcher']:
    obj=getattr(xgr,name,None)
    print(name,'exists',obj is not None,'signature',inspect.signature(obj) if obj is not None else 'NA')
for name in ['from_huggingface','compile_json_schema','fill_next_token_bitmask','accept_token','is_terminated','is_completed']:
    for holder in [xgr.TokenizerInfo,xgr.GrammarCompiler,xgr.GrammarMatcher]:
        if hasattr(holder,name):
            obj=getattr(holder,name)
            print(holder.__name__,name,inspect.signature(obj))
