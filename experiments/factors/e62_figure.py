import sys, json, numpy as np, torch, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0, "experiments/factors"); from train_ae import AE
r = json.load(open("results/e62/e62.json")); B = torch.load("results/e62/blocks.pt")
names = ["gripper", "arm pose", "cube yaw", "cube position", "cube colour", "light tint", "brightness", "cam. dist/elev", "cam. azimuth"]
M = np.array([x["reading"] for x in r["rungs"]] + [r["core_reading"]]); ae = AE(); ae.load_state_dict(B["ae"]); ae.eval()
fig = plt.figure(figsize=(14, 7.4)); gs = fig.add_gridspec(1, 2, width_ratios=[1, 1.15], wspace=0.28)
ax = fig.add_subplot(gs[0]); im = ax.imshow(np.clip(M, 0, 1), cmap="Blues", vmin=0, vmax=1)
ax.set_xticks(range(9)); ax.set_xticklabels([f"{i+1} {n}" for i, n in enumerate(names)], rotation=60, ha="right", fontsize=8.5)
ax.set_yticks(range(9)); ax.set_yticklabels([f"rung {i+1}" for i in range(8)] + ["left-over core"], fontsize=9)
for i in range(9):
    for j in range(9): ax.text(j, i, f"{M[i,j]:.2f}", ha="center", va="center", fontsize=7.5, color="white" if M[i, j] > .55 else "black")
for g in range(9):
    if g + 1 not in r["retained_factors"]: ax.add_patch(plt.Rectangle((g - .5, -.5), 1, 9, fill=False, ec="#b00", lw=1.2, ls="--"))
ax.set_title("Which factor each rung's block carries\n(held-out R², dashed = factor the encoder did not keep)", fontsize=10.5)
sub = gs[1].subgridspec(8, 5, wspace=0.03, hspace=0.05); mean, mat = B["mean"].double(), B["matrix"].double(); inv = torch.linalg.inv(mat)
for k in range(8):
    v = B["blocks"][k][:, 0]
    for j, t in enumerate([-3, -1.5, 0, 1.5, 3]):
        z = (mean + (t * v) @ inv).float()[None]
        with torch.no_grad(): im_ = ae.decode(z)[0].permute(1, 2, 0).numpy()
        a = fig.add_subplot(sub[k, j]); a.imshow(im_); a.set_xticks([]); a.set_yticks([])
        if j == 0: a.set_ylabel(f"r{k+1}", fontsize=8, rotation=0, labelpad=10)
        if k == 0: a.set_title(f"{t:+.1f}", fontsize=8)
fig.text(0.62, 0.935, "What each block does to the image (move along its main direction)", fontsize=10.5, ha="left")
fig.savefig("docs/img/e62_ladder.png", dpi=150, bbox_inches="tight")
