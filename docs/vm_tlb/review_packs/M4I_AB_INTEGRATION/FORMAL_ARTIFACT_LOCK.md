# M4I formal artifact lock

Status: `PASS` — immutable sources verified; selective compressed-trace stage
created at `/workspace/vm-m4b-stage-f96b7ea9-5bdd4b55`.

| ROI | immutable archive | SHA256 | archive integrity | staged `.traceg.xz` files |
| --- | --- | --- | --- | ---: |
| prefill | `/workspace/m4a-rented-host-pilot/formal-prefill/m4a-llama-prefill-20260902T182016Z.tar.zst` | `f96b7ea91b798e2ce8eb8f4592b1ef6512a762870471d2dbb85ab4777c97f181` | `zstd -t` PASS | 724 |
| decode1 | `/workspace/m4a-rented-host-pilot/formal-decode1/m4a-llama-decode1-20260903T004138Z.tar.zst` | `5bdd4b55ed0e1499cbfee756d289cbd8072f556db4f467a882a54e42cd32dcad` | `zstd -t` PASS | 772 |

Both archives were tar-listed without mutation.  Each selected staged file was
checked against the archive's internal `SHA256SUMS`: 732 prefill and 780 decode1
entries passed.  The archive-level SHA256 binds the remaining un-staged capture
provenance files and unused `.trace.xz` siblings; the replay stage deliberately
uses only the required compressed `.traceg.xz` inputs plus manifests/lists.

## Semantic derivatives

The externally retained, reproducible Track-B derivatives were copied read-only
from `/workspace/m4a-merge-prep/` and rehashed:

| ROI | semantic full | compute-only | NCCL-only |
| --- | --- | --- | --- |
| prefill | `ee53ca249cd45e2fd4da6920db4038673636960d6f36f2f99789062412636908` | `a40d6832219e5b0a6232875bb181754ac121bb5f867c9b13c84370e2a2cb6e6f` | `9c899cd5312a8854e027db4c3415b934dfc0e9fd5e4a68c3d79a21055e978111` |
| decode1 | `9bb152d8475f7827e58071a7f765b2b00c5a2d08161a306f9031ff00a8f48701` | `b6c42eb1932fcacefc2429b91a2015d38003a764a5319fe4bcbaf65b3d0cd0dc` | `c642daa4902c4d686e77934f2c9416a883ae170ccf5d18e67f86d6871ca84657` |

The raw lists contain 724/772 entries; the compute-only lists contain 692/740
and the NCCL-only lists contain 32/32, conserving each ROI exactly.  Capture
Framework source is `c79f4469c6a2befa59e4c4efcd3c885dc2259a81`; model/revision
is `meta-llama/Llama-3.2-1B@4e20de362430cd3b72f300e6b0f18e50e7166e08`.

No accepted archive was edited, repacked, renamed, or placed in Git.
