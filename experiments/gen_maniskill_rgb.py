"""Robot ladder data: ManiSkill3 PickCube-v1, two cameras in 64x64 RGB (run in the isolated environment with software Vulkan):
VK_ICD_FILENAMES=/usr/share/vulkan/icd.d/lvp_icd.json /tmp/claude-0/msvenv/bin/python experiments/gen_maniskill_rgb.py N_EPISODES [OUT_DIR]
Writes OUT_DIR/{views.npy (R, 2, T, 12288) uint8 = [base_camera, side render camera] each (3, 64, 64) channel-major, audit.npz (simulator state, evaluator side)}.
Same episode generator as gen_maniskill.py (action smoothing 0.9, noise 0.3, 60 steps)."""
import os, sys

import numpy as np
import gymnasium as gym
import mani_skill.envs  # noqa: F401
import yaml

cfg = yaml.safe_load(open("configs/other_data.yaml"))["robot"]
n_ep, T = int(sys.argv[1]), cfg["steps"]
out = sys.argv[2] if len(sys.argv) > 2 else "data/maniskill_rgb"
env = gym.make("PickCube-v1", obs_mode="rgb", num_envs=1, render_mode="rgb_array", sim_backend="cpu", max_episode_steps=T + 10)
u = env.unwrapped


def small(img):
    a = np.asarray(img, np.float32); k = a.shape[0] // 64
    return np.clip(a.reshape(64, k, 64, k, 3).mean((1, 3)), 0, 255).astype(np.uint8).transpose(2, 0, 1).reshape(-1)


views = np.zeros((n_ep, 2, T, 3 * 64 * 64), np.uint8)
aud = {"goal": np.zeros((n_ep, 3)), "cube": np.zeros((n_ep, T, 3)), "tcp": np.zeros((n_ep, T, 3)), "qpos": np.zeros((n_ep, T, 9))}
rng = np.random.default_rng(0)
for e in range(n_ep):
    obs, _ = env.reset(seed=e)
    aud["goal"][e] = u.goal_site.pose.p[0].numpy()
    a = np.zeros(8, np.float32)
    for t in range(T):
        views[e, 0, t] = small(obs["sensor_data"]["base_camera"]["rgb"][0].cpu().numpy())
        views[e, 1, t] = small(env.render()[0].cpu().numpy())
        aud["cube"][e, t] = u.cube.pose.p[0].numpy(); aud["tcp"][e, t] = u.agent.tcp.pose.p[0].numpy(); aud["qpos"][e, t] = u.agent.robot.get_qpos()[0].cpu().numpy()[:9]
        a = (cfg["action_smoothing"] * a + cfg["action_noise"] * rng.standard_normal(8)).clip(-1, 1).astype(np.float32)
        obs, *_ = env.step(a)
    if e % 10 == 0:
        print("episode", e, flush=True)
os.makedirs(out, exist_ok=True)
np.save(f"{out}/views.npy", views); np.savez(f"{out}/audit.npz", **aud)
print("done", views.shape)
