"""Synthetic pure-control tests: no scientific paths are opened or changed."""
import copy
import json
import unittest

import tls_v10_selector as tls
import v9_transaction as v9


class SelectorTests(unittest.TestCase):
    def setUp(self):
        self.group = 'P9_PUBLIC'
        self.root = tls.GROUPS[self.group]
        self.commit = 'a' * 40
        self.dirs = [self.row('.', 'directory'), self.row('d', 'directory'),
                     self.row('d/empty', 'directory')]
        self.files = [self.row('d/f', 'regular')]

    def row(self, relative, kind):
        return dict(schema='TLS_V10_OLD174_EXACT_SOURCE_ENTRY_V1', type=kind,
                    source_root=self.root,
                    source_path=self.root if relative == '.' else self.root + '/' + relative,
                    relative_path=relative, source_commit='b' * 40, dev=156, inode=100,
                    nlink=1 if kind == 'regular' else 2, uid=12345, gid=23456,
                    mode_octal='0o640' if kind == 'regular' else '0o750',
                    mtime_ns=1770000000123456789, ctime_ns=1770000000987654321,
                    size_bytes=23 if kind == 'regular' else 4096, allocated_bytes=4096,
                    sha256='c' * 64 if kind == 'regular' else None, source_action='SOURCE_KEEP')

    @staticmethod
    def raw(rows):
        return b''.join(v9.canonical(r) for r in rows)

    def build(self, files=None, dirs=None, commit=None):
        return tls.build_manifest(self.raw(self.files if files is None else files),
                                  self.raw(self.dirs if dirs is None else dirs),
                                  self.commit if commit is None else commit, self.group)

    def test_repeat_and_exact_v9_identity(self):
        first, txid = self.build()
        self.assertEqual((first, txid), self.build())
        self.assertEqual(txid, v9.validate_manifest(first))
        self.assertEqual(first['selector_sha256'], v9.digest(v9.canonical(first['files'])))
        self.assertEqual(first['source_file_inventory_sha256'], v9.digest(self.raw(self.files)))
        self.assertEqual(first['source_directory_inventory_sha256'], v9.digest(self.raw(self.dirs)))
        self.assertEqual(first['source_filesystem_identity'], tls.SOURCE_FS)
        self.assertTrue(first['genuine164_destination_root'].endswith(first['selector_sha256']))
        self.assertEqual(first['destination_path_on_174new'], '/root/share/mnt164' + first['genuine164_destination_root'][len('/home/shared'):])
        self.assertEqual(first['source_originals_action'], 'SOURCE_KEEP_NO_RELEASE_AUTHORITY')
        self.assertNotIn('txid', first)  # Full manifest SHA binds this exact object.

    def test_source_path_link_type_and_metadata_faults_hold(self):
        changes = [('relative_path', '../escape'), ('relative_path', '/absolute'),
                   ('relative_path', 'd//f'), ('relative_path', 'd/./f'),
                   ('relative_path', 'd\\f'), ('relative_path', 'd/\x00f'),
                   ('source_root', '/workspace/other'), ('source_path', self.root + '/different'),
                   ('type', 'symlink'), ('nlink', 2), ('nlink', True), ('dev', 2431),
                   ('inode', 0), ('uid', -1), ('size_bytes', -1), ('allocated_bytes', 513),
                   ('sha256', 'g' * 64), ('sha256', 'c' * 63), ('mode_octal', '0o100640'),
                   ('mode_octal', '0o888'), ('source_action', 'SOURCE_RELEASED'),
                   ('source_commit', 'x' * 40)]
        for key, value in changes:
            with self.subTest(key=key, value=value):
                rows = copy.deepcopy(self.files)
                rows[0][key] = value
                with self.assertRaises(v9.Hold):
                    self.build(files=rows)

    def test_duplicate_missing_parent_collision_hold(self):
        with self.assertRaises(v9.Hold):
            self.build(files=self.files * 2)
        with self.assertRaises(v9.Hold):
            self.build(dirs=[self.dirs[0], self.dirs[2]])
        collision = self.row('d/f', 'directory')
        with self.assertRaises(v9.Hold):
            self.build(dirs=self.dirs + [collision])
        with self.assertRaises(v9.Hold):
            self.build(dirs=self.dirs + [self.dirs[0]])
        with self.assertRaises(v9.Hold):
            self.build(dirs=self.dirs[1:])

    def test_empty_directory_only_group_is_exact_not_sample(self):
        m, _ = self.build(files=[])
        self.assertEqual(m['files'], [])
        self.assertEqual(len(m['directories']), 3)
        with self.assertRaises(v9.Hold):
            self.build(files=[], dirs=[self.dirs[0], self.dirs[2]])

    def test_manifest_order_and_frozen_identity_do_not_silently_change(self):
        rows = self.files + [self.row('d/another', 'regular')]
        a, at = self.build(files=rows)
        b, bt = self.build(files=list(reversed(rows)))
        self.assertNotEqual(a['selector_sha256'], b['selector_sha256'])
        self.assertNotEqual(at, bt)
        changed, ct = self.build(files=rows, commit='d' * 40)
        self.assertEqual(a['selector_sha256'], changed['selector_sha256'])
        self.assertNotEqual(at, ct)

    def test_directory_metadata_full_manifest_sha_binding(self):
        a, at = self.build()
        dirs = copy.deepcopy(self.dirs)
        dirs[2]['mode_octal'] = '0o700'
        b, bt = self.build(dirs=dirs)
        # The agreed V9 V2 selector is file-only; full manifest SHA additionally binds directories.
        self.assertEqual(at, bt)
        self.assertNotEqual(v9.digest(v9.canonical(a)), v9.digest(v9.canonical(b)))
        self.assertNotEqual(a['source_directory_inventory_sha256'], b['source_directory_inventory_sha256'])

    def test_large_file_keeps_original_identity_not_fictional_chunk_file(self):
        rows = copy.deepcopy(self.files)
        rows[0]['size_bytes'] = 285915764
        rows[0]['allocated_bytes'] = 285917184
        m, _ = self.build(files=rows)
        self.assertEqual(m['files'][0]['size'], 285915764)
        self.assertGreater(m['files'][0]['size'], v9.CAP)
        self.assertEqual(m['files'][0]['sha256'], self.files[0]['sha256'])

    def test_unknown_group_and_bad_publication_hold(self):
        with self.assertRaises(v9.Hold):
            tls.build_manifest(self.raw(self.files), self.raw(self.dirs), self.commit, 'MATRIX_V2_ACTIVE')
        with self.assertRaises(v9.Hold):
            self.build(commit='bad')


if __name__ == '__main__':
    unittest.main()
