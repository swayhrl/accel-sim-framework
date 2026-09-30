# R17 GloVe-100 input authority

Date: 2026-09-30. Source authority only; no large payload was downloaded.

State: `PUBLIC_INPUT_SOURCE_QUALIFIED_LOCAL_RECEIPT_PENDING`.

## Upstream authority

Pinned ANN-Benchmarks source:
`erikbern/ann-benchmarks@2e081ad32c1eccab72dcb739ad886c310b90f715`.

Its `glove(out_fn,100)` path downloads Stanford `glove.twitter.27B.zip`, selects the 100-dimensional vectors, performs a deterministic train/test split with test_size=10000 and random_state=1, then writes an angular-distance ANN dataset with ground truth.

The pinned README records:
- dimension 100;
- base/train vectors 1,183,514;
- queries 10,000;
- ground-truth neighbors/query 100;
- distance Angular;
- published HDF5 about 463 MB.

This is a real learned NLP-embedding ANN workload. It is not a natural online RAG request trace.

## Stable cuVS preparation path

Pinned cuVS source:
`v26.08.01@25b1be43a8c127e5ab6d2f29f20c62dbfd3351ab`.

The stable dataset helper downloads `glove-100-angular.hdf5`. Its converter requires FP32 train/test, INT32 neighbor IDs and FP32 distances. With `--normalize`, angular base/query vectors are row-normalized; the helper then stores the prepared representation under the corresponding `glove-100-inner` directory.

Future receipts must not mix:
- raw angular HDF5 identity,
- unnormalized vectors,
- normalized `glove-100-inner` prepared identity.

Proposed stable execution representation is therefore: public angular HDF5 -> stable helper with `--normalize` -> normalized FP32 base/query + inherited ground-truth IDs. For R17, k=10 can be evaluated against the published top-100 ground truth.

## Still pending locally

Before any scientific Native timing:
- HDF5 SHA256/byte size;
- prepared base/query/ground-truth hashes, shapes and dtypes;
- finite/unit-normalization check;
- exact preparation command and package version;
- durable node164 location and any node109 replica identity;
- dataset terms/redistribution note.

The unattended lane did not download the payload. No synthetic or SIFT input may replace it for the scientific result.
