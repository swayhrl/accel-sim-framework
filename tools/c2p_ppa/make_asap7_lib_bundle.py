#!/usr/bin/env python3
"""Build one Liberty file from ASAP7's split same-PVT cell libraries."""

import gzip
import pathlib
import sys


def split_library(text: str, source: pathlib.Path) -> tuple[str, str]:
    start = text.find("library (")
    if start < 0:
        raise ValueError(f"{source}: no Liberty library declaration")
    brace = text.find("{", start)
    end = text.rfind("}")
    if brace < 0 or end <= brace:
        raise ValueError(f"{source}: malformed Liberty library block")
    return text[start : brace + 1], text[brace + 1 : end]


def read_liberty(path: pathlib.Path) -> str:
    if path.suffix == ".gz":
        with gzip.open(path, "rt") as source:
            return source.read()
    return path.read_text()


def main() -> None:
    if len(sys.argv) < 3:
        raise SystemExit(f"usage: {sys.argv[0]} OUTPUT.lib INPUT.lib [...]")

    output = pathlib.Path(sys.argv[1])
    inputs = [pathlib.Path(arg) for arg in sys.argv[2:]]
    parts = [split_library(read_liberty(path), path) for path in inputs]

    # Every input is a different cell-family view at one PVT.  Keep the full
    # common header of the first library; subsequent bodies contain only
    # duplicate common templates plus cells, and Liberty accepts them inside
    # the same library scope.
    header, first_body = parts[0]
    bodies = [first_body] + [body for _, body in parts[1:]]
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(header + "\n" + "\n".join(bodies) + "\n}\n")


if __name__ == "__main__":
    main()
