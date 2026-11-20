"""E62 details for the report: the autoencoder, the whitening matrix W_wh = C^-1/2 (48 x 48) and how nonlinearly the factors sit in the 48 numbers
(linear against small-network read-out of each factor group). Needs data/e62 (ae.pt, pairs_k*.npz, probe.npz) and results/e62/blocks.pt.
    PYTHONPATH=src python experiments/factors/e62_details.py   -> results/e62/e62_details.json"""
import sys, json, numpy as np, torch
sys.path.insert(0, 'src'); sys.path.insert(0, 'experiments/factors')
from train_ae import AE
from isj.engine import fit_whitener
from isj import audits
torch.set_num_threads(4)
ck = torch.load('data/e62/ae.pt'); ae = AE(); ae.load_state_dict(ck['state']); ae.eval()
print('ae steps', ck['steps'], 'final loss', ck['log'][-1], 'n log', len(ck['log']))
n_enc = sum(p.numel() for p in ae.enc.parameters()); n_all = sum(p.numel() for p in ae.parameters()); print('params encoder', n_enc, 'all', n_all)
for name, m in ae.enc.named_children(): print(name, m)
def enc(x):
    with torch.no_grad(): return torch.cat([ae.encode(torch.from_numpy(x[i:i+500]).permute(0,3,1,2).float()/255) for i in range(0, len(x), 500)]).double()
Zu = []
for k in range(1, 9): Zu.append(enc(np.load(f'data/e62/pairs_k{k}.npz')['u']))
Z = torch.cat(Zu); print('whitening set', Z.shape)
wh = fit_whitener(Z.float(), 1e-5)
saved = torch.load('results/e62/blocks.pt'); M = saved['matrix']; print('saved matrix', M.shape, 'diff to recomputed', float((M - wh.matrix).abs().max()), 'mean diff', float((saved['mean'] - wh.mean).abs().max()))
C = torch.cov(Z.T); ev = torch.linalg.eigvalsh(C).flip(0)
print('eig C: max', float(ev[0]), 'min', float(ev[-1]), 'cond', float(ev[0]/ev[-1]), 'n<1e-5', int((ev < 1e-5).sum()))
print('eig C all', [float(f'{x:.3g}') for x in ev.tolist()])
Wm = M.double(); print('W_wh symmetric?', float((Wm - Wm.T).abs().max()), 'W C W - I max', float((Wm @ C @ Wm - torch.eye(48, dtype=torch.double)).abs().max()))
sv = torch.linalg.svdvals(Wm); print('W_wh singular values max/min', float(sv[0]), float(sv[-1]))
# bend: linear vs nonlinear read of each factor group from the latent
P = np.load('data/e62/probe.npz'); Zp = enc(P['x']); F = torch.from_numpy(P['f']).double(); ntr = 6000
Ft = (F - F[:ntr].mean(0)) / F[:ntr].std(0); SIZES = [1,2,1,2,3,2,1,2,1]; OFF = np.cumsum([0]+SIZES)
lin, mlp = [], []
for g in range(9):
    cols = list(range(OFF[g], OFF[g+1]))
    lin.append(float(np.mean([audits.linear_r2(Zp[:ntr], Ft[:ntr,[c]], Zp[ntr:], Ft[ntr:,[c]]) for c in cols])))
    mlp.append(float(np.mean([audits.mlp_r2(Zp[:ntr].float(), Ft[:ntr,[c]].float(), Zp[ntr:].float(), Ft[ntr:,[c]].float()) for c in cols])))
print('linear R2', [round(x,2) for x in lin]); print('mlp R2   ', [round(x,2) for x in mlp])
r = json.load(open('results/e62/e62.json')); print('stored full_latent_R2', [round(x,2) for x in r['full_latent_R2']])
json.dump({'ae_steps': ck['steps'], 'ae_final_loss': ck['log'][-1][1], 'params_encoder': n_enc, 'params_all': n_all, 'eigC': ev.tolist(), 'linear_r2': lin, 'mlp_r2': mlp,
           'wh_match_max_abs': float((M - wh.matrix).abs().max()), 'sv_max': float(sv[0]), 'sv_min': float(sv[-1])}, open('results/e62/e62_details.json', 'w'))
