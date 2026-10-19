"""PREPARED_NOT_TESTED host references; never a trace/value oracle.

Source recipes: PolyBench/GPU 5584aaa7 BICG/GEMM and source-backed
MatrixMarket/Parboil SpMV. No I/O, allocation of full new inputs, GPU or
simulator startup occurs on import. Full-size native outputs do not exist
for N1/N2. Capture/native comparison must retain source tolerances and the
actual compiler's FP32/FMA behavior.
"""
import struct


def f32(value):
    return struct.unpack("f", struct.pack("f", value))[0]


def bicg_reference(a, r, p):
    """s=A^T*r and q=A*p, per-output ascending reduction, rounded FP32."""
    nx, ny = len(a), len(p)
    assert len(r) == nx and all(len(row) == ny for row in a)
    s, q = [0.0] * ny, [0.0] * nx
    for i in range(nx):
        for j in range(ny):
            s[j] = f32(s[j] + f32(f32(r[i]) * f32(a[i][j])))
            q[i] = f32(q[i] + f32(f32(a[i][j]) * f32(p[j])))
    return s, q


def gemm_reference(a, b, c, alpha=32412.0, beta=2123.0):
    """The pinned naive GEMM's ascending-k FP32 reference operation order."""
    ni, nk, nj = len(a), len(b), len(c[0])
    assert len(c) == ni and all(len(row) == nk for row in a)
    assert all(len(row) == nj for row in b + c)
    result = []
    for i in range(ni):
        row = []
        for j in range(nj):
            acc = f32(f32(c[i][j]) * f32(beta))
            for k in range(nk):
                product = f32(f32(alpha) * f32(a[i][k]))
                product = f32(product * f32(b[k][j]))
                acc = f32(acc + product)
            row.append(acc)
        result.append(row)
    return result


def spmv_coordinate_reference(rows, columns, triples, x):
    """Independent mathematical reference, not the JDS implementation.

    Caller must parse the fixed MatrixMarket symmetry/duplicate semantics
    and supply ordered zero-based coordinates, compare against the existing
    native reference, and qualify JDS row permutation independently.
    """
    assert len(x) == columns
    output = [0.0] * rows
    for row, column, value in triples:
        assert 0 <= row < rows and 0 <= column < columns
        output[row] = f32(output[row] + f32(f32(value) * f32(x[column])))
    return output
