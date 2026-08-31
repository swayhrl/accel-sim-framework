#!/usr/bin/env python3
"""Permanent deterministic EPL2SRV1 classification and distance fixtures."""
from collections import deque

BINS = (8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096)

def bucket(distance):
    for index, high in enumerate(BINS):
        if distance <= high:
            return index
    return 10

class SectorReuse:
    def __init__(self):
        self.reset()
    def reset(self):
        self.touches, self.lines, self.stack = {}, set(), deque()
        self.a = self.b = self.c = self.unique = self.reused = self.wb = 0
        self.hist = [0] * 11
    def ref(self, block, bits, writeback=False):
        if writeback:
            self.wb += 1
            return
        sectors = [(block, bit) for bit in bits]
        old_line = block in self.lines
        old = {sector: self.touches.get(sector, 0) for sector in sectors}
        distances = {sector: (self.stack.index(sector) if sector in self.stack else 4097)
                     for sector, touched in old.items() if touched}
        for sector, touched in old.items():
            if touched:
                self.c += 1
                if touched == 1:
                    self.reused += 1
                self.touches[sector] += 1
                self.hist[bucket(distances[sector])] += 1
            else:
                self.touches[sector] = 1
                self.unique += 1
                if old_line:
                    self.b += 1
                else:
                    self.a += 1
        for sector in sectors:
            if sector in self.stack:
                self.stack.remove(sector)
        for sector in sectors:
            self.stack.appendleft(sector)
        while len(self.stack) > 4097:
            self.stack.pop()
        self.lines.add(block)
    def check(self):
        assert self.a + self.b + self.c == sum(self.touches.values())
        assert self.reused + (self.unique - self.reused) == self.unique
        assert sum(self.hist) == self.c

# New line, spatial-only continuation, immediate temporal reuse and a revisit.
r = SectorReuse(); r.ref(0, [0]); assert (r.a, r.b, r.c) == (1, 0, 0)
r.ref(0, [1]); r.ref(0, [2]); r.ref(0, [3]); assert (r.a, r.b, r.c) == (1, 3, 0)
r.ref(0, [0]); r.ref(0, [2]); assert r.c == 2 and r.hist[0] == 2; r.check()

# An unseen multi-sector request classifies every bit against pre-request state.
r = SectorReuse(); r.ref(3, [0, 1, 2, 3]); assert (r.a, r.b, r.c) == (4, 0, 0)
r.ref(3, [1, 2]); r.ref(3, [0, 3]); assert (r.a, r.b, r.c) == (4, 0, 4); r.check()
r = SectorReuse(); r.ref(4, [0]); r.ref(4, [0, 1]); assert (r.a, r.b, r.c) == (1, 1, 1); r.check()

# Epoch reset, independent slices, write demand and excluded writeback traffic.
r.reset(); r.ref(7, [0]); assert r.c == 0 and r.a == 1
x, y = SectorReuse(), SectorReuse(); x.ref(9, [0]); y.ref(9, [0]); x.ref(9, [0]); assert x.c == 1 and y.c == 0
r = SectorReuse(); r.ref(10, [1]); r.ref(10, [1]); r.ref(10, [2], writeback=True); assert r.c == 1 and r.wb == 1; r.check()

def distance_case(distance):
    r = SectorReuse(); r.ref(0, [0])
    for item in range(1, distance + 1):
        r.ref(item, [0])
    r.ref(0, [0]); return r.hist

for distance, expected in ((0, 0), (8, 0), (9, 1), (16, 1), (17, 2),
                           (32, 2), (33, 3), (64, 3), (65, 4), (128, 4),
                           (129, 5), (256, 5), (257, 6), (512, 6),
                           (513, 7), (1024, 7), (1025, 8), (2048, 8),
                           (2049, 9), (4096, 9), (4097, 10)):
    histogram = distance_case(distance)
    assert histogram[expected] == 1 and sum(histogram) == 1, (distance, histogram)
print("EPL2SRV1 directed contract: PASS")
