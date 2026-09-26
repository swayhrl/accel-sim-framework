# Compact normalization

Raw `REQUEST_SELECTION.tsv` retains exact multiline dataset text, including source trailing spaces. The Git review copy JSON-escapes `raw_prompt` and `rendered_prompt` only; decoding yields the exact original strings. Dataset receipt hashes bind the raw authority.
