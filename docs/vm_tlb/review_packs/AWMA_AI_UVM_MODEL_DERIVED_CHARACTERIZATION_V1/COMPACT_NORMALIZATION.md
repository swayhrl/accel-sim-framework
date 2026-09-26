# Compact-copy normalization

The node164 raw TSV authorities retain their original Python `csv.writer` CRLF bytes and are identified by `RAW_DATA_INDEX.tsv`. Git review-pack TSV copies are byte-normalized from CRLF to LF only; field content is unchanged. `SHA256SUMS` in this directory binds the normalized compact copies, while the durable raw directory's `SHA256SUMS` binds raw bytes.
