#!/usr/bin/env python3
"""Validate the C16 frozen Llama S0/B1/T128/Decode4/TEXT binding without tokenizer use."""
import argparse, hashlib, json, sys
from pathlib import Path

FOUR = {
    "raw": "bae0b908106146659663fa04f44bc03ec0da18cadb08c9ec357c140afc4d8208",
    "token_receipt": "0b5a86fdee44452e74e5d80e8043ebd97054fbbe29a6232a4f5cf5d06568c7dd",
    "target_ids": "f9cf1ea6dca7956c740b3aa0af59acadd17be014df2aaffb75d240383502e3a7",
    "derived": "fc712eb0a158f0fe62231f7826feec3eaabfea51906ca6b1588a55ee81ae3624",
}

def sha(p: Path):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda:f.read(1048576),b""): h.update(b)
    return h.hexdigest()

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--root",type=Path,required=True); ap.add_argument("--output",type=Path,required=True); a=ap.parse_args()
    if a.output.exists(): raise SystemExit("refusing overwrite")
    r=json.loads((a.root/"C16_FIND_AND_TRANSFER_LLAMA_S5_FROZEN_INPUT_BINDING_RECEIPT.json").read_text())
    errors=[]; inv=[]
    ident=r.get("identity",{})
    if (ident.get("scenario_id"),ident.get("batch_size"),ident.get("prefill_tokens"),ident.get("decode_tokens"),ident.get("input_class")) != ("S0",1,128,4,"TEXT"): errors.append("semantic identity mismatch")
    if (ident.get("model_id"),ident.get("model_revision")) != ("meta-llama/Llama-3.2-1B","4e20de362430cd3b72f300e6b0f18e50e7166e08"): errors.append("model identity mismatch")
    for e in r.get("transfer_inventory",[]):
        p=a.root/e["filename"]; actual={"filename":e["filename"],"exists":p.is_file()}
        if p.is_file(): actual.update(size=p.stat().st_size,sha256=sha(p))
        inv.append(actual)
        if not p.is_file() or actual.get("size")!=e["destination_size_bytes"] or actual.get("sha256")!=e["destination_sha256"] or not e.get("size_equal") or not e.get("sha256_equal"): errors.append("transfer inventory mismatch: "+e["filename"])
    binding=json.loads((a.root/"LLAMA_S0_TEXT_BINDING_RECEIPT.json").read_text())
    token=json.loads((a.root/"TEXT_T128.json").read_text())
    derived=json.loads((a.root/"LLAMA_S0_TEXT_TOKEN_IDS.json").read_text())
    if sha(a.root/"TEXT.txt")!=FOUR["raw"] or sha(a.root/"TEXT_T128.json")!=FOUR["token_receipt"] or sha(a.root/"LLAMA_S0_TEXT_TOKEN_IDS.json")!=FOUR["derived"]: errors.append("three payload hashes mismatch")
    ids=token.get("target_token_ids"); compact=json.dumps(ids,separators=(",",":"),ensure_ascii=False).encode(); canonical=hashlib.sha256(compact).hexdigest()
    if not isinstance(ids,list) or len(ids)!=128 or canonical!=FOUR["target_ids"]: errors.append("canonical target_token_ids mismatch")
    if derived!=ids: errors.append("derived token IDs differ from authoritative target IDs")
    bi=binding.get("input",{})
    if (bi.get("raw_input_sha256"),bi.get("token_receipt_sha256"),bi.get("target_token_ids_sha256"),bi.get("derived_token_ids_sha256")) != tuple(FOUR.values()): errors.append("binding four-hash mismatch")
    result={"status":"FROZEN_INPUT_ADMISSION_PASS" if not errors else "FROZEN_INPUT_ADMISSION_FAIL","errors":errors,"identity":ident,"inventory":inv,"canonical_target_token_ids_sha256":canonical,"target_id_count":len(ids) if isinstance(ids,list) else None,"tokenizer_invoked":False}
    a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n"); print(result["status"]); return 0 if not errors else 1
if __name__=="__main__": sys.exit(main())
