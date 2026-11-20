"""E74: frozen embeddings of the E62 scene-factor images from a borrowed network (nothing is trained).
    python extract_embeddings.py MODEL IMAGES_NPZ OUT_NPZ        MODEL = vjepa2 | resnet50 | ae   (ae needs data/e62/ae.pt and src/ + experiments/factors on the path)
IMAGES_NPZ holds uint8 images: probe (9000, 96, 96, 3) and u1..u8, v1..v8 (n, 96, 96, 3). OUT_NPZ gets float32 arrays Zp, Zu1..Zu8, Zv1..Zv8.
vjepa2   : facebook/vjepa2-vitl-fpc64-256 (Meta's video JEPA); each image is fed as a 2-frame clip resized to 256 x 256, ImageNet mean/std; patch features averaged -> 1024 numbers
resnet50 : torchvision ResNet-50, IMAGENET1K_V1 supervised weights; image resized to 224, global average pool -> 2048 numbers (the SplitJEPA paper's backbone family; non-JEPA control)
ae       : the E62 convolutional autoencoder encoder (reconstruction-trained, 48 numbers)"""
import sys, time, numpy as np, torch
model_name, src, out = sys.argv[1], sys.argv[2], sys.argv[3]
dev = "cuda" if torch.cuda.is_available() else "cpu"; torch.set_num_threads(4 if dev == "cpu" else 1)
MEAN = torch.tensor([0.485, 0.456, 0.406])[None, :, None, None]; STD = torch.tensor([0.229, 0.224, 0.225])[None, :, None, None]
if model_name == "vjepa2":
    from transformers import VJEPA2Model
    net = VJEPA2Model.from_pretrained("facebook/vjepa2-vitl-fpc64-256").eval().to(dev)
    def f(x):                                                           # x: (B, 3, 96, 96) in [0, 1]
        x = torch.nn.functional.interpolate(x, size=256, mode="bilinear", align_corners=False); x = ((x - MEAN.to(x.device)) / STD.to(x.device))[:, None].repeat(1, 2, 1, 1, 1)
        return net.get_vision_features(pixel_values_videos=x).mean(1)
elif model_name == "resnet50":
    import torchvision
    net = torchvision.models.resnet50(weights=torchvision.models.ResNet50_Weights.IMAGENET1K_V1); net.fc = torch.nn.Identity(); net = net.eval().to(dev)
    def f(x):
        x = torch.nn.functional.interpolate(x, size=224, mode="bilinear", align_corners=False); return net((x - MEAN.to(x.device)) / STD.to(x.device))
elif model_name == "ae":
    from train_ae import AE
    ck = torch.load("data/e62/ae.pt"); net = AE(); net.load_state_dict(ck["state"]); net = net.eval().to(dev)
    def f(x): return net.encode(x)
else: raise SystemExit("model?")
D = np.load(src); res = {}; t0 = time.time(); bs = 128 if dev == "cuda" else 64
for key in ["probe"] + [f"{a}{k}" for k in range(1, 9) for a in "uv"]:
    X = D[key]; parts = []
    with torch.no_grad():
        for i in range(0, len(X), bs):
            x = torch.from_numpy(X[i:i + bs]).permute(0, 3, 1, 2).float().div(255).to(dev); parts.append(f(x).float().cpu())
    Z = torch.cat(parts).numpy(); res["Zp" if key == "probe" else f"Z{key}"] = Z.astype(np.float32); print(key, Z.shape, round(time.time() - t0), "s", flush=True)
np.savez(out, **res); print("saved", out)
