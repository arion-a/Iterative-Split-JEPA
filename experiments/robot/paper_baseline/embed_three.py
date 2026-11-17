"""Embed every image with a trained three-head encoder; save [z_S, z_P, z_L] per group (same layout as the earlier feature files).
    python embed_three.py TASK CHECKPOINT"""
import sys, os, glob, numpy as np, torch, torch.nn as nn
sys.path.insert(0, "robot")
from hl_maniskill.models import _build_backbone
from hl_maniskill.data import image_norm_params
task, ckpt = sys.argv[1], sys.argv[2]; dev = "cuda"; ck = torch.load(ckpt, map_location=dev); ds, dp, dl = ck["dims"]
class ThreeHeadEncoder(nn.Module):
    def __init__(self):
        super().__init__(); self.shared_trunk, f = _build_backbone(ck["backbone"], False); mk = lambda d: nn.Sequential(nn.Linear(f, 512), nn.ReLU(inplace=True), nn.Linear(512, d)); self.head_s, self.head_p, self.head_l = mk(ds), mk(dp), mk(dl)
    def forward(self, x): h = self.shared_trunk(x); return torch.cat([self.head_s(h), self.head_p(h), self.head_l(h)], 1)
enc = ThreeHeadEncoder().to(dev); enc.load_state_dict(ck["state_dict"]); enc.eval(); mean, std = image_norm_params(ck["image_norm"]); m = torch.tensor(mean, device=dev).view(1, 3, 1, 1); s = torch.tensor(std, device=dev).view(1, 3, 1, 1)
out = "data/robot_split3"; os.makedirs(f"{out}/feat/{task}", exist_ok=True); os.makedirs(f"{out}/{task}", exist_ok=True)
with torch.no_grad():
    for f in sorted(glob.glob(f"data/robot/{task}/group_*.npz")):
        d = np.load(f); img = torch.from_numpy(d["images"]).reshape(-1, 128, 128, 3).to(dev).permute(0, 3, 1, 2).float() / 255.0
        z = torch.cat([enc((img[i:i + 240] - m) / s).float().cpu() for i in range(0, len(img), 240)]).reshape(*d["images"].shape[:3], -1).numpy()
        b = os.path.basename(f)[:-4]; np.save(f"{out}/feat/{task}/{b}.npy", z); np.savez(f"{out}/{task}/{b}.npz", state=d["state"])
print("embedded", task, "dims", ck["dims"])
