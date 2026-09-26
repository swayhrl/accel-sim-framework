#!/usr/bin/env python3
"""Small executable contracts for post-coalescing research hypotheses.

This is not an Accel-Sim mechanism.  It fixes the online-only decisions that a
later prototype would be required to preserve, so directed tests can reject
future-information, unbounded-resource, and duplicate-selection shortcuts.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional


@dataclass(frozen=True)
class TranslationGroup:
    instruction: str
    group: str
    request_order: int
    is_head: bool
    ready: bool
    baseline_eligible: bool = True


def is_last_unresolved_head_group(
    candidate: TranslationGroup, groups: Iterable[TranslationGroup]
) -> bool:
    """Return the H1 priority predicate using only current group state.

    A single-page instruction is deliberately not called a last-group
    opportunity: it has no within-instruction alternative and is ordinary
    demand translation rather than the residual multi-page question.
    """

    same_instruction = [g for g in groups if g.instruction == candidate.instruction]
    if len(same_instruction) < 2:
        return False
    if not candidate.is_head or candidate.ready or not candidate.baseline_eligible:
        return False
    return all(g.group == candidate.group or g.ready for g in same_instruction)


@dataclass(frozen=True)
class PortRequest:
    request: str
    arrival_order: int
    baseline_eligible: bool
    head_demand: bool
    resident_prelaunch: bool


def choose_demand_before_prelaunch(
    requests: Iterable[PortRequest], slots: int = 1
) -> list[str]:
    """Fixed H2 arbitration: head demand first, prelaunch only in idle slots.

    The function never manufactures requests, changes eligibility, looks at a
    completion time, or provides more than ``slots`` grants.
    """

    if slots < 0:
        raise ValueError("slots must be non-negative")
    eligible = [r for r in requests if r.baseline_eligible]
    eligible.sort(
        key=lambda r: (
            0 if r.head_demand else 1,
            0 if not r.resident_prelaunch else 1,
            r.arrival_order,
            r.request,
        )
    )
    return [r.request for r in eligible[:slots]]


@dataclass(frozen=True)
class AccessTimeline:
    request_ready: int
    translation_ready: int
    address_applied: int
    cache_admitted: int

    def validate(self) -> None:
        values = (
            self.request_ready,
            self.translation_ready,
            self.address_applied,
            self.cache_admitted,
        )
        if any(v < 0 for v in values):
            raise ValueError("cycles must be non-negative")
        if list(values) != sorted(values):
            raise ValueError("event order must be monotonic")

    def translation_wait(self) -> int:
        self.validate()
        return self.translation_ready - self.request_ready

    def ready_to_apply(self) -> int:
        self.validate()
        return self.address_applied - self.translation_ready

    def apply_to_admission(self) -> int:
        self.validate()
        return self.cache_admitted - self.address_applied


def classify_residual(timeline: AccessTimeline) -> str:
    """Separate translation wait from already-translated downstream delay."""

    if timeline.translation_wait() > 0:
        return "TRANSLATION_WAIT_PRESENT"
    if timeline.ready_to_apply() > 0:
        return "READY_RESULT_CONSUMPTION_DELAY"
    if timeline.apply_to_admission() > 0:
        return "POST_TRANSLATION_ADMISSION_DELAY"
    return "NO_RESIDUAL_DELAY"
