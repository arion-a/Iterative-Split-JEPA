"""Generate matched groups of ManiSkill3 trajectories with two cameras (Stage C; design in docs/stage_c_design.md). Run with the ManiSkill environment:
    python experiments/robot/gen_robot_data.py --task PickCube --groups 0 1 2 --out data/robot
One .npz per group: images (8, K, 2, 128, 128, 3) uint8 [camera 0 = base, 1 = side], state (8, K, 9) = tcp xyz, cube xyz, goal xyz, progress (K,), success (8,).
A group = the same initial layout (env seed) executed 8 times with perturbed waypoints and speed (the paper's way of generating trajectories is not stated)."""
import argparse, os, time
import numpy as np, torch, sapien, gymnasium as gym
from mani_skill.envs.tasks.tabletop.pick_cube import PickCubeEnv
from mani_skill.envs.tasks.tabletop.push_cube import PushCubeEnv
from mani_skill.envs.utils import randomization  # noqa: F401
from mani_skill.sensors.camera import CameraConfig
from mani_skill.utils import sapien_utils
from mani_skill.utils.registration import register_env
from mani_skill.examples.motionplanning.panda.motionplanner import PandaArmMotionPlanningSolver
from mani_skill.examples.motionplanning.base_motionplanner.utils import compute_grasp_info_by_obb, get_actor_obb

SIDE = sapien_utils.look_at(eye=[0.05, 0.55, 0.45], target=[0.0, 0.0, 0.1])


@register_env("PickCubeSide-v1", max_episode_steps=2000)
class PickCubeSide(PickCubeEnv):
    @property
    def _default_sensor_configs(self):
        return list(super()._default_sensor_configs) + [CameraConfig("side_camera", SIDE, 128, 128, np.pi / 2, 0.01, 100)]


@register_env("PushCubeSide-v1", max_episode_steps=2000)
class PushCubeSide(PushCubeEnv):
    @property
    def _default_sensor_configs(self):
        return list(super()._default_sensor_configs) + [CameraConfig("side_camera", SIDE, 128, 128, np.pi / 2, 0.01, 100)]


class Recorder(gym.Wrapper):
    """Records both cameras and a small state vector at every control step."""
    def __init__(self, env):
        super().__init__(env); self.reset_log()

    def reset_log(self):
        self.frames, self.states = [], []

    def _log(self, obs):
        u = self.env.unwrapped
        sd = obs["sensor_data"]
        self.frames.append(np.stack([sd["base_camera"]["rgb"][0].cpu().numpy(), sd["side_camera"]["rgb"][0].cpu().numpy()]))
        goal = (u.goal_site.pose.p if hasattr(u, "goal_site") else u.goal_region.pose.p)[0].cpu().numpy()
        self.states.append(np.concatenate([u.agent.tcp.pose.p[0].cpu().numpy(), (u.cube if hasattr(u, "cube") else u.obj).pose.p[0].cpu().numpy(), goal]))

    def reset(self, **kw):
        out = self.env.reset(**kw); self.reset_log(); self._log(out[0]); return out

    def step(self, a):
        out = self.env.step(a); self._log(out[0]); return out


def planner_for(env, rng):
    return PandaArmMotionPlanningSolver(env, debug=False, vis=False, base_pose=env.unwrapped.agent.robot.pose, visualize_target_grasp_pose=False, print_env_info=False,
                                        joint_vel_limits=float(rng.uniform(0.4, 1.0)), joint_acc_limits=float(rng.uniform(0.4, 1.0)))


def solve_pick(env, seed, rng):
    env.reset(seed=seed); pl = planner_for(env, rng); u = env.unwrapped
    obb = get_actor_obb(u.cube); appr = np.array([0, 0, -1]); closing_t = u.agent.tcp.pose.to_transformation_matrix()[0, :3, 1].cpu().numpy()
    gi = compute_grasp_info_by_obb(obb, approaching=appr, target_closing=closing_t, depth=0.025)
    grasp = u.agent.build_grasp_pose(appr, gi["closing"], u.cube.pose.sp.p)
    off = np.array([rng.uniform(-0.03, 0.03), rng.uniform(-0.03, 0.03), rng.uniform(-0.07, -0.03)])          # perturbed reach point
    pl.move_to_pose_with_screw(sapien.Pose(grasp.p + off, grasp.q)) if False else pl.move_to_pose_with_screw(grasp * sapien.Pose(off))
    pl.move_to_pose_with_screw(grasp); pl.close_gripper()
    lift = rng.uniform(0.0, 0.08)
    res = pl.move_to_pose_with_screw(sapien.Pose(u.goal_site.pose.sp.p + np.array([0, 0, lift]), grasp.q))
    res = pl.move_to_pose_with_screw(sapien.Pose(u.goal_site.pose.sp.p, grasp.q)) if lift > 0 else res
    pl.close(); return res


def solve_push(env, seed, rng):
    env.reset(seed=seed); pl = planner_for(env, rng); u = env.unwrapped
    pl.close_gripper()
    behind = rng.uniform(0.04, 0.08); side = rng.uniform(-0.02, 0.02); up = rng.uniform(0.0, 0.02)
    pl.move_to_pose_with_screw(sapien.Pose(u.obj.pose.sp.p + np.array([-behind, side, up]), u.agent.tcp.pose.sp.q))
    res = pl.move_to_pose_with_screw(sapien.Pose(u.goal_region.pose.sp.p + np.array([-rng.uniform(0.10, 0.14), side, 0.0]), u.agent.tcp.pose.sp.q))
    pl.close(); return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", choices=["PickCube", "PushCube"], required=True)
    ap.add_argument("--groups", type=int, nargs="+", required=True)
    ap.add_argument("--per-group", type=int, default=8); ap.add_argument("--frames", type=int, default=30); ap.add_argument("--out", default="data/robot")
    a = ap.parse_args()
    env = Recorder(gym.make(f"{a.task}Side-v1", obs_mode="rgb", control_mode="pd_joint_pos", render_mode="rgb_array", sim_backend="cpu"))
    solve = solve_pick if a.task == "PickCube" else solve_push
    os.makedirs(f"{a.out}/{a.task}", exist_ok=True)
    for g in a.groups:
        path = f"{a.out}/{a.task}/group_{g:04d}.npz"
        if os.path.exists(path): continue
        t0 = time.time(); imgs, sts, succ, lens, tries = [], [], [], [], 0
        rng = np.random.default_rng(10_000 + g)
        while len(imgs) < a.per_group and tries < 6 * a.per_group:
            tries += 1
            try:
                res = solve(env, 1000 + g, rng)
                ok = res != -1 and bool(res[-1]["success"].item())
            except Exception as e:
                ok = False
            if not ok or len(env.frames) < 8: continue
            idx = np.round(np.linspace(0, len(env.frames) - 1, a.frames)).astype(int)
            imgs.append(np.stack([env.frames[i] for i in idx])); sts.append(np.stack([env.states[i] for i in idx])); lens.append(len(env.frames)); succ.append(True)
        if len(imgs) < a.per_group: print(f"group {g}: only {len(imgs)} successful trajectories after {tries} tries, skipped", flush=True); continue
        np.savez_compressed(path, images=np.stack(imgs), state=np.stack(sts), progress=np.linspace(0, 1, a.frames), success=np.array(succ), lengths=np.array(lens), group=g, task=a.task)
        print(f"group {g}: 8 trajectories, lengths {lens}, {tries} tries, {time.time() - t0:.0f} s", flush=True)


if __name__ == "__main__":
    main()
