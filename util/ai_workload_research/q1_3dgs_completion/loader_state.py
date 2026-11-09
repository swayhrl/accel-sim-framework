"""CPU-owned deterministic Dataset loader checkpoint support.

The initial loader preserves the installed RandomSampler and DataLoader global
RNG consumption. Materializing RandomSampler's local-generator permutation does
not consume extra global RNG. Restore replays only unconsumed deterministic
samples. Worker Python/NumPy RNG state is NOT captured: deterministic __getitem__
is a mandatory, independently source-verified prerequisite.
"""
import hashlib
import json
import torch
from torch.utils.data import DataLoader, RandomSampler, Sampler

SCHEMA = "q1-deterministic-loader-v1"


def mapping_digest(indices, image_names=None):
    """Hash Dataset item -> parser index -> optional source-name identity."""
    if hasattr(indices, "tolist"):
        indices = indices.tolist()
    payload = {"indices": [int(x) for x in indices]}
    if image_names is not None:
        payload["image_names"] = [str(x) for x in image_names]
    return hashlib.sha256(json.dumps(payload, sort_keys=True,
                                    separators=(",", ":")).encode()).hexdigest()


class _RecordingSampler(Sampler):
    def __init__(self, owner):
        self.owner = owner

    def __len__(self):
        return len(self.owner.dataset)

    def __iter__(self):
        owner = self.owner
        if owner._resume_pending:
            owner._resume_pending = False
            start = owner.consumed_samples
        else:
            # Execute lazily at the same point at which DataLoader's first
            # prefetch obtains its first index. Original RandomSampler consumes
            # one seed from the main CPU RNG and uses its private generator.
            owner.epoch_indices = list(iter(RandomSampler(owner.dataset)))
            owner.epoch += 1
            owner.consumed_samples = 0
            owner.consumed_batches = 0
            start = 0
        yield from owner.epoch_indices[start:]


class StatefulLoader:
    def __init__(self, dataset, *, dataset_digest, deterministic_dataset,
                 batch_size=1, num_workers=4, pin_memory=True,
                 persistent_workers=True, restore_state=None):
        if deterministic_dataset is not True:
            raise ValueError("DATASET_DETERMINISM_NOT_QUALIFIED")
        if not isinstance(dataset_digest, str) or len(dataset_digest) != 64:
            raise ValueError("INVALID_DATASET_DIGEST")
        if len(dataset) < 1 or batch_size < 1:
            raise ValueError("INVALID_LOADER_SHAPE")
        if num_workers < 0 or (persistent_workers and num_workers == 0):
            raise ValueError("INVALID_WORKER_CONFIG")
        self.dataset = dataset
        self.dataset_digest = dataset_digest
        self.batch_size = int(batch_size)
        self.num_workers = int(num_workers)
        self.pin_memory = bool(pin_memory)
        self.persistent_workers = bool(persistent_workers)
        self.epoch_indices = None
        self.epoch = -1
        self.consumed_samples = 0
        self.consumed_batches = 0
        self._resume_pending = False
        self._it = None
        self._base_rng_state = None
        self._restored_base_seed = None
        generator = None
        if restore_state is not None:
            self._validate(restore_state)
            self.epoch_indices = list(restore_state["epoch_indices"])
            self.epoch = int(restore_state["epoch"])
            self.consumed_samples = int(restore_state["consumed_samples"])
            self.consumed_batches = int(restore_state["consumed_batches"])
            self._base_rng_state = restore_state["initial_base_seed_rng_state"].clone()
            self._restored_base_seed = int(restore_state["base_seed"])
            self._resume_pending = True
            # Explicit sampler keeps this generator out of RandomSampler.
            # Only the fresh DataLoader base-seed draw uses it, avoiding an
            # extra draw from checkpoint's main CPU RNG.
            generator = torch.Generator()
            generator.set_state(self._base_rng_state)
        self._loader = DataLoader(
            dataset, batch_size=self.batch_size,
            sampler=_RecordingSampler(self), shuffle=False,
            num_workers=self.num_workers, pin_memory=self.pin_memory,
            persistent_workers=self.persistent_workers, generator=generator)

    def _validate(self, state):
        expected = {"schema": SCHEMA, "dataset_digest": self.dataset_digest,
                    "dataset_length": len(self.dataset),
                    "batch_size": self.batch_size,
                    "num_workers": self.num_workers,
                    "pin_memory": self.pin_memory,
                    "persistent_workers": self.persistent_workers,
                    "deterministic_dataset_required": True}
        for key, value in expected.items():
            if state.get(key) != value:
                raise ValueError("LOADER_STATE_IDENTITY_MISMATCH:" + key)
        permutation = state.get("epoch_indices")
        if not isinstance(permutation, list) or any(
            type(i) is not int for i in permutation
        ) or sorted(permutation) != list(range(len(self.dataset))):
            raise ValueError("INVALID_EPOCH_PERMUTATION")
        count = state.get("consumed_samples")
        batches = state.get("consumed_batches")
        epoch = state.get("epoch")
        if (type(count) is not int or not 0 <= count <= len(self.dataset)
            or type(batches) is not int or batches < 0
            or count != min(batches * self.batch_size, len(self.dataset))
            or batches > (len(self.dataset) + self.batch_size - 1) // self.batch_size
            or type(epoch) is not int or epoch < 0):
            raise ValueError("INVALID_CONSUMER_CURSOR")
        rng = state.get("initial_base_seed_rng_state")
        if (not isinstance(rng, torch.Tensor) or rng.dtype != torch.uint8
            or rng.device.type != "cpu" or rng.ndim != 1):
            raise ValueError("INVALID_BASE_RNG_STATE")
        try:
            torch.Generator().set_state(rng)
        except Exception as exc:
            raise ValueError("INVALID_BASE_RNG_STATE") from exc
        if type(state.get("base_seed")) is not int:
            raise ValueError("INVALID_BASE_SEED")

    def __len__(self):
        return (len(self.dataset) + self.batch_size - 1) // self.batch_size

    def __iter__(self):
        if self._base_rng_state is None:
            self._base_rng_state = torch.get_rng_state().clone()
        self._it = iter(self._loader)
        if self._restored_base_seed is not None:
            if int(self._it._base_seed) != self._restored_base_seed:
                raise RuntimeError("RESTORED_WORKER_BASE_SEED_MISMATCH")
            self._restored_base_seed = None
        return self

    def __next__(self):
        if self._it is None:
            raise RuntimeError("LOADER_ITERATOR_NOT_STARTED")
        item = next(self._it)
        self.consumed_samples = min(
            self.consumed_samples + self.batch_size, len(self.dataset))
        self.consumed_batches += 1
        return item

    def snapshot(self):
        if self._it is None or self.epoch_indices is None:
            raise RuntimeError("LOADER_NO_ACTIVE_EPOCH")
        return {
            "schema": SCHEMA, "dataset_digest": self.dataset_digest,
            "dataset_length": len(self.dataset), "batch_size": self.batch_size,
            "num_workers": self.num_workers, "pin_memory": self.pin_memory,
            "persistent_workers": self.persistent_workers,
            "deterministic_dataset_required": True,
            "epoch": self.epoch, "epoch_indices": list(self.epoch_indices),
            "consumed_samples": self.consumed_samples,
            "consumed_batches": self.consumed_batches,
            "base_seed": int(self._it._base_seed),
            "initial_base_seed_rng_state": self._base_rng_state.clone(),
            "worker_rng_scope": "NOT_CAPTURED_DETERMINISTIC_GETITEM_REQUIRED",
            "pending_prefetch": "RECONSTRUCT_FROM_UNCONSUMED_EPOCH_INDICES",
        }

    def close(self):
        iterator = self._it
        try:
            if iterator is not None and hasattr(iterator, "_shutdown_workers"):
                iterator._shutdown_workers()
        finally:
            self._it = None
            self._loader._iterator = None
