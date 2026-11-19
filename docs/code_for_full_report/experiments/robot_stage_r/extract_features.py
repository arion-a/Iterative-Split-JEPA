"""Frozen ImageNet-initialized ResNet-50 features (global-average-pooled, 2048-d) for every frame of every generated group (Stage C).
    python experiments/robot/extract_features.py --task PickCube [--threads 2]
Reads data/robot/<task>/group_*.npz, writes data/robot/feat/<task>/group_*.npy = float16 (8, K, 2, 2048). Resumable."""
import argparse, glob, os, time
import numpy as np, torch, torchvision

ap = argparse.ArgumentParser(); ap.add_argument("--task", required=True); ap.add_argument("--threads", type=int, default=2); ap.add_argument("--data", default="data/robot"); a = ap.parse_args()
torch.set_num_threads(a.threads)
dev = "cuda" if torch.cuda.is_available() else "cpu"
net = torchvision.models.resnet50(weights=torchvision.models.ResNet50_Weights.IMAGENET1K_V1); net.fc = torch.nn.Identity(); net.eval().to(dev)
mean = torch.tensor([0.485, 0.456, 0.406]).view(1, 3, 1, 1).to(dev); std = torch.tensor([0.229, 0.224, 0.225]).view(1, 3, 1, 1).to(dev)
os.makedirs(f"{a.data}/feat/{a.task}", exist_ok=True)
for f in sorted(glob.glob(f"{a.data}/{a.task}/group_*.npz")):
    out = f.replace(f"/{a.task}/", f"/feat/{a.task}/").replace(".npz", ".npy")
    if os.path.exists(out): continue
    t0 = time.time(); im = np.load(f)["images"]; shp = im.shape[:3]                          # (8, K, 2, ...)
    x = torch.from_numpy(im.reshape(-1, 128, 128, 3)).permute(0, 3, 1, 2).float() / 255.0
    feats = []
    with torch.no_grad():
        for i in range(0, len(x), 120):
            feats.append(net((x[i:i + 120].to(dev) - mean) / std).cpu())
    np.save(out, torch.cat(feats).reshape(*shp, 2048).numpy().astype(np.float16))
    print(f"{os.path.basename(f)}: {len(x)} images, {time.time() - t0:.0f} s", flush=True)
