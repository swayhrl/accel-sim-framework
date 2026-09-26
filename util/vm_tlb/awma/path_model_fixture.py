#!/usr/bin/env python3
"""Executable timing/correctness contracts for diagnostic access paths.

This is not simulator mechanism code.  It fixes the conservative timing
composition used to interpret an already accepted 0/80 diagnostic as the
minimum VIPT-like overlap for the frozen 10-cycle TLB and 32-cycle L1D path.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Operation(str, Enum):
    LOAD = "LOAD"
    STORE = "STORE"
    ATOMIC = "ATOMIC"


@dataclass(frozen=True)
class AccessCase:
    tlb_hit: bool
    l1d_hit: bool
    operation: Operation = Operation.LOAD
    l1_tlb_latency: int = 10
    miss_translation_tail: int = 80
    l1d_latency: int = 32

    @property
    def physical_translation_latency(self) -> int:
        return self.l1_tlb_latency + (0 if self.tlb_hit else self.miss_translation_tail)


@dataclass(frozen=True)
class PathOutcome:
    completion_cycle: int | None
    lower_physical_issue_cycle: int | None
    translation_services: int
    data_requests: int
    translation_required: bool


def current_sequential(case: AccessCase) -> PathOutcome:
    translation_done = case.physical_translation_latency
    l1d_done = translation_done + case.l1d_latency
    return PathOutcome(
        completion_cycle=l1d_done if case.l1d_hit else None,
        lower_physical_issue_cycle=None if case.l1d_hit else l1d_done,
        translation_services=1,
        data_requests=1,
        translation_required=True,
    )


def vipt_like_minimum_overlap(case: AccessCase) -> PathOutcome:
    """Conservative overlap: credit only the initial L1-TLB lookup interval.

    The existing L1D operation remains after the effective translation path;
    therefore this does not model early tag use or hide an L2/PTW tail.  With
    the frozen 32-cycle L1D and 10-cycle L1 TLB, the effective L1-TLB latency
    is zero, exactly matching the accepted reference 0/80 diagnostic.
    """

    overlap = min(case.l1_tlb_latency, case.l1d_latency)
    effective_translation_done = case.physical_translation_latency - overlap
    l1d_done = effective_translation_done + case.l1d_latency
    # Even though the timing model credits overlap, no hit completion or lower
    # physical request may precede the unmodified translation's legal result.
    assert l1d_done >= case.physical_translation_latency
    return PathOutcome(
        completion_cycle=l1d_done if case.l1d_hit else None,
        lower_physical_issue_cycle=None if case.l1d_hit else l1d_done,
        translation_services=1,
        data_requests=1,
        translation_required=True,
    )


def virtual_l1_filter_bound(
    case: AccessCase, *, cached_permission_valid: bool
) -> PathOutcome:
    """Logical B2 bound, deliberately not an integrated simulator path.

    Only a load that is fully served by an assumed virtual L1 with cached
    permissions may avoid translation. Stores/atomics and every L1D miss fall
    back to the normal translated path. The real source lacks virtual tags,
    permission state, synonym handling, and virtual-cache coherence, so this
    function is a correctness contract rather than authorization to run B2.
    """

    filterable = (
        case.operation == Operation.LOAD
        and case.l1d_hit
        and cached_permission_valid
    )
    if filterable:
        return PathOutcome(
            completion_cycle=case.l1d_latency,
            lower_physical_issue_cycle=None,
            translation_services=0,
            data_requests=1,
            translation_required=False,
        )
    return current_sequential(case)


class ExactlyOnceApplication:
    def __init__(self) -> None:
        self.applied = False
        self.applications = 0

    def apply(self) -> bool:
        if self.applied:
            return False
        self.applied = True
        self.applications += 1
        return True
