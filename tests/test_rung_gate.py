"""Gap 2: a rung that fails the gap criterion is not applied (nothing removed); a rung that passes is applied exactly as before."""
import torch

from isj.audits import max_angle_deg
from isj.engine import fit_ladder

D, N = 6, 20000
U = torch.linalg.qr(torch.randn(D, D, generator=torch.Generator().manual_seed(0)))[0]       # fixed rotation; block b = coordinates 2b..2b+1


def pairs(first_block_visible):
    g = torch.Generator().manual_seed(1)

    def fn(k):
        z = torch.randn(N, D, generator=g); w = z.clone()
        for j in range(1, k + 1):
            if j == 1 and not first_block_visible:      # block 1 absent from the representation: its coordinates stay equal
                continue
            w[:, 2 * (j - 1): 2 * j] = torch.randn(N, 2, generator=g)
        return z @ U + 0.01 * torch.randn(N, D, generator=g), w @ U + 0.01 * torch.randn(N, D, generator=g)
    return fn


def test_failed_rung_is_not_applied_and_the_next_rung_is_spared():
    image2 = U[2:4, :].T
    on = fit_ladder(pairs(False), D, d_ks=[2, 2], gate_gap_ratio=10.0)
    off = fit_ladder(pairs(False), D, d_ks=[2, 2])
    assert not on[0].applied and on[1].applied and on[1].H_prev.shape[1] == D        # nothing removed after the failed rung
    assert max_angle_deg(on[1].V, image2) < 2.0 < max_angle_deg(off[1].V, image2)       # without the gate the failed rung damages rung 2


def test_passing_rungs_are_unchanged_by_the_gate():
    on = fit_ladder(pairs(True), D, d_ks=[2, 2], gate_gap_ratio=10.0)
    off = fit_ladder(pairs(True), D, d_ks=[2, 2])
    assert all(r.applied for r in on) and all(torch.allclose(a.V, b.V) and torch.allclose(a.Q, b.Q) for a, b in zip(on, off))
