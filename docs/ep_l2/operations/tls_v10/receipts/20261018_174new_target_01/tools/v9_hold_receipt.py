"""Immutable failure receipts layered on the frozen V9 transaction primitives."""
from contextlib import contextmanager
import json

from v9_transaction import canonical, digest, exclusive_json, no_symlinks, require


def record_hold(transaction, failed_step, reason):
    require(isinstance(reason, str) and reason and isinstance(failed_step, str), 'invalid HOLD reason')
    prior = sorted((transaction.work / 'receipts').glob('*.json'))
    if prior:
        last = json.loads(prior[-1].read_bytes())
        # Reusing an existing state validates the entire previous hash chain.
        transaction.transition(last['state'], last['evidence'])
    receipt = dict(schema='STORAGE_OPS_V9_IMMUTABLE_HOLD', status='HOLD', txid=transaction.txid,
                   failed_step=failed_step, reason=reason,
                   previous_receipt_sha256=digest(prior[-1].read_bytes()) if prior else None,
                   manifest_sha256=digest(canonical(transaction.manifest)),
                   source_originals='SOURCE_KEEP', source_release_authorized=False)
    directory = no_symlinks(transaction.work / 'holds'); directory.mkdir(exist_ok=True)
    path = directory / (digest(canonical(receipt)) + '.json')
    sha256 = exclusive_json(path, receipt)
    return dict(path=str(path), sha256=sha256, receipt=receipt)


@contextmanager
def guard(transaction, failed_step):
    """A failed archive step records HOLD, preserves prior success and re-raises.

    An unavailable evidence filesystem still propagates failure: callers must
    publish the error through their independent Git/local audit, never PASS.
    """
    try:
        yield
    except Exception as error:
        record_hold(transaction, failed_step, str(error))
        raise
