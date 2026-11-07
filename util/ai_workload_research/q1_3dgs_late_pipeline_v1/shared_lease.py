"""Same-claimant reservation renewal under one already-held campaign flock.

No server, flock acquisition, CUDA or NVML operation is implemented here.
The deployed endpoint has no compare-and-swap; pre/post attestation detects
observed changes but cannot exclude a concurrent authorized administrator write.
"""
import math
import os
import time
from shared_gate import SharedClient, same, kernel_holders

RENEW_TTL_SECONDS = 1800
RENEW_BEFORE_SECONDS = 600


class RenewingSharedClient(SharedClient):
    def __init__(self, cfg):
        super().__init__(cfg)
        ttl = self.s.get("reservation_ttl_seconds")
        if type(ttl) is not int or ttl != RENEW_TTL_SECONDS:
            raise ValueError("LEASE_TTL_MUST_EQUAL_ORIGINAL_1800")
        self.expires_unix = None
        self.lease_events = []
        self._renewal_uncertain = False
        self._reservation_attempted = False

    def _event(self, kind, **values):
        event = dict(kind=kind, unix=time.time(), **values)
        self.lease_events.append(event)
        return event

    def _expiry(self, reservation, now):
        value = reservation.get("expires_unix")
        if (isinstance(value, bool) or not isinstance(value, (int, float))
                or not math.isfinite(value) or value <= now):
            raise RuntimeError("LEASE_EXPIRY_INVALID_OR_EXPIRED")
        return float(value)

    def _same_claimant(self, reservation):
        return (isinstance(reservation, dict)
                and same(reservation.get("owner") or {}, self.claimant)
                and reservation.get("pause_new_work") is True)

    def _verify_held(self, value, request_id):
        reservation = value.get("reservation") or {}
        if (not self._same_claimant(reservation)
                or reservation.get("request_id") != request_id):
            raise RuntimeError("LEASE_CLAIMANT_OR_REQUEST_CHANGED")
        if kernel_holders(self.cfg["lock"]) != [os.getpid()]:
            raise RuntimeError("LEASE_FLOCK_OWNER_CHANGED")
        if value.get("state") != "GPU_RESERVED_FOR_AI_ARCH":
            raise RuntimeError("LEASE_RESERVED_STATE_CHANGED")
        holders = value.get("kernel_holders") or []
        if (not holders or any(not same(h.get("identity") or {}, self.claimant)
                               for h in holders)):
            raise RuntimeError("LEASE_SERVER_HOLDER_CHANGED")
        fingerprint = (value["completed_scopes"],
                       value["last_quiescence"]["finished_unix"])
        if self.baseline is not None and fingerprint != self.baseline:
            raise RuntimeError("LEASE_IMAGE_LAB_EXECUTION_CHANGED")
        self._expiry(reservation, time.time())
        return reservation

    def reserve(self):
        # Original reserve semantics and API remain unchanged.
        self._reservation_attempted = True
        try:
            result = super().reserve()
            self.expires_unix = self._expiry(result, time.time())
            self._event("RESERVED", request_id=self.request_id,
                        expires_unix=self.expires_unix)
            return result
        except Exception as error:
            # The initial POST may also have committed before transport failed.
            self._renewal_uncertain = True
            self._event("RESERVE_ERROR", error_type=type(error).__name__,
                        outcome_uncertain=True)
            raise

    def renew_if_due(self, held_owner_pid=None):
        if held_owner_pid is not None and held_owner_pid != os.getpid():
            raise RuntimeError("LEASE_CALLER_OWNER_MISMATCH")
        if self.request_id is None:
            raise RuntimeError("LEASE_NOT_RESERVED")
        if self._renewal_uncertain:
            raise RuntimeError("LEASE_UNCERTAIN_REQUIRES_SAFE_STOP")
        try:
            value = self.get()  # Inherited challenge/loaded-gate/incarnation checks.
            current = self._verify_held(value, self.request_id)
            now = time.time()
            self.expires_unix = self._expiry(current, now)
            if self.expires_unix - now >= RENEW_BEFORE_SECONDS:
                return dict(renewed=False, request_id=self.request_id,
                            expires_unix=self.expires_unix)
            previous_id = self.request_id
            # Treat all subsequent failures as possibly committed. Cleanup must
            # re-read claimant identity rather than rely on previous_id.
            self._renewal_uncertain = True
            result, _ = self.api(
                "POST", "/gpu-sharing/reservation",
                dict(owner_pid=os.getpid(), ttl_seconds=RENEW_TTL_SECONDS,
                     pause_new_work=True), admin=True)
            renewed = result.get("reservation") or {}
            if (result.get("ownership_granted") is not False
                    or not self._same_claimant(renewed)):
                raise RuntimeError("LEASE_RENEW_RESPONSE_IDENTITY_INVALID")
            new_id = renewed.get("request_id")
            if not isinstance(new_id, str) or not new_id or new_id == previous_id:
                raise RuntimeError("LEASE_RENEW_RESPONSE_ID_INVALID")
            expiry = self._expiry(renewed, time.time())
            if expiry > time.time() + RENEW_TTL_SECONDS + 5:
                raise RuntimeError("LEASE_RENEW_RESPONSE_TTL_INVALID")
            self.request_id = new_id
            verified = self.get()
            live = self._verify_held(verified, new_id)
            if self._expiry(live, time.time()) != expiry:
                raise RuntimeError("LEASE_RENEW_POST_ATTESTATION_CHANGED")
            self.expires_unix = expiry
            self._renewal_uncertain = False
            return self._event(
                "RENEWED", renewed=True, previous_request_id=previous_id,
                request_id=new_id, expires_unix=expiry,
                ownership_granted=False)
        except Exception as error:
            self._event("RENEW_ERROR", error_type=type(error).__name__,
                        outcome_uncertain=self._renewal_uncertain,
                        request_id=self.request_id)
            raise

    def check(self, row):
        self.renew_if_due(held_owner_pid=os.getpid())
        return super().check(row)

    def release(self):
        # DELETE has no request-id condition. Never send it on a foreign
        # reservation or on an unverified/stale GET.
        if self.request_id is None and not self._reservation_attempted:
            return dict(reservation_created=False)
        try:
            value = self.get()
            current = value.get("reservation")
            if not current:
                return self._event("RELEASE_ALREADY_ABSENT", released=True)
            if not self._same_claimant(current):
                return self._event("RELEASE_REFUSED_FOREIGN", released=False,
                                   reason="Current claimant is not this process")
            current_id = current.get("request_id")
            if not isinstance(current_id, str) or not current_id:
                raise RuntimeError("LEASE_RELEASE_CURRENT_ID_INVALID")
            if current_id != self.request_id and not self._renewal_uncertain:
                return self._event(
                    "RELEASE_REFUSED_ID_CHANGE", released=False,
                    reason="Current id changed outside own uncertain POST")
            # Adopt only a same-incarnation claimant proven by fresh get().
            self.request_id = current_id
            result, _ = self.api("DELETE", "/gpu-sharing/reservation", admin=True)
            if (result.get("ownership_granted") is not False
                    or result.get("reservation")):
                raise RuntimeError("LEASE_RELEASE_RESPONSE_INVALID")
            final = self.get()
            if final.get("reservation"):
                raise RuntimeError("LEASE_RELEASE_POST_ATTESTATION_NOT_EMPTY")
            self._renewal_uncertain = False
            self.request_id = None
            return self._event("RELEASED", released=True,
                               ownership_granted=False)
        except Exception as error:
            return self._event("RELEASE_ERROR", released=False,
                               error_type=type(error).__name__,
                               outcome_uncertain=True)
