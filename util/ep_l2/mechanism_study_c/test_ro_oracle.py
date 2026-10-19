import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("ro_oracle", Path(__file__).parent / "ro_oracle.py")
ro = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ro)


def kernel(instructions):
    return ("-grid dim = (1,1,1)\n-block dim = (32,1,1)\n"
            "#BEGIN_TB\nthread block = 0,0,0\nwarp = 0\ninsts = "
            + str(len(instructions)) + "\n" + "\n".join(instructions) + "\n#END_TB\n")


def ins(op, addr, width=4, mask="1"):
    return f"0 0 0 0 0000 {mask} 0 {op} 0 {width} 0 {addr:x}"


class OracleTest(unittest.TestCase):
    def host_case(self,command):
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup);root=Path(temp.name)
        (root/'kernel-0.traceg').write_text(kernel([ins('LDG',0x1000),ins('LDG',0x1080),ins('LDG',0x2000)]))
        (root/'kernelslist.g').write_text('kernel-0.traceg\n'+command+'\n')
        manifest=ro.build(root/'kernelslist.g',root/'out',ro.SCOPE,'CONTROL_FIXTURE_NOT_APPLICATION')
        return manifest,(root/'out/certified_lines.txt').read_text()

    def test_later_partial_host_write_excludes_whole_line(self):
        m,lines=self.host_case('MemcpyHtoD,0x1001,1')
        self.assertEqual(lines,'0000000000001080\n0000000000002000\n')
        self.assertEqual(m['host_updates_excluded'],[(0x1000,0x1000)])

    def test_host_write_crosses_two_lines(self):
        _,lines=self.host_case('MemcpyHtoD,0x107f,2')
        self.assertEqual(lines,'0000000000002000\n')

    def test_dtoh_is_not_a_gpu_writer(self):
        _,lines=self.host_case('MemcpyDtoH,0x1000,128')
        self.assertEqual(len(lines.splitlines()),3)

    def test_host_range_overflow_is_rejected(self):
        with self.assertRaises(ValueError):self.host_case('MemcpyHtoD,0xffffffffffffffff,2')

    def test_ambiguous_host_command_is_rejected(self):
        with self.assertRaises(ValueError):self.host_case('MemcpyHtoD,0x1000,128,unknown-agent')

    def run_build(self, kernels, scope=ro.SCOPE):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        names = []
        for i, text in enumerate(kernels):
            name = f"kernel-{i}.traceg"
            (root/name).write_text(text); names.append(name)
        (root/"kernelslist.g").write_text("\n".join(names)+"\n")
        manifest = ro.build(root/"kernelslist.g", root/"out", scope, "fixture")
        return manifest, (root/"out/certified_lines.txt").read_text()

    def test_cross_kernel_same_line_store_excludes_other_sector(self):
        m, lines = self.run_build([kernel([ins("LDG", 0x1000)]),
                                  kernel([ins("STG", 0x1060), ins("LDG", 0x2000)])])
        self.assertEqual(lines, "0000000000002000\n")
        self.assertEqual(m["counts"]["SAME_LINE_STORE_lines"], 1)

    def test_atomic_readlike_is_writer(self):
        m, lines = self.run_build([kernel([ins("LDG", 0x1000), ins("ATOM", 0x1004)])])
        self.assertEqual(lines, "")
        self.assertEqual(m["counts"]["SAME_LINE_ATOMIC_lines"], 1)

    def test_cross_line_width_excludes_both(self):
        _, lines = self.run_build([kernel([ins("LDG", 0x1000), ins("LDG", 0x1080),
                                          ins("STG.128", 0x1078, 16)])])
        self.assertEqual(lines, "")

    def test_unresolved_generic_writer_poison_epoch(self):
        m, lines = self.run_build([kernel([ins("LDG", 0x1000), ins("ST", 0x3000)])])
        self.assertEqual(lines, "")
        self.assertEqual(m["status"], "NO_CERTIFIED_LINES_UNRESOLVED_EPOCH")

    def test_full_kernel_required(self):
        with self.assertRaises(ValueError):
            self.run_build([kernel([ins("LDG", 0x1000)]).replace("#END_TB", "")])

    def test_missing_warp_is_not_full_epoch(self):
        with self.assertRaises(ValueError):
            self.run_build([kernel([ins("LDG", 0x1000)]).replace("(32,1,1)", "(64,1,1)")])

    def test_scope_must_be_explicit(self):
        with self.assertRaises(ValueError):
            self.run_build([kernel([ins("LDG", 0x1000)])], "UNKNOWN_EXTERNAL_WRITERS")

    def test_all_active_lanes_and_negative_stride(self):
        _, width, addresses = ro.instruction("0 0 0 0 0 f 0 LDG.U16 0 2 1 1006 -2")
        self.assertEqual((width, addresses), (2, [0x1006,0x1004,0x1002,0x1000]))

    def test_sparse_stride_rejected(self):
        with self.assertRaises(ValueError):
            ro.instruction("0 0 0 0 0 5 0 LDG 0 4 1 1000 4")

    def test_executed_store_without_addresses_rejected(self):
        with self.assertRaises(ValueError):
            ro.instruction("0 0 0 0 0 1 0 STG 0 0")

    def test_sparse_explicit_and_delta(self):
        self.assertEqual(ro.instruction("0 0 0 0 0 5 0 LDG 0 4 0 1000 2000")[2], [0x1000, 0x2000])
        self.assertEqual(ro.instruction("0 0 0 0 0 7 0 LDG 0 4 2 1000 32 -16")[2], [0x1000,0x1020,0x1010])

    def test_shared_store_does_not_alias_global(self):
        _, lines = self.run_build([kernel([ins("LDG", 0x1000), ins("STS", 0x1000)])])
        self.assertEqual(lines, "0000000000001000\n")

    def test_corrupt_instruction_is_rejected(self):
        with self.assertRaises(ValueError):
            self.run_build([kernel(["0 0 0 0 0 1 0 LDG 0 4 99 1000"])])

    def test_duplicate_threadblock_not_complete_epoch(self):
        x = kernel([ins("LDG", 0x1000)])
        stream = x.replace("(1,1,1)", "(2,1,1)") + x[x.index("#BEGIN_TB"):]
        with self.assertRaises(ValueError): self.run_build([stream])

    def test_instruction_identity_is_checked(self):
        with self.assertRaises(ValueError):
            self.run_build([kernel([ins("LDG", 0x1000).replace("0 0 0 0", "0 0 0 1", 1)])])

    def test_verify_binds_every_trace_and_artifact(self):
        temp = tempfile.TemporaryDirectory(); self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        (root/"kernel-1.traceg").write_text(kernel([ins("LDG", 0x1000)]))
        (root/"kernelslist.g").write_text("kernel-1.traceg\n")
        ro.build(root/"kernelslist.g", root/"out", ro.SCOPE, "fixture")
        self.assertEqual(ro.verify(root/"out")["kernel_count"], 1)
        (root/"out/certified_lines.txt").write_text("0000000000002000\n")
        with self.assertRaises(ValueError): ro.verify(root/"out")


if __name__ == "__main__":
    unittest.main()
