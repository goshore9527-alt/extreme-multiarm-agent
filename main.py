from __future__ import annotations

import json
from pathlib import Path

from config import ProjectConfig
from env.extreme_env import ExtremeMultiArmEnv
from agents.perception_agent import EnvironmentPerceptionAgent
from agents.decision_agent import DecisionAgent
from agents.scheduler_agent import SchedulerAgent
from controllers.cvar_td3_control_api import CVaRTD3SMCControlAPI
from utils.metrics import compute_metrics
from utils.plotting import plot_history


def run_episode(cfg: ProjectConfig, verbose: bool = True):
    env = ExtremeMultiArmEnv(cfg.sim)
    perception = EnvironmentPerceptionAgent(cfg.agent.risk_weights)
    decision = DecisionAgent(cfg.sim.high_risk_threshold, cfg.sim.severe_risk_threshold)
    scheduler = SchedulerAgent(cfg.controller)
    controller = CVaRTD3SMCControlAPI(cfg.controller.torque_limit)

    obs = env.reset()
    latest_plan = None

    while not obs["done"]:
        risk_report = perception.analyze(obs, env)

        # Replan periodically or when risk is high.
        if latest_plan is None or obs["step"] % 20 == 0 or risk_report.global_risk > cfg.sim.high_risk_threshold:
            latest_plan = decision.make_plan(cfg.agent.macro_task, risk_report, obs)
            if verbose and obs["step"] % 40 == 0:
                print(f"[step {obs['step']:03d}] {risk_report.textual_summary}")
                print(f"  plan: {latest_plan.reasoning_summary}")

        scheduled = scheduler.schedule(latest_plan, risk_report, obs, env)
        low_level_commands = {
            arm.arm_id: controller.compute_command(arm, scheduled[arm.arm_id])
            for arm in obs["arms"]
        }
        obs = env.step(low_level_commands)

    metrics = compute_metrics(env.history, env.success())
    return env, metrics


def main():
    cfg = ProjectConfig()
    env, metrics = run_episode(cfg, verbose=True)
    result_dir = Path("results")
    result_dir.mkdir(exist_ok=True)
    plot_history(env.history, str(result_dir))
    with open(result_dir / "metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)
    print("\n=== Metrics ===")
    print(json.dumps(metrics, ensure_ascii=False, indent=2))
    print("\nFigures saved to ./results/: distance_curve.png, risk_curve.png, trajectories.png")


if __name__ == "__main__":
    main()
