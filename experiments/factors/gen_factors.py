"""E62 data: re-render a ManiSkill3 PickCube scene with nested, nameable factors (registered in docs/EVIDENCE.md).
Run with the ManiSkill venv:  python gen_factors.py OUTDIR   -> pairs_k{1..8}.npz (u, v images + factors), probe.npz
Factors (fast -> slow), group sizes: gripper 1, arm 2, yaw 1, cube xy 2, colour 3, light tint 2, brightness 1, camera dist/elev 2, camera azimuth 1 (15 numbers)."""
import sys, os, numpy as np, torch, gymnasium as gym, mani_skill.envs, sapien
from multiprocessing import Pool
from mani_skill.utils import sapien_utils
from mani_skill.utils.structs.pose import Pose
SIZES = [1, 2, 1, 2, 3, 2, 1, 2, 1]; OFF = np.cumsum([0] + SIZES); NF = int(OFF[-1])
LO = np.array([0.0, -1, -1, -np.pi / 2, -0.06, -0.06, 0.1, 0.1, 0.1, -0.4, -0.4, 0.25, 0.38, 0.6, -0.5]); HI = np.array([0.04, 1, 1, np.pi / 2, 0.06, 0.06, 1, 1, 1, 0.4, 0.4, 0.75, 0.52, 0.95, 0.5])
ARM_DIR = np.random.RandomState(0).randn(2, 7); ARM_DIR /= np.linalg.norm(ARM_DIR, axis=1, keepdims=True)
_env = None
def env():
    global _env
    if _env is None:
        pose = sapien_utils.look_at(eye=[0.32, 0.0, 0.32], target=[0.0, 0.0, 0.02])
        e = gym.make("PickCube-v1", obs_mode="rgb", num_envs=1, sensor_configs=dict(width=96, height=96, base_camera=dict(pose=pose, fov=0.75)), **(dict(sim_backend="cpu", render_backend="cpu") if os.environ.get("CPU_RENDER") else {})); e.reset(seed=0)   # CPU_RENDER=1: software rendering on a pod whose GPU has no Vulkan driver
        u = e.unwrapped; rb = u.cube._objs[0].find_component_by_type(sapien.render.RenderBodyComponent)
        _env = (u, u.scene.sensors["base_camera"].camera, rb, u.agent.robot.get_qpos().clone())
    return _env
def render(f):
    u, cam, rb, q0 = env(); g, a1, a2, yaw, cx, cy, cr, cg, cb, t1, t2, br, rd, el, az = [float(x) for x in f]
    q = q0.clone(); q[:, :7] += 0.12 * torch.tensor(a1 * ARM_DIR[0] + a2 * ARM_DIR[1], dtype=q.dtype)[None]; q[:, 7:9] = g; u.agent.robot.set_qpos(q)
    quat = [np.cos(yaw / 2), 0, 0, np.sin(yaw / 2)]; u.cube.set_pose(Pose.create_from_pq(torch.tensor([[cx, cy, 0.02]]), torch.tensor([quat], dtype=torch.float32)))
    for s in rb.render_shapes:
        for p in s.parts: p.material.set_base_color([cr, cg, cb, 1])
    u.scene.set_ambient_light([br * (1 + t1), br, br * (1 + t2)])
    eye = np.array([rd * np.cos(el) * np.cos(az), rd * np.cos(el) * np.sin(az), 0.02 + rd * np.sin(el)])
    cam.set_local_pose(sapien_utils.look_at(eye=eye, target=[0, 0, 0.02]).sp)
    u.scene.update_render(update_sensors=True); return u.get_obs()["sensor_data"]["base_camera"]["rgb"][0].cpu().numpy()
def work(F): return np.stack([render(f) for f in F])
def render_all(F, pool, chunks=64): return np.concatenate(pool.map(work, np.array_split(F, chunks)))
def draw(rng, n): return LO + rng.rand(n, NF) * (HI - LO)
if __name__ == "__main__":
    out = sys.argv[1]; os.makedirs(out, exist_ok=True); N = 6000; rng = np.random.RandomState(1)
    with Pool(4) as pool:
        for k in range(1, 9):
            A = draw(rng, N); B = draw(rng, N); B[:, OFF[k]:] = A[:, OFF[k]:]          # share factors k+1..9
            np.savez(f"{out}/pairs_k{k}.npz", u=render_all(A, pool), v=render_all(B, pool), fu=A, fv=B); print("rung", k, flush=True)
        P = draw(rng, 9000); np.savez(f"{out}/probe.npz", x=render_all(P, pool), f=P); print("probe", flush=True)
