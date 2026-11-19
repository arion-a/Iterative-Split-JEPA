"""D9 nesting enforcement: hard projection puts rung 2 inside rung 1's invariant content; soft reproduces hard as lambda grows."""
import torch

from isj.audits import max_angle_deg, rank_monitor
from isj.engine import fit_ladder, fit_rung
from isj.worlds import BlockWorld, LinearRepresentation


def world3(seed=0, noise=0.1):
    w = BlockWorld([2, 2, 2], [0.2, 0.7, 0.95], seed=seed)
    return w, LinearRepresentation(w, seed=seed, noise=noise)


def ladder(w, rep, budgets, mode="hard", lam=100.0):
    def pairs_fn(k, n):
        u, v = w.correspondence_pairs(n, k)
        return rep(u), rep(v)
    return fit_ladder(pairs_fn, w.d, d_ks=[2, 2], pair_budgets=budgets, nesting_enforcement=mode, soft_lambda=lam)


def true_h1(rep):
    return torch.cat([rep.true_block(2), rep.true_block(3)], 1)


def test_hard_nesting_below_half_degree_and_exactly_inside():
    w, rep = world3()
    r1, r2 = ladder(w, rep, [120_000, 30_000])
    nest = max_angle_deg(r2.V, true_h1(rep))
    print(f"\nhard nesting angle vs true rung-1 subspace: {nest:.3f} deg (budgets {r1.n_pairs}/{r2.n_pairs})")
    assert nest < 0.5
    leak_out = (torch.eye(w.d) - r1.Q @ r1.Q.T) @ r2.V          # estimated V lies in estimated H1 exactly
    assert float(leak_out.norm()) < 1e-5
    assert float((r2.V.T @ r2.V - torch.eye(2)).abs().max()) < 1e-5


def test_hard_beats_none_and_per_rung_budgets_are_used():
    w, rep = world3()
    hard = ladder(w, rep, [60_000, 20_000])
    none = ladder(w, rep, [60_000, 20_000], mode="none")
    assert (hard[0].n_pairs, hard[1].n_pairs) == (60_000, 20_000)
    assert max_angle_deg(hard[1].V, true_h1(rep)) < max_angle_deg(none[1].V, true_h1(rep))


def test_soft_with_large_lambda_reproduces_hard():
    w, rep = world3()
    u1, v1 = w.correspondence_pairs(30_000, 1)
    u2, v2 = w.correspondence_pairs(30_000, 2)
    r1 = fit_rung(rep(u1), rep(v1), torch.eye(w.d), k=1, d_k=2)
    args = (rep(u2), rep(v2), r1.Q)
    hard = fit_rung(*args, k=2, d_k=2, nesting_enforcement="hard")
    for lam, tol in [(1_000.0, 0.1), (10_000.0, 0.01)]:       # same pairs: only the enforcement differs
        soft = fit_rung(*args, k=2, d_k=2, nesting_enforcement="soft", soft_lambda=lam)
        gap = max_angle_deg(soft.V, hard.V)
        print(f"\nsoft(lambda={lam:g}) vs hard on identical pairs: {gap:.5f} deg")
        assert gap < tol


def test_rank_monitor_passes_then_fails_on_rank_one_variation():
    w, rep = world3()
    ok = ladder(w, rep, [30_000, 30_000])
    assert all(rank_monitor(r)["pass"] for r in ok)

    def pairs_fn(k, n):
        u, v = w.correspondence_pairs(n, k, rank=1 if k == 2 else None)
        return rep(u), rep(v)
    bad = fit_ladder(pairs_fn, w.d, d_ks=[2, 2], pair_budgets=[30_000, 30_000])
    assert rank_monitor(bad[0])["pass"] and not rank_monitor(bad[1])["pass"]
