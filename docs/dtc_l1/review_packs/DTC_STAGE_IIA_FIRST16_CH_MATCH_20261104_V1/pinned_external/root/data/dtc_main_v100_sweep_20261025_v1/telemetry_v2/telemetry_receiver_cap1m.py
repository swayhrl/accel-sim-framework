"""Prepared opt-in AG7 datagram receiver; never launches, adopts or signals.

Kernel credentials authenticate the sender PID; the BA observer must separately
prove PID generation, image, input and ROI before constructing the binding.
No packet, including a natural candidate, grants scientific acceptance.
"""
import json
import socket
import struct


class TelemetryError(ValueError):
    pass


PHASES = frozenset(('INIT', 'PARSE', 'SIMULATE', 'BOUNDARY'))
TERMINALS = frozenset(('NONE', 'NATURAL', 'LIMIT', 'ERROR'))
BINDING_KEYS = ('pid', 'start_ticks', 'generation', 'input', 'roi')


def integer(value, low=0, high=(1 << 64) - 1):
    return type(value) is int and low <= value <= high


class TelemetryReceiver:
    MAX_PACKET = 1024
    MAX_RECORDS = 1048576
    MAX_FRESH_NS = 30_000_000_000

    def __init__(self, channel, binding, *, started_ns, opt_in=False):
        if opt_in is not True:
            raise TelemetryError('EXPLICIT_POLICY_B_OPT_IN_REQUIRED')
        if not isinstance(binding, dict) or binding.get('proven_actual_root') is not True:
            raise TelemetryError('ACTUAL_POSTFORK_ROOT_BINDING_REQUIRED')
        if any(k not in binding for k in BINDING_KEYS) or not integer(started_ns, 1):
            raise TelemetryError('INCOMPLETE_BINDING_OR_START_TIME')
        for key in ('pid', 'start_ticks'):
            if not integer(binding[key], 1):
                raise TelemetryError('INVALID_BINDING_INTEGER')
        generation = binding['generation']
        if (not isinstance(generation, str) or not 1 <= len(generation) <= 64 or
                any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_.:' for c in generation)):
            raise TelemetryError('INVALID_GENERATION_TOKEN')
        for key, length in (('input', 64), ('roi', 64)):
            value = binding[key]
            if not isinstance(value, str) or len(value) != length or any(c not in '0123456789abcdef' for c in value):
                raise TelemetryError('INVALID_BINDING_DIGEST')
        if channel.family != socket.AF_UNIX or channel.getsockopt(socket.SOL_SOCKET, socket.SO_TYPE) != socket.SOCK_DGRAM:
            raise TelemetryError('DEDICATED_UNIX_DATAGRAM_REQUIRED')
        if channel.getblocking() or channel.getsockopt(socket.SOL_SOCKET, socket.SO_PASSCRED) != 1:
            raise TelemetryError('NONBLOCKING_PASSCRED_REQUIRED')
        self.channel = channel
        self.binding = {k: binding[k] for k in BINDING_KEYS}
        self.started_ns = started_ns
        self.last = None
        self.last_semantic = None
        self.last_sequence = 0
        self.last_consumer_ns = started_ns
        self.failed = None
        self.terminal = None

    def _fail(self, reason):
        self.failed = reason
        raise TelemetryError(reason)

    def _accept(self, data, ancillary, flags, now_ns):
        if flags & (socket.MSG_TRUNC | socket.MSG_CTRUNC):
            self._fail('TRUNCATED_TELEMETRY_OR_CREDENTIALS')
        credentials = [payload for level, kind, payload in ancillary
                       if level == socket.SOL_SOCKET and kind == socket.SCM_CREDENTIALS]
        if len(credentials) != 1 or len(credentials[0]) != struct.calcsize('3i'):
            self._fail('MISSING_OR_AMBIGUOUS_KERNEL_CREDENTIALS')
        pid, uid, _gid = struct.unpack('3i', credentials[0])
        if pid != self.binding['pid'] or uid != 0:
            self._fail('SENDER_IS_NOT_PROVEN_ACTUAL_ROOT')
        if not data or len(data) >= self.MAX_PACKET:
            self._fail('INVALID_PACKET_SIZE')
        try:
            def unique(pairs):
                result = {}
                for key, value in pairs:
                    if key in result:
                        raise ValueError('duplicate key')
                    result[key] = value
                return result
            record = json.loads(data.decode('utf-8'), object_pairs_hook=unique,
                                parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))
        except (UnicodeError, ValueError, TypeError):
            self._fail('MALFORMED_TELEMETRY')
        keys = set(BINDING_KEYS) | {'v', 'seq', 'mono_ns', 'epoch',
            'phase_epoch', 'phase', 'stream_id', 'stream_scope', 'completed', 'end'}
        if not isinstance(record, dict) or set(record) != keys or record['v'] != 1 or type(record['v']) is not int:
            self._fail('UNKNOWN_OR_INCOMPLETE_SCHEMA')
        if any(record[k] != self.binding[k] or type(record[k]) is not type(self.binding[k]) for k in BINDING_KEYS):
            self._fail('PRODUCER_IDENTITY_OR_INPUT_SCOPE_MISMATCH')
        seq, now = record['seq'], record['mono_ns']
        if not integer(seq, 1, self.MAX_RECORDS) or seq != self.last_sequence + 1:
            self._fail('LOST_DUPLICATE_OR_REVERSED_SEQUENCE')
        if not integer(now, self.started_ns) or now > now_ns or now_ns - now > self.MAX_FRESH_NS:
            self._fail('STALE_FUTURE_OR_PRESTART_RECORD')
        if self.last is not None and (now <= self.last['mono_ns'] or now - self.last['mono_ns'] > self.MAX_FRESH_NS):
            self._fail('REVERSED_CLOCK_OR_PRODUCER_GAP')
        if record['epoch'] != 0 or type(record['epoch']) is not int or record['stream_scope'] != 'whole_input':
            self._fail('UNSUPPORTED_COUNTER_EPOCH_OR_STREAM_SCOPE')
        if (not isinstance(record['phase'], str) or not isinstance(record['end'], str) or
                record['phase'] not in PHASES or record['end'] not in TERMINALS or
                not integer(record['phase_epoch'], 1) or
                not integer(record['stream_id'], -1, (1 << 63) - 1) or
                not integer(record['completed'])):
            self._fail('INVALID_METRIC_OR_PHASE')
        if self.last is None and (record['phase'] != 'INIT' or record['phase_epoch'] != 1):
            self._fail('MISSING_INITIAL_PRODUCER_EPOCH')
        if self.last is not None:
            changed = record['phase'] != self.last['phase']
            if record['phase_epoch'] != self.last['phase_epoch'] + int(changed):
                self._fail('LOST_OR_RESET_PHASE_EPOCH')
        if self.terminal is not None:
            self._fail('LATE_RECORD_AFTER_PRODUCER_TERMINAL')
        if record['end'] != 'NONE' and record['phase'] != 'BOUNDARY':
            self._fail('TERMINAL_OUTSIDE_RUN_END')
        if self.last_semantic is not None and record['completed'] < self.last_semantic['completed']:
            self._fail('COMPLETION_COUNTER_REVERSED_OR_RESET')
        self.last_semantic = dict(record)
        self.last = dict(record)
        self.last_sequence = seq
        if record['end'] != 'NONE':
            self.terminal = record['end']
        return dict(record)

    def drain(self, now_ns):
        """Consume bounded records; pass a live monotonic callable in production.

        Integer timestamps support declared synthetic tests. A live callable is
        sampled after each recvmsg and once after draining, so a packet emitted
        during receive cannot be mistaken for a future producer observation.
        Consumer time is used only for validation, never stored as progress.
        """
        if self.failed:
            raise TelemetryError(self.failed)
        def consumer_now():
            try:
                current = now_ns() if callable(now_ns) else now_ns
            except Exception:
                self._fail('CONSUMER_CLOCK_ERROR')
            if not integer(current, self.last_consumer_ns):
                self._fail('INVALID_OR_REVERSED_CONSUMER_CLOCK')
            self.last_consumer_ns = current
            return current
        records = []
        for _ in range(8192 + 1):
            try:
                data, ancillary, flags, _address = self.channel.recvmsg(
                    self.MAX_PACKET, socket.CMSG_SPACE(struct.calcsize('3i')),
                    socket.MSG_DONTWAIT)
            except BlockingIOError:
                break
            except OSError:
                self._fail('TELEMETRY_CHANNEL_ERROR')
            records.append(self._accept(data, ancillary, flags, consumer_now()))
        else:
            self._fail('TELEMETRY_DRAIN_BOUND_EXCEEDED')
        last_time = self.started_ns if self.last is None else self.last['mono_ns']
        if consumer_now() - last_time > self.MAX_FRESH_NS:
            self._fail('MISSING_OR_STALE_PRODUCER')
        return {'records': records, 'latest': None if self.last is None else dict(self.last),
                'latest_semantic': None if self.last_semantic is None else dict(self.last_semantic),
                'terminal': self.terminal, 'scientific_acceptance': False}
