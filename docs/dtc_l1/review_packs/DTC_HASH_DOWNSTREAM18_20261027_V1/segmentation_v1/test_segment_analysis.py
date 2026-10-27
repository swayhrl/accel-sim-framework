"""CPU-only scientific-parser tests; no simulator imports or starts."""
import gzip
import unittest
import segment_analysis as s

def row(work,cycles,past=0,line=2,metric=0):
 return {'line':line,'cycles':cycles,'instructions':past+work,'past_instructions':past,'kernel_instructions':work,'wall_ms':cycles,
  'metrics':{'dram_read_atoms':metric,'l2_fifo_full_events':metric},'dram_per_mc':[metric],
  'fifo_per_sp':[metric],'retired_warp_per_sm':[work]}

class SegmentationTests(unittest.TestCase):
 def test_concatenated_members_and_incomplete_tail(self):
  one=gzip.compress(b'header\n');two=gzip.compress(b'123\n');tail=gzip.compress(b'456\npartial')
  raw,meta=s.inflate_live(one+two+tail[:-8])
  self.assertEqual(raw,b'header\n123\n456\n');self.assertEqual(meta['complete_members'],2);self.assertTrue(meta['open_tail'])
 def test_gzip_corruption_is_not_missing_or_zero(self):
  data=bytearray(gzip.compress(b'abc\n'));data[-8]^=1
  with self.assertRaisesRegex(ValueError,'CORRUPT'):s.inflate_live(bytes(data))
 def test_partial_csv_row_not_accepted(self):
  header='gpu_tot_sim_cycle,gpu_sim_cycle,gpu_tot_sim_insn,gpu_sim_insn,wall_clock_ms,\n'
  data=gzip.compress((header+'0,100,0,20,1000,\n0,200,0,').encode())
  rows,meta=s.parse_perf(data);self.assertEqual(len(rows),1);self.assertGreater(meta['discarded_partial_line_bytes'],0)
 def test_bad_csv_width_fails_closed(self):
  header='gpu_tot_sim_cycle,gpu_sim_cycle,gpu_tot_sim_insn,gpu_sim_insn,wall_clock_ms,\n'
  with self.assertRaisesRegex(ValueError,'WIDTH'):s.parse_perf(gzip.compress((header+'0,100,0,20,\n').encode()))
 def test_missing_metrics_are_none(self):
  header='gpu_tot_sim_cycle,gpu_sim_cycle,gpu_tot_sim_insn,gpu_sim_insn,wall_clock_ms,\n'
  rows,meta=s.parse_perf(gzip.compress((header+'0,100,0,20,1000,\n').encode()))
  self.assertIsNone(rows[0]['metrics']['dram_read_atoms']);self.assertIn('dram_read_atoms',meta['missing_groups'])
 def test_global_counter_reset_rejected(self):
  header='gpu_tot_sim_cycle,gpu_sim_cycle,gpu_tot_sim_insn,gpu_sim_insn,wall_clock_ms,\n'
  with self.assertRaisesRegex(ValueError,'NONMONOTONE'):s.parse_perf(gzip.compress((header+'0,100,0,20,1000,\n0,50,0,30,2000,\n').encode()))
 def test_terminal_boundary_and_cumulative_cross_kernel(self):
  kernels=[dict(ordinal=1,kernel='a',active_thread_instructions=100),dict(ordinal=2,kernel='b',active_thread_instructions=200)]
  rows=[row(50,100,metric=10),row(100,200,line=3,metric=20),row(40,300,past=100,line=4,metric=30)]
  curves=s.kernel_curves(rows,kernels);self.assertTrue(curves[1]['baseline_observed'])
  a=s.anchor(curves[1],0);b=s.anchor(curves[1],40)
  self.assertEqual(s.delta_bound(a['counters']['dram_read_atoms'],b['counters']['dram_read_atoms'])['estimate'],10)
  self.assertEqual(s.delta_bound(a['cycles'],b['cycles'])['estimate'],100)
 def test_missing_terminal_does_not_forge_second_baseline(self):
  kernels=[dict(ordinal=1,kernel='a',active_thread_instructions=100),dict(ordinal=2,kernel='b',active_thread_instructions=200)]
  curves=s.kernel_curves([row(50,100),row(40,300,past=100)],kernels)
  self.assertIsNone(s.anchor(curves[1],0));self.assertEqual(s.segment(curves[1],0,5)['status'],'PENDING_OR_MISSING_BOUNDARY')
 def test_interpolation_is_bounded_and_not_exact(self):
  curve={'population':100,'ordinal':1,'points':[dict(work=0,row=row(0,0)),dict(work=50,row=row(50,100)),dict(work=100,row=row(100,300))]}
  a=s.anchor(curve,25);self.assertEqual(a['cycles'],dict(low=0,estimate=50,high=100));self.assertEqual(a['bracket_work'],[0,50])
  seg=s.segment(curve,0,25);self.assertTrue(seg['coarse']);self.assertEqual(seg['cycles']['estimate'],50)
 def test_repeated_full_work_retains_last_drain_sample(self):
  k=[dict(ordinal=1,kernel='a',active_thread_instructions=100)]
  curves=s.kernel_curves([row(100,200),row(100,250,line=3)],k)
  self.assertEqual(s.anchor(curves[0],100)['cycles']['estimate'],250)
 def test_reset_counter_is_none_not_zero(self):
  self.assertIsNone(s.delta_bound(dict(low=10,estimate=10,high=10),dict(low=2,estimate=2,high=2)))
 def test_ratio_direction_and_bounds(self):
  r=s.ratio_bounds(dict(low=18,estimate=20,high=22),dict(low=9,estimate=10,high=11))
  self.assertEqual(r['estimate'],2);self.assertAlmostEqual(r['low'],18/11);self.assertAlmostEqual(r['high'],22/9)
 def test_unbounded_denominator_not_fake_infinity(self):
  r=s.ratio_bounds(dict(low=1,estimate=2,high=3),dict(low=0,estimate=1,high=2));self.assertIsNone(r['high'])
 def test_script_payload_escapes_html(self):
  text=s.render({'x':'</script><script>oops</script>'},'__PAYLOAD__')
  self.assertNotIn('</script>',text);self.assertIn('\\u003c',text)

if __name__=='__main__':unittest.main(verbosity=2)
