"""E72 rate estimator (src/isj/stage_b1.rho_hat): lag-1 correlation per slice recovers the speed of known AR(1) blocks."""
import torch
from isj.stage_b1 import rho_hat
from isj.worlds import BlockWorld

RHOS = [0.3, 0.7, 0.9, 0.96]

def _pairs(n=200_000, seed=0):
    w = BlockWorld([4, 4, 4, 4], RHOS, seed=seed)
    return w, *w.transition_pairs(n)

def test_identity_recovers_speeds():
    w, z1, z2 = _pairs()
    est = rho_hat(z1, z2, [w.block_slice(b) for b in range(1, 5)])
    for e, r in zip(est, RHOS): assert abs(e - r) < 0.01, (est, RHOS)

def test_rotation_inside_slice_and_scaling_do_not_matter():
    w, z1, z2 = _pairs(seed=1)
    g = torch.Generator().manual_seed(5)
    qb = torch.block_diag(*[torch.linalg.qr(torch.randn(4, 4, generator=g))[0] for _ in range(4)])
    est = rho_hat(3.0 * z1 @ qb + 1.0, 3.0 * z2 @ qb + 1.0, [w.block_slice(b) for b in range(1, 5)])
    for e, r in zip(est, RHOS): assert abs(e - r) < 0.01, (est, RHOS)

def test_pairs_without_time_link_give_zero():
    w, z1, z2 = _pairs(seed=2)
    est = rho_hat(z1, z2[torch.randperm(len(z2))], [w.block_slice(b) for b in range(1, 5)])
    assert all(abs(e) < 0.01 for e in est), est

def test_order_is_preserved_by_a_monotone_nonlinear_map():
    w, z1, z2 = _pairs(seed=3)
    est = rho_hat(torch.tanh(0.5 * z1), torch.tanh(0.5 * z2), [w.block_slice(b) for b in range(1, 5)])
    assert est == sorted(est), est                                          # (values shift slightly under a nonlinear map; the order of the speeds stays)
