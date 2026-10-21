"""R1 data: ManiSkill3 PickCube-v1 episodes with two cameras (run in the isolated environment with software Vulkan):
VK_ICD_FILENAMES=/usr/share/vulkan/icd.d/lvp_icd.json /tmp/claude-0/msvenv/bin/python experiments/gen_maniskill.py
Writes data/maniskill/{views.npy (R, 2, T, 1024) gray 32x32 of [base_camera, side render camera], audit.npz (simulator state, evaluator side)}."""
import json, os, sys

import numpy as np
import gymnasium as gym
import mani_skill.envs  # noqa: F401
import yaml

cfg = yaml.safe_load(open("configs/other_data.yaml"))["robot"]
n_ep, T = cfg["n_episodes"], cfg["steps"]
env = gym.make("PickCube-v1", obs_mode="rgb", num_envs=1, render_mode="rgb_array", sim_backend="cpu", max_episode_steps=T + 10)
u = env.unwrapped
def gray(img, k):
    a = np.asarray(img, np.float32).mean(-1) / 255.0
    return a.reshape(32, k, 32, k).mean((1, 3)).reshape(-1)
views = np.zeros((n_ep, 2, T, 1024), np.float32)
aud = {"goal": np.zeros((n_ep, 3)), "cube": np.zeros((n_ep, T, 3)), "tcp": np.zeros((n_ep, T, 3)), "qpos": np.zeros((n_ep, T, 9))}
rng = np.random.default_rng(0)
for e in range(n_ep):
    obs, _ = env.reset(seed=e)
    aud["goal"][e] = u.goal_site.pose.p[0].numpy()
    a = np.zeros(8, np.float32)
    for t in range(T):
        views[e, 0, t] = gray(obs["sensor_data"]["base_camera"]["rgb"][0].cpu().numpy(), 4)
        views[e, 1, t] = gray(env.render()[0].cpu().numpy(), 16)
        aud["cube"][e, t] = u.cube.pose.p[0].numpy(); aud["tcp"][e, t] = u.agent.tcp.pose.p[0].numpy(); aud["qpos"][e, t] = u.agent.robot.get_qpos()[0].cpu().numpy()[:9]
        a = (cfg["action_smoothing"] * a + cfg["action_noise"] * rng.standard_normal(8)).clip(-1, 1).astype(np.float32)
        obs, *_ = env.step(a)
    if e % 10 == 0:
        print("episode", e, flush=True)
os.makedirs("data/maniskill", exist_ok=True)
np.save("data/maniskill/views.npy", views); np.savez("data/maniskill/audit.npz", **aud)
print("done", views.shape)
