# Local typesetting provenance

Actual tool: pdfTeX 3.141592653-2.6-1.40.22 (TeX Live2021/Debian), IEEEtran conference Letter, newtx fonts, PGF/TikZ. Temporary runtime-only macro/font files came from CTAN; exact URLs/archive SHA-256/bytes are recorded in validation/TEX_DEPENDENCIES.json. No archives/fonts or copyrighted papers are vendored, no system install/global font map edit, no production C++ compiler. Runtime footprint is in TYPESETTING_RESOURCE.json.

The local dependency tree can be supplied as `<deps>`; source parent is `<paper>`, scratch working directory is `<render>`. Preserve runtime hierarchy and create this wrapper in the fresh scratch directory:

```tex
\pdfmapfile{+newtx.map}
\input{<paper>/EP_L2_EN_v3.tex}
```

Set task-local environment only: TEXINPUTS=`<deps>//:<paper>//:`, and TFMFONTS, VFFONTS, T1FONTS, ENCFONTS, TEXFONTMAPS each `<deps>//:`. From `<render>`, invoke twice:

```sh
timeout 45 nice -n 10 pdflatex -interaction=nonstopmode -halt-on-error -no-shell-escape -no-mktex=pk -no-mktex=tfm -jobname=EP_L2_EN_v3 build.tex
```

The successful final two passes are pass5/pass6 in task scratch. Earlier attempts exposed missing local packages and produced no usable PDF; dependencies were resolved in the temporary tree. Final log is preserved, warnings0/undefined0/overfull0. Cross-reference resolution requires the second successful pass. PDF timestamps may differ on another render; source and current delivered PDF each have independent hashes.

Verification used pdfinfo, pdffonts, pdftotext and pdftoppm; all five pages viewed in a contact sheet, enlarged page2 checked for architecture labels/routing. See LAYOUT_VALIDATION.json, PDF_INFO.txt and PDF_FONTS.txt. The diagram remains editable TikZ in the paper source. Tables/plots awaiting acceptance are intentionally not synthesized.
