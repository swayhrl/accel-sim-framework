"""Decode known installed bytecode without executing it; compare exact 3.10 source compile."""
import hashlib
import importlib.util
import json
import marshal
from pathlib import Path
import sys
import types


def norm(code):
    # pip rewrites co_filename when compiling wheel bytecode at its installation path.
    attrs = ['co_argcount', 'co_posonlyargcount', 'co_kwonlyargcount', 'co_nlocals',
             'co_stacksize', 'co_flags', 'co_code', 'co_names', 'co_varnames',
             'co_freevars', 'co_cellvars', 'co_firstlineno', 'co_linetable']
    values = tuple(getattr(code, n) for n in attrs)
    return values + (tuple(norm(x) if isinstance(x, types.CodeType) else x
                           for x in code.co_consts),)


def main():
    request = Path(sys.argv[1])
    rows = []
    for name in json.loads(request.read_text()):
        p = Path(name)
        source = Path(importlib.util.source_from_cache(str(p)))
        content = p.read_bytes()
        assert content[:4] == importlib.util.MAGIC_NUMBER
        cached = marshal.loads(content[16:])
        compiled = compile(source.read_bytes(), cached.co_filename, 'exec', dont_inherit=True, optimize=0)
        assert norm(cached) == norm(compiled), 'BYTECODE_NOT_SAME_ACCEPTED_SOURCE ' + str(p)
        rows.append({'pyc': str(p), 'source': str(source),
                     'pyc_sha256': hashlib.sha256(content).hexdigest(),
                     'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                     'status': 'PASS_EXACT_SOURCE_CODEOBJECT_EXCEPT_FILENAME_AND_HEADER',
                     'code_executed': False})
    print(json.dumps({'status': 'PASS', 'Python': sys.version, 'records': rows}))


if __name__ == '__main__':
    main()
