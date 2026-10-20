"""Log-observation integrity controls, not simulator/native qualification."""
import tempfile
import unittest
from pathlib import Path
import paper_four_pair_details as p
import sync_intake as i

class PaperObservations(unittest.TestCase):
    def test_two_wait_versions_and_cumulative_delta_not_sum_of_snapshots(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'raw.log';lines=[]
            for n,clock,value in [(1,10,5),(2,20,8)]:
                lines.extend([f'kernel_name = kernel{n}\n',f'gpu_sim_cycle = 10\n',f'gpu_tot_sim_cycle = {clock}\n'])
                for sid in range(64):
                    for version,reason in [('EPL2MSV1',1),('EPL2MSV2',15)]:
                        lines.append(f'{version}|WAIT|slice={sid}|reason={reason}|requests=1|resolved=1|sum={value}|max={value}|observations={value}|unknown_while_unresolved=0\n')
            path.write_text(''.join(lines));r=p.observe(path,i.digest(path))
            self.assertEqual(r['frames'][-1]['cumulative']['wait_landing_sum'],64*8)
            self.assertEqual(r['frames'][-1]['counter_snapshot_delta']['wait_landing_sum'],64*3)
            self.assertEqual(r['frames'][-1]['counter_snapshot_delta']['wait_V_query_sum'],64*3)
            self.assertEqual(r['frames'][-1]['cumulative']['EPL2TVDV2_read_responses'],'UNKNOWN')
            with self.assertRaisesRegex(ValueError,'raw bytes changed'):p.observe(path,'wrong')

    def test_elapsed_kernel_sum_and_terminal_residual_are_separate(self):
        obs={s:{'frames':[{'kernel_name':'k','gpu_sim_cycle':n,'gpu_tot_sim_cycle':n,
          'counter_snapshot_delta':{},'raw_clock_line':1},{'kernel_name':'','gpu_sim_cycle':0,
          'gpu_tot_sim_cycle':n+tail,'counter_snapshot_delta':{},'raw_clock_line':2}]} for s,n,tail in [('S',100,9),('F',90,12)]}
        rows=p.paired_timing('x',obs)
        self.assertEqual(rows[0]['F_minus_S_cycles'],-10)
        self.assertEqual(rows[-1]['F_minus_S_cycles'],3)
        self.assertEqual(sum(x['F_minus_S_cycles'] for x in rows),-7)
        obs['F']['frames'][0]['kernel_name']='other'
        with self.assertRaisesRegex(ValueError,'different named kernel'):p.paired_timing('x',obs)

if __name__=='__main__':unittest.main()
