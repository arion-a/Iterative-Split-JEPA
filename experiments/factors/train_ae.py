"""E62 encoder: convolutional autoencoder (latent 48), reconstruction loss only, trained without labels on the generated pair images.
    python train_ae.py DATA_DIR OUT_PT [MINUTES]"""
import sys, time, glob, numpy as np, torch, torch.nn as nn
torch.set_num_threads(4); torch.manual_seed(0)
class AE(nn.Module):
    def __init__(s, z=48):
        super().__init__(); c = lambda i, o: nn.Sequential(nn.Conv2d(i, o, 4, 2, 1), nn.GELU())
        s.enc = nn.Sequential(c(3, 32), c(32, 64), c(64, 128), c(128, 128), nn.Flatten(), nn.Linear(128 * 36, z))
        s.fc = nn.Linear(z, 128 * 36); d = lambda i, o: nn.Sequential(nn.ConvTranspose2d(i, o, 4, 2, 1), nn.GELU())
        s.dec = nn.Sequential(d(128, 128), d(128, 64), d(64, 32), nn.ConvTranspose2d(32, 3, 4, 2, 1), nn.Sigmoid())
    def encode(s, x): return s.enc(x)
    def decode(s, z): return s.dec(s.fc(z).view(-1, 128, 6, 6))
if __name__ == "__main__":
    data, out, minutes = sys.argv[1], sys.argv[2], float(sys.argv[3]) if len(sys.argv) > 3 else 25
    X = np.concatenate([np.load(f)[k] for f in sorted(glob.glob(f"{data}/pairs_k*.npz")) for k in ("u", "v")]); print("images", X.shape, flush=True)
    X = torch.from_numpy(X).permute(0, 3, 1, 2).contiguous(); m = AE(); opt = torch.optim.Adam(m.parameters(), 1e-3); t0 = time.time(); step = 0; log = []
    while time.time() - t0 < minutes * 60:
        idx = torch.randint(0, len(X), (128,)); x = X[idx].float() / 255
        loss = (m.decode(m.encode(x)) - x).square().mean(); opt.zero_grad(); loss.backward(); opt.step(); step += 1
        if step % 200 == 0: log.append((step, float(loss))); print(step, round(float(loss), 5), round(time.time() - t0), "s", flush=True)
    torch.save({"state": m.state_dict(), "log": log, "steps": step}, out)
