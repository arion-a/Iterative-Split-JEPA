"""Render one 'video': 48 frames in which the six recovered factors all vary at once, each with its own rhythm. Run with the ManiSkill venv.
    python gen_clip.py OUT.npz"""
import sys, numpy as np
from gen_factors import work, LO, HI
T = 48; mid = (LO + HI) / 2; amp = 0.8 * (HI - LO) / 2; tau = np.arange(T) / T
F = np.tile(mid, (T, 1)); w = lambda cyc, ph=0: np.sin(2 * np.pi * (cyc * tau + ph))
F[:, 3] = 0.0                                                    # cube yaw held fixed (not a recovered factor)
F[:, 4] = mid[4] + amp[4] * w(4);       F[:, 5] = mid[5] + amp[5] * w(4, .27)           # cube position, 4 cycles
for j, i in enumerate((6, 7, 8)): F[:, i] = mid[i] + amp[i] * w(3, j / 3)               # cube colour, 3 cycles
for j, i in enumerate((9, 10)): F[:, i] = mid[i] + amp[i] * w(2, j / 4)                 # light tint, 2 cycles
F[:, 11] = mid[11] + amp[11] * w(2, .1)                                                 # brightness, 2 cycles
F[:, 12] = mid[12] + amp[12] * w(1); F[:, 13] = mid[13] + amp[13] * w(1, .25)           # camera distance / elevation, 1 cycle
F[:, 14] = mid[14] + amp[14] * w(1, .6)                                                 # camera azimuth, 1 cycle
X = work(F); np.savez(sys.argv[1], x=X, f=F); print(X.shape)
