# C16 Lane G CPython 3.10 wheelhouse closure

The C16-0.3 wheelhouse is an actual local collection of Linux x86_64 CPython
3.10 wheels, not a logical package list.  `WHEELHOUSE_MANIFEST.tsv` is derived
from each wheel's embedded distribution metadata and records its filename,
distribution/version, byte size, SHA256, source, and compatibility tag.  The
external wheel directory is deliberately not committed; its manifest is the
transfer contract.

The prior root lock was not installable: PyPI has no `autoawq==0.2.8` release.
The available fixed release `autoawq==0.2.7.post3` requires
`huggingface-hub>=0.26.5`, so the unified exact roots use
`autoawq==0.2.7.post3` and `huggingface-hub==0.26.5`.  They are resolved and
installed together with the PyTorch CUDA 12.4 wheel and all transitive Python
dependencies using `pip --no-index --find-links` in a clean CPython 3.10 venv.

The verification receipt performs a resolver dry-run, offline installation,
`pip check`, and Python imports.  `pip==26.1` is itself included in the
wheelhouse so a fresh CPython 3.10 venv can first upgrade its installer
offline and support `pip install --dry-run`. It does not launch a CUDA kernel and cannot
establish rented-GPU runtime compatibility.  That remaining gate is explicitly
`GPU_RUNTIME_VERIFY_REQUIRED` and belongs to inline C16-1 qualification after
both A's fixed GPU asset package and user-provided AutoDL SSH are available.
