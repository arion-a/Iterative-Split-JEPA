"""Reconstruction-free encoder training: predictive loss + collapse regulariser (monograph §9, Step 1)."""

from __future__ import annotations

import math
from dataclasses import dataclass

import torch
import torch.nn.functional as F
from torch import nn

from .worlds import BlockWorld, CouplingMap


def mlp(i: int, h: int, o: int) -> nn.Sequential:
    return nn.Sequential(nn.Linear(i, h), nn.GELU(), nn.Linear(h, h), nn.GELU(), nn.Linear(h, o))


class SIGReg(nn.Module):
    """Sliced characteristic-function regulariser toward N(0, I) (LeJEPA), reimplemented."""

    def __init__(self, knots: int = 17, slices: int = 128, t_max: float = 3.0):
        super().__init__()
        self.slices = slices
        t = torch.linspace(0.0, t_max, knots)
        dt = t_max / (knots - 1)
        quad = torch.full((knots,), 2.0 * dt)
        quad[[0, -1]] = dt
        self.register_buffer("t", t)
        self.register_buffer("target", torch.exp(-0.5 * t.square()))
        self.register_buffer("weights", quad * torch.exp(-0.5 * t.square()))

    def forward(self, h: torch.Tensor) -> torch.Tensor:
        dirs = F.normalize(torch.randn(h.shape[1], self.slices, device=h.device), dim=0)
        proj = (h @ dirs).unsqueeze(-1) * self.t
        err = (proj.cos().mean(0) - self.target).square() + proj.sin().mean(0).square()
        return (err @ self.weights).mean() * len(h)


class InverseCouplingEncoder(nn.Module):
    """Mirror-style encoder: the same alternating coupling layers as the observation map, run in
    reverse and subtracting, with learned weights. Only valid when the observation has the same
    dimension as the hidden state (no lift). Reimplemented from the paper's description.
    """

    def __init__(self, d: int, layers: int):
        super().__init__()
        self.half = d // 2
        right = d - self.half
        shapes = [(self.half, right) if i % 2 == 0 else (right, self.half) for i in range(layers)]
        self.weights = nn.ParameterList(nn.Parameter(torch.randn(*sh) / math.sqrt(sh[0])) for sh in shapes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        h = x
        for i in reversed(range(len(self.weights))):
            left, right = h[:, : self.half], h[:, self.half:]
            if i % 2 == 0:
                right = right - torch.tanh(left @ self.weights[i])
            else:
                left = left - torch.tanh(right @ self.weights[i])
            h = torch.cat([left, right], dim=1)
        return h


def variance_hinge(h: torch.Tensor, gamma: float = 1.0) -> torch.Tensor:
    """L_var = sum_j max(0, gamma - std(h_j)) (monograph eq. 11)."""
    return F.relu(gamma - torch.sqrt(h.var(0) + 1e-4)).sum()


def covariance_penalty(h: torch.Tensor) -> torch.Tensor:
    h = h - h.mean(0)
    c = h.T @ h / (len(h) - 1)
    off = c - torch.diag(torch.diag(c))
    return off.square().sum() / h.shape[1]


@dataclass
class EncoderConfig:
    in_dim: int
    latent_dim: int
    hidden: int = 64
    steps: int = 8000
    batch_size: int = 256
    lr: float = 3e-3
    reg: str = "hinge"            # "hinge" | "sigreg" | "none"
    var_weight: float = 1e-2
    cov_weight: float = 0.0
    sigreg_weight: float = 1e-6
    pred_weight: float = 1.0
    stop_grad: bool = True        # stop-gradient on the prediction target
    log_every: int = 1000
    arch: str = "mlp"             # "mlp" | "inverse_coupling" (mirror-style, needs obs_dim == d)
    objective: str = "predict"    # "predict" (predictor + regulariser) | "lejepa" (alignment + SIGReg)
    coupling_layers: int = 4


def train_encoder(world: BlockWorld, observe: CouplingMap, cfg: EncoderConfig,
                  seed: int, verbose: bool = False) -> tuple[nn.Module, list[dict]]:
    """Train g (encoder) and f (predictor) on stationary transition pairs; return frozen g."""
    torch.manual_seed(seed)
    if cfg.arch == "inverse_coupling":
        assert cfg.in_dim == cfg.latent_dim, "mirror-style encoder needs obs_dim == d"
        enc = InverseCouplingEncoder(cfg.latent_dim, cfg.coupling_layers)
    else:
        enc = mlp(cfg.in_dim, cfg.hidden, cfg.latent_dim)
    pred = mlp(cfg.latent_dim, cfg.hidden, cfg.latent_dim)
    sig = SIGReg()
    params = list(enc.parameters()) + (list(pred.parameters()) if cfg.objective == "predict" else [])
    opt = torch.optim.AdamW(params, lr=cfg.lr)
    half = max(cfg.steps // 2, 1)
    log = []
    for step in range(cfg.steps):
        # constant lr for the first half, cosine decay in the second (as in the reference recipe)
        prog = max(step - half, 0) / max(cfg.steps - half, 1)
        lr = cfg.lr if step < half else cfg.lr * (1 + math.cos(math.pi * prog)) / 2
        for g in opt.param_groups:
            g["lr"] = lr
        z1, z2 = world.transition_pairs(cfg.batch_size)
        h = enc(observe(torch.cat([z1, z2])))
        h1, h2 = h[: cfg.batch_size], h[cfg.batch_size:]
        if cfg.objective == "lejepa":   # paper: pull both views to their mean + SIGReg, no predictor
            views = h.reshape(2, cfg.batch_size, -1)
            l_pred = (views.mean(0) - views).square().mean()
            l_reg = cfg.sigreg_weight * sig(h)
            loss = (1 - cfg.sigreg_weight) * cfg.pred_weight * l_pred + l_reg
            opt.zero_grad()
            loss.backward()
            opt.step()
            if step % cfg.log_every == 0 or step == cfg.steps - 1:
                log.append({"step": step, "pred": float(l_pred.detach()), "reg": float(l_reg.detach()),
                            "min_std": float(h.std(0).min())})
            continue
        l_pred = F.mse_loss(pred(h1), h2.detach() if cfg.stop_grad else h2)
        loss = cfg.pred_weight * l_pred
        l_reg = torch.zeros(())
        if cfg.reg == "hinge":
            l_reg = cfg.var_weight * variance_hinge(h) + cfg.cov_weight * covariance_penalty(h)
        elif cfg.reg == "sigreg":
            l_reg = cfg.sigreg_weight * sig(h)
        loss = loss + l_reg
        opt.zero_grad()
        loss.backward()
        opt.step()
        if step % cfg.log_every == 0 or step == cfg.steps - 1:
            rec = {"step": step, "pred": float(l_pred.detach()), "reg": float(l_reg.detach()),
                   "min_std": float(h.std(0).min())}
            log.append(rec)
            if verbose:
                print(rec, flush=True)
    enc.eval()
    for p in enc.parameters():
        p.requires_grad_(False)
    return enc, log


@torch.no_grad()
def encode(enc: nn.Module, observe: CouplingMap, z: torch.Tensor, chunk: int = 10_000) -> torch.Tensor:
    return torch.cat([enc(observe(z[i: i + chunk])) for i in range(0, len(z), chunk)])
