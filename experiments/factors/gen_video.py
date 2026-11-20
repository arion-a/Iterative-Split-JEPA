"""E75 data: render videos of the E62 scene whose 9 factor groups follow AR(1) chains with different speeds (registered in docs/EVIDENCE.md).
Run with the ManiSkill venv (software Vulkan):  VK_ICD_FILENAMES=/usr/share/vulkan/icd.d/lvp_icd.json python gen_video.py OUTDIR [N_VIDEOS=500] [T=40] [PROCS]
Group b (1 = gripper, fastest ... 9 = camera azimuth, slowest) moves by u_t+1 = rho_b u_t + sqrt(1 - rho_b^2) eps, rho_b = 1 - geomspace(0.8, 0.04, 9)_b = 0.2 ... 0.96;
the factor values are LO + Phi(u) (HI - LO) (Phi = the normal cumulative distribution), i.e. uniform in the E62 ranges at every time. -> OUTDIR/videos_<i>.npz: x (n, T, 96, 96, 3) uint8, f (n, T, 15)."""
import sys, os, math, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_factors as G
from multiprocessing import Pool
RHO = 1 - np.geomspace(0.8, 0.04, 9)
def ndtr(u): return 0.5 * (1 + np.vectorize(math.erf)(u / math.sqrt(2)))
def factor_video(rng, T):
    f = np.zeros((T, G.NF))
    for b in range(9):
        k = G.SIZES[b]; u = rng.randn(k); lo, hi = G.OFF[b], G.OFF[b + 1]
        for t in range(T):
            f[t, lo:hi] = G.LO[lo:hi] + ndtr(u) * (G.HI[lo:hi] - G.LO[lo:hi]); u = RHO[b] * u + math.sqrt(1 - RHO[b] ** 2) * rng.randn(k)
    return f
def shard(args):
    i, n, T, seed, out = args; rng = np.random.RandomState(seed * 1000 + i); F = np.stack([factor_video(rng, T) for _ in range(n)])
    X = np.stack([np.stack([G.render(f) for f in fv]) for fv in F]); np.savez(f"{out}/videos_{i}.npz", x=X, f=F); return i
if __name__ == "__main__":
    out = sys.argv[1]; V = int(sys.argv[2]) if len(sys.argv) > 2 else 500; T = int(sys.argv[3]) if len(sys.argv) > 3 else 40; P = int(sys.argv[4]) if len(sys.argv) > 4 else os.cpu_count()
    os.makedirs(out, exist_ok=True); per = 5; jobs = [(i, per, T, 7, out) for i in range(V // per) if not os.path.exists(f"{out}/videos_{i}.npz")]
    with Pool(min(P, len(jobs))) as pool:
        for n, i in enumerate(pool.imap_unordered(shard, jobs)): print("shard", i, f"{n + 1}/{len(jobs)}", flush=True)
