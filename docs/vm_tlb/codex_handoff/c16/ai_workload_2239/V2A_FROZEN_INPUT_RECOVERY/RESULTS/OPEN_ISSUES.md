# V2A open issues

1. `HISTORICAL_FROZEN_INPUT_NOT_RECOVERED`: three byte-exact payloads are
   present, but the exact five-file historical bundle is incomplete.  The two
   required binding receipts and the required `LLAMA_S0_TEXT_TOKEN_IDS.json`
   member under that historical filename were not located in the bounded source
   roots.
2. `c16_frozen_input_admission.py` remains fail-closed: its transfer-binding
   receipt requirement prevents a valid PASS.  Do not create a replacement,
   rename a nearby receipt, or invoke a tokenizer to fill the gap.
3. RTX4080 R5 U5/U6/U9 raw/static-map/stdout remains
   `UNKNOWN_PROVENANCE`: only a status summary was found, not a path+SHA
   receipt/manifest.
4. N1 and U8 have receipt-bound locators, but `/data/c16` is not mounted in
   this source container.  This is a visibility limitation, not proof of loss
   or transfer; no large artifact was copied.

No issue permits reinterpreting RTX3090 or RTX4080 authority, running a
workload, or publishing an incomplete frozen-input bundle.
