import os
os.sched_setaffinity(0, {22, 23})
import copy
import unittest
import torch
from torch.utils.data import Dataset, DataLoader
from loader_state import StatefulLoader, mapping_digest


class Fixture(Dataset):
    def __init__(self, n=19):
        self.n = n
        self.indices = [3 * i + 7 for i in range(n)]

    def __len__(self):
        return self.n

    def __getitem__(self, item):
        return {"image_id": item, "parser_index": self.indices[item],
                "pixels": torch.tensor([item, item + 0.25])}


def ids(batch):
    return batch["image_id"].tolist()


def digest(ds):
    return mapping_digest(ds.indices)


class LoaderStateTests(unittest.TestCase):
    def setUp(self):
        torch.set_num_threads(1)
        self.ds = Fixture()
        self.open_loaders = []

    def make(self, state=None, **kwargs):
        opts = dict(dataset_digest=digest(self.ds),
                    deterministic_dataset=True, batch_size=2,
                    num_workers=4, pin_memory=False, persistent_workers=True)
        opts.update(kwargs)
        loader = StatefulLoader(self.ds, restore_state=state, **opts)
        self.open_loaders.append(loader)
        return loader

    def tearDown(self):
        for loader in self.open_loaders:
            loader.close()

    def snapshot(self, n=3):
        torch.manual_seed(43021)
        loader = self.make()
        it = iter(loader)
        for _ in range(n):
            next(it)
        return loader, loader.snapshot()

    def test_initial_sequence_and_main_rng_match_original(self):
        torch.manual_seed(392)
        original = DataLoader(self.ds, batch_size=2, shuffle=True,
                              num_workers=4, persistent_workers=True,
                              pin_memory=False)
        try:
            seq = [ids(b) for b in original]
            rng = torch.get_rng_state().clone()
        finally:
            original._iterator._shutdown_workers()
        torch.manual_seed(392)
        observed = [ids(b) for b in self.make()]
        self.assertEqual(seq, observed)
        self.assertTrue(torch.equal(rng, torch.get_rng_state()))

    def test_original_three_epochs_and_rng(self):
        torch.manual_seed(393)
        original = DataLoader(self.ds, batch_size=2, shuffle=True,
                              num_workers=4, persistent_workers=True,
                              pin_memory=False)
        try:
            seq = [[ids(b) for b in original] for _ in range(3)]
            rng = torch.get_rng_state().clone()
        finally:
            original._iterator._shutdown_workers()
        torch.manual_seed(393)
        loader = self.make()
        observed = [[ids(b) for b in loader] for _ in range(3)]
        self.assertEqual(seq, observed)
        self.assertTrue(torch.equal(rng, torch.get_rng_state()))

    def test_mid_epoch_restore(self):
        original, state = self.snapshot()
        rng = torch.get_rng_state().clone()
        tail = []
        while True:
            try:
                tail.append(ids(next(original)))
            except StopIteration:
                break
        original.close()
        torch.set_rng_state(rng)
        restored = self.make(state)
        observed = [ids(b) for b in restored]
        self.assertEqual(tail, observed)
        self.assertTrue(torch.equal(rng, torch.get_rng_state()))

    def test_cross_epoch_restore_and_main_rng(self):
        original, state = self.snapshot(8)
        rng = torch.get_rng_state().clone()
        tail = []
        while True:
            try:
                tail.append(ids(next(original)))
            except StopIteration:
                break
        next_epochs = [[ids(b) for b in original] for _ in range(2)]
        final_rng = torch.get_rng_state().clone()
        original.close()
        torch.set_rng_state(rng)
        restored = self.make(state)
        self.assertEqual(tail, [ids(b) for b in restored])
        self.assertEqual(next_epochs, [[ids(b) for b in restored] for _ in range(2)])
        self.assertTrue(torch.equal(final_rng, torch.get_rng_state()))

    def test_prologue_consumes_two_batches(self):
        loader, state = self.snapshot(2)
        self.assertEqual(state["consumed_batches"], 2)
        self.assertEqual(state["consumed_samples"], 4)
        self.assertEqual(ids(next(loader)), state["epoch_indices"][4:6])

    def test_single_request_batch_one(self):
        loader = self.make(batch_size=1)
        it = iter(loader)
        next(it); next(it)
        state = loader.snapshot()
        self.assertEqual(state["consumed_samples"], 2)
        restored = self.make(state, batch_size=1)
        it2 = iter(restored)
        self.assertEqual(ids(next(it)), ids(next(it2)))

    def test_mapping_digest_binds_parser_and_source(self):
        self.assertNotEqual(mapping_digest([1, 2]), mapping_digest([2, 1]))
        self.assertNotEqual(mapping_digest([1], ["a"]), mapping_digest([1], ["b"]))
        self.assertEqual(mapping_digest([1], ["a"]), mapping_digest([1], ["a"]))

    def test_bad_identity_rejected(self):
        _, state = self.snapshot()
        state["dataset_digest"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "IDENTITY_MISMATCH"):
            self.make(state)

    def test_bad_permutation_rejected(self):
        _, state = self.snapshot()
        state["epoch_indices"][0] = state["epoch_indices"][1]
        with self.assertRaisesRegex(ValueError, "PERMUTATION"):
            self.make(state)

    def test_bad_cursor_rejected(self):
        _, state = self.snapshot()
        state["consumed_samples"] = 7
        with self.assertRaisesRegex(ValueError, "CURSOR"):
            self.make(state)

    def test_nondeterministic_dataset_rejected(self):
        with self.assertRaisesRegex(ValueError, "DETERMINISM"):
            self.make(deterministic_dataset=False)

    def test_workers_shutdown(self):
        loader, _ = self.snapshot()
        workers = list(loader._it._workers)
        self.assertEqual(len(workers), 4)
        loader.close()
        self.assertTrue(all(not w.is_alive() for w in workers))

    def test_restore_full_epoch_then_next_epoch(self):
        loader = self.make()
        for _ in loader:
            pass
        state = loader.snapshot()
        rng = torch.get_rng_state().clone()
        expected = [ids(b) for b in loader]
        final_rng = torch.get_rng_state().clone()
        loader.close()
        torch.set_rng_state(rng)
        restored = self.make(state)
        self.assertEqual([], [ids(b) for b in restored])
        self.assertEqual(expected, [ids(b) for b in restored])
        self.assertTrue(torch.equal(final_rng, torch.get_rng_state()))

    def test_bad_rng_rejected(self):
        _, state = self.snapshot()
        state["initial_base_seed_rng_state"] = torch.tensor([3], dtype=torch.uint8)
        with self.assertRaisesRegex(ValueError, "BASE_RNG"):
            self.make(state)


if __name__ == "__main__":
    unittest.main(verbosity=2)
