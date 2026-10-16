import gzip
import hashlib
import io
import tarfile
import unittest

from polybench_archive_restore_audit import RateDigestReader, expected_members, recover_members


def payload(entries):
    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode='w') as archive:
        for name, content in entries:
            member = tarfile.TarInfo(name)
            member.size = len(content)
            archive.addfile(member, io.BytesIO(content))
    return gzip.compress(raw.getvalue())


class RestoreChecks(unittest.TestCase):
    def setUp(self):
        self.expected = {'polybench/example/traces/a': dict(logical_bytes='5',
                         sha256=hashlib.sha256(b'trace').hexdigest())}

    def run_stream(self, data, expected=None):
        reader = RateDigestReader(io.BytesIO(data), lambda: None)
        with gzip.GzipFile(fileobj=reader) as decoded:
            result = recover_members(decoded, self.expected if expected is None else expected)
            while decoded.read(4096):
                pass
        while reader.read(4096):
            pass
        self.assertEqual(reader.count, len(data))
        self.assertEqual(reader.digest.hexdigest(), hashlib.sha256(data).hexdigest())
        return result

    def test_real_gzip_tar_recovers_selected_content_and_hashes_all_compressed_bytes(self):
        data = payload([('ignored', b'other'), ('polybench/example/traces/a', b'trace')])
        seen, size = self.run_stream(data)
        self.assertEqual((set(seen), size), (set(self.expected), 5))

    def test_silent_member_corruption_is_rejected(self):
        with self.assertRaisesRegex(RuntimeError, 'SHA256 mismatch'):
            self.run_stream(payload([('polybench/example/traces/a', b'wrong')]))

    def test_duplicate_selected_tar_member_is_rejected(self):
        entry = ('polybench/example/traces/a', b'trace')
        with self.assertRaisesRegex(RuntimeError, 'duplicate/nonregular'):
            self.run_stream(payload([entry, entry]))

    def test_missing_selected_member_is_rejected(self):
        with self.assertRaisesRegex(RuntimeError, 'incomplete selected'):
            self.run_stream(payload([('other', b'trace')]))

    def test_corrupt_gzip_trailer_is_rejected_after_tar_eof(self):
        data = bytearray(payload([('polybench/example/traces/a', b'trace')]))
        data[-8] ^= 1
        with self.assertRaises((gzip.BadGzipFile, EOFError)):
            self.run_stream(bytes(data))

    def test_parent_traversal_in_frozen_manifest_is_rejected(self):
        raw = b'relative_path_under_decoupled_l2_extract\tlogical_bytes\tsha256\n../polybench/a\t5\tx\n'
        with self.assertRaisesRegex(RuntimeError, 'unsafe stage'):
            expected_members(raw, hashlib.sha256(raw).hexdigest(), 1)


if __name__ == '__main__':
    unittest.main()
