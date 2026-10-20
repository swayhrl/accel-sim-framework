"""Additive exact-P9 resource gate; existing transfer/ACK primitives stay pinned.

Only this subclass replaces the workspace-floor admission decision. Original
runner, all24 controllers, scientific gates and release code are untouched.
The existing COPY16 names identify the historical wire protocol, while gate
records explicitly name the new effective policy and measured free bytes.
"""
from dataclasses import replace
import os
import time
import fcntl
from pathlib import Path

import tls_v10_copy_only16g_gate as original
import tls_v10_p9_exact_window_runner as parent
import tls_v10_p9_lowspace5_gate as policy


class LowSpaceP9Runner(parent.ExactWindowRunner):
    def __init__(self, context, binding_path, *, action):
        super().__init__(context, binding_path, lambda: parent.production_evidence(binding_path))
        parent._require(context.production, 'low-space runner requires original Source production context')
        self.action = action

    def _gate(self, inspected, *, staged_physical=0):
        ctx=self.ctx
        parent._check_context(ctx)
        binding=parent._json(self.binding_path.read_bytes())
        req=inspected['request']
        window=inspected['window_id']
        match=parent.WINDOW_RE.fullmatch(window)
        parent._require(match is not None and binding['window_id']==window and
                        binding['txid']==parent.old.TXID and
                        binding['selector_sha256']==parent.old.SELECTOR and
                        binding['canonical_manifest_sha256']==parent.old.MANIFEST_SHA256 and
                        binding['source_root']==parent.old.SOURCE_ROOT and
                        binding['target_root_native164']==parent.old.TARGET_ROOT and
                        binding['target_request_sha256']==inspected['request_sha256'] and
                        inspected['manifest_sha256']==parent.old.MANIFEST_SHA256 and
                        req['window_id']==window and req['txid']==parent.old.TXID,
                        'low-space exact binding mismatch')
        first_at=time.monotonic()
        v=os.statvfs('/workspace'); first=v.f_bavail*v.f_frsize
        time.sleep(2)
        snap=self.evidence()
        receiver_idle=False
        with (ctx.bridge/'.TARGET_RECEIVER.lock').open('r+b') as receiver:
            try:
                fcntl.flock(receiver,fcntl.LOCK_EX|fcntl.LOCK_NB)
                receiver_idle=True
            except BlockingIOError:
                pass
        v=os.statvfs('/workspace'); last=v.f_bavail*v.f_frsize
        observed_at=time.monotonic()
        reserve=policy.growth_reserve(first,last,observed_at-first_at)
        b=snap['base']
        parent._require(b.window_id==window and
                        b.target_request_sha256==inspected['request_sha256'],
                        'fresh gate window mismatch')
        projected=0 if staged_physical else req['raw_bytes']+parent.MIB
        parent._require(parent._bridge_allocated(ctx.bridge)+projected<=256*parent.MIB,
                        'whole bridge physical cap')
        # A real statvfs refresh, never an artificial floor offset.
        b=replace(b,workspace_available_bytes=last,
                  planned_bridge_staged_bytes=projected,
                  planned_rate_bytes_per_second=parent.old.MAX_RATE_BPS,
                  first_source_identity_ok=True, first_source_sha_refreshed=True,
                  target_request_present_and_exact=True)
        adapter=replace(b,window_id=parent.old.WINDOW,
                        target_request_sha256=parent.old.TARGET_REQUEST_SHA256)
        decision=policy.evaluate(original.Copy16Input(
            adapter,original.APPROVAL_SHA256,req['raw_bytes'],True,True,
            snap['lane_final_closure_verified'],snap['lane_physical_clear']),
            window=int(match[1]),action=self.action,predicted_growth_bytes=reserve,
            growth_sample_age_seconds=time.monotonic()-observed_at)
        parent._require(decision['decision']=='POLICY_ELIGIBLE_NOT_READY',
                        'P9 COPY5 resource HOLD: '+','.join(decision['reasons']))
        parent._require(snap['source_reader_clear'] and snap['scheduled_reader_clear'] and
                        snap['sole_sender_clear'] and snap['receiver_clear'] and receiver_idle and
                        parent.SHA_RE.fullmatch(inspected['target_receiver_preflight_sha256']) is not None,
                        'reader/sender/receiver not independently clear')
        return dict(decision=decision,workspace_available_bytes=last,
                    share_available_bytes=b.share_available_bytes,
                    snapshot_age_seconds=b.snapshot_age_seconds,
                    staged_physical_bytes=staged_physical,
                    growth_sample=dict(first_available_bytes=first,last_available_bytes=last,
                                       interval_seconds=observed_at-first_at),
                    first_source_SHA_claim='BOUNDED_RANGE_INSPECTION_OR_EXACT_ACK_CORE_REQUIRED_SEPARATELY',
                    source_originals='SOURCE_KEEP',source_unlinks=0)
