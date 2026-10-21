"""Presence probe: a nonlinear readout finds structure a linear one misses, and reads noise as absent."""
import torch

from isj.audits import linear_r2, mlp_r2


def test_mlp_probe_finds_nonlinear_content_and_rejects_noise():
    g = torch.Generator().manual_seed(0)
    x = torch.randn(8000, 8, generator=g)
    y = torch.stack([torch.sin(2 * x[:, 0]) + x[:, 1] ** 2, x[:, 2] * x[:, 3]], 1)
    tr, te = slice(0, 6000), slice(6000, 8000)
    assert linear_r2(x[tr], y[tr], x[te], y[te]) < 0.5
    assert mlp_r2(x[tr], y[tr], x[te], y[te]) > 0.8
    noise = torch.randn(8000, 2, generator=g)
    assert abs(mlp_r2(x[tr], noise[tr], x[te], noise[te])) < 0.05
