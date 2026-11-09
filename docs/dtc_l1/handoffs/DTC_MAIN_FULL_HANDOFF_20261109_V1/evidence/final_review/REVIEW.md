PASS: fixed32 x4 modes, 128 UUIDs, 96 matched Oracle/OFF pairs.

Each raw log was read and SHA-checked; pure frozen population/lifecycle and Oracle checks were executed again. Each true164 archive chunk and the complete archive stream were hashed again. Source and native restored trees were checked for all manifest paths, types, permissions, owner, SHA and symlink targets.

Full trace-body SHA receipts and capture provenance are referenced, not newly certified. Current trace member sizes/mtime/readability and commandlist SHA were checked. Prior strict/archive PASS labels were not treated as independent acceptance.

{
  "M_DATAREAD": {
    "fixed_inputs": 32,
    "matched_pairs": 32,
    "GM_S": 1.6767585258096842,
    "GM_implied_H": 0.40361120304003617,
    "positive": 32,
    "zero": 0,
    "negative": 0,
    "missing": 0,
    "minimum_S": 1.000037907580382,
    "maximum_S": 10.288070318538344
  },
  "L2_DATAREAD": {
    "fixed_inputs": 32,
    "matched_pairs": 32,
    "GM_S": 1.2806486845080634,
    "GM_implied_H": 0.2191457250556339,
    "positive": 19,
    "zero": 11,
    "negative": 2,
    "missing": 0,
    "minimum_S": 0.9980035598549842,
    "maximum_S": 4.132224010294569
  },
  "L1_DATAREADY": {
    "fixed_inputs": 32,
    "matched_pairs": 32,
    "GM_S": 1.9399115770053144,
    "GM_implied_H": 0.4845125871439343,
    "positive": 32,
    "zero": 0,
    "negative": 0,
    "missing": 0,
    "minimum_S": 1.000037907580382,
    "maximum_S": 35.85115131414243
  }
}

No unresolved scientific HOLD within controlled declared-trace scope. Entire Goal completion is for Main. Historical engineering failures and original data remain untouched. First audit parser compatibility errors are retained in ROW_AUDIT_INTERMEDIATE.json.
