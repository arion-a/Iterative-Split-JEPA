"""E73 block-speed estimator (src/isj/stage_b1.block_rho_hat) on known AR(1) layers."""
import torch
from isj.stage_b1 import block_rho_hat
from isj.worlds import BlockWorld
RHOS = [0.2, 0.7, 0.95]
def _pairs(seed=0):
    w = BlockWorld([4, 4, 4], RHOS, seed=seed); return w.transition_pairs(200_000)
def test_identity_bases_recover_speeds():
    z1, z2 = _pairs(); eye = torch.eye(12)
    est = block_rho_hat(z1, z2, [eye[:, 0:4], eye[:, 4:8], eye[:, 8:12]])
    for e, r in zip(est, RHOS): assert abs(e - r) < 0.01, (est, RHOS)
def test_rotated_basis_inside_a_block_does_not_matter():
    z1, z2 = _pairs(1); g = torch.Generator().manual_seed(3)
    qs = [torch.linalg.qr(torch.randn(4, 4, generator=g))[0] for _ in range(3)]
    eye = torch.eye(12); bases = [eye[:, 4 * i:4 * i + 4] @ qs[i] for i in range(3)]
    est = block_rho_hat(z1, z2, bases)
    for e, r in zip(est, RHOS): assert abs(e - r) < 0.01, (est, RHOS)
def test_wrong_block_gives_a_mixture():
    z1, z2 = _pairs(2); eye = torch.eye(12)
    mixed = torch.cat([eye[:, 0:2], eye[:, 8:10]], dim=1)       # two texture directions and two category directions
    est = block_rho_hat(z1, z2, [mixed])[0]
    assert abs(est - (0.2 + 0.95) / 2) < 0.02, est               # a block that mixes layers reads the average speed
