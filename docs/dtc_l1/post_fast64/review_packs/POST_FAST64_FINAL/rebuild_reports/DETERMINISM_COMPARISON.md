# Isolated deterministic rebuild comparison

Status: **PASS**

E2.3 ran the canonical build twice with the same committed compact inputs and two isolated output directories:

```text
/tmp/post-fast64-lane-e-rebuild-a
/tmp/post-fast64-lane-e-rebuild-b
```

`diff -qr` was empty across the complete package, including TSV/Markdown, SVG, PNG, deterministic PDF, compact input snapshots, and manifests. The canonical review-pack build was then compared against rebuild A with the same empty result. The PDF exporter intentionally avoids timestamp metadata; the SVG assets are deterministic vector figures.
