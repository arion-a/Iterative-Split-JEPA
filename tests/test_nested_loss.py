"""E68/E69/E71 code checks (docs/PLAN_NESTED_LOSS_STEPS.md, tests T1, T2, T5)."""
import torch
from isj.encoder import EncoderConfig, train_encoder
from isj.stage_b1 import invariance_residual, slice_measures
from isj.worlds import BlockWorld, CouplingMap


class CountWorld(BlockWorld):
    calls: list = []
    def correspondence_pairs(self, n, k, rank=None):
        CountWorld.calls.append(k); return super().correspondence_pairs(n, k, rank)


def _train(schedule):
    CountWorld.calls = []; w = CountWorld([4, 4, 4, 4], [0.2, 0.5, 0.75, 0.95], seed=1); obs = CouplingMap(w.d, 4, 0.5, 16, seed=1)
    cfg = EncoderConfig(in_dim=16, latent_dim=16, hidden=16, steps=5, batch_size=32, corr_inv_weight=1.0, corr_inv_schedule=schedule)
    train_encoder(w, obs, cfg, 0); return set(CountWorld.calls)


def test_T1_schedule_gates_the_families():
    assert _train(None) == {1, 2, 3}                 # all on from step 0
    assert _train((0, 100, 100)) == {1}              # families 2 and 3 not yet on in the first 5 steps
    assert _train((0, 3, 100)) == {1, 2}             # family 2 switches on at step 3


def test_T2_slice_measures_on_known_embeddings():
    g = torch.Generator().manual_seed(0); z = torch.randn(3000, 12, generator=g); sl = [slice(0, 4), slice(4, 8), slice(8, 12)]
    m = slice_measures(z[:2000], z[2000:], z[:2000], z[2000:], sl)                   # h = z: every slice holds exactly its own layer
    assert min(m["presence"]) > 0.9 and max(m["leakage_faster"]) < 0.1
    noise = torch.randn(3000, 12, generator=g); n = slice_measures(noise[:2000], noise[2000:], z[:2000], z[2000:], sl)   # h unrelated to z
    assert max(n["presence"]) < 0.2


def test_T5_invariance_residual():
    w = BlockWorld([4, 4, 4], [0.2, 0.5, 0.9], seed=2); u, v = w.correspondence_pairs(4000, 1)        # h = z: the tail (blocks 2, 3) is shared
    assert invariance_residual(u, v, 4) < 1e-9
    a, b = w.sample(4000), w.sample(4000)                                                              # independent samples: about 2
    assert 1.8 < invariance_residual(a, b, 4) < 2.2
