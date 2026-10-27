"""CPU-qualified private chooser gate; import does not install or dispatch.

No stale/empty resource frame is returned. Transient read failure blocks this
admission pass only. Original chooser gates, claims and model identities remain.
"""
import copy
import json
import time


class FrameUnavailable(Exception):
    def __init__(self, evidence):
        super().__init__('bounded frame read unavailable')
        self.evidence = evidence


class FrameReadGuard:
    def __init__(self, aging, attempts=3, retry_delays=(.02, .05), sleeper=time.sleep):
        assert attempts == 3 and tuple(retry_delays) == (.02, .05)
        self.aging = aging
        self.original_choose = aging.wrapper
        self.original_provider = aging.frame_provider
        self.attempts = attempts
        self.delays = retry_delays
        self.sleeper = sleeper
        self.last_issue = None
        self.last_recovery = None
        self.last_pass_status = 'NOT_CALLED'
        self.failclosed_passes = 0
        self.wrapper = self.choose

    def frames(self, *args, **kwargs):
        errors = []
        for attempt in range(self.attempts):
            try:
                frame = self.original_provider(*args, **kwargs)
            except (json.JSONDecodeError, UnicodeDecodeError, OSError) as error:
                # Invalid contracts/keys/assertions are deliberately not hidden.
                errors.append(dict(attempt=attempt + 1, error_type=type(error).__name__,
                                   error=str(error)[:500]))
                if attempt + 1 < self.attempts:
                    self.sleeper(self.delays[attempt])
                    continue
                raise FrameUnavailable(dict(status='FRAME_READ_UNAVAILABLE',
                    errors=errors, attempts=self.attempts, retry_sleep_seconds=sum(self.delays),
                    resource_snapshot_fabricated=False, stale_frame_reused=False)) from error
            if errors:
                self.last_recovery = dict(status='FRAME_READ_RECOVERED', errors=errors,
                                          attempts=attempt + 1)
            return frame

    def choose(self, *args, **kwargs):
        aging = self.aging
        with aging.lock:
            # A failure may occur on the fresh second frame, after advance().
            # Restore only private aging accounting; do not touch external state.
            before = copy.deepcopy(aging.state.__dict__)
            calls_before = aging.calls
            assert aging.frame_provider is self.original_provider
            aging.frame_provider = self.frames
            try:
                value = self.original_choose(*args, **kwargs)
                self.last_issue = None
                self.last_pass_status = 'VALID_FRESH_FRAMES'
                return value
            except FrameUnavailable as error:
                aging.state.__dict__.clear()
                aging.state.__dict__.update(before)
                aging.calls = calls_before
                self.failclosed_passes += 1
                self.last_issue = dict(error.evidence, state_restored=True,
                    admission_returned_none=True, failclosed_passes=self.failclosed_passes,
                    journal_note='Any earlier decision journal entry in this pass is aborted; no proposal returned.')
                self.last_pass_status = 'FAILCLOSED_FRAME_UNAVAILABLE'
                return None
            finally:
                aging.frame_provider = self.original_provider


# Main may install gate.wrapper on the existing private owner, maintaining its
# existing restore chain. There is intentionally no auto-install API here.
