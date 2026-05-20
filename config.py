from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class SimConfig:
    seed: int = 7
    n_arms: int = 4
    dt: float = 0.05
    max_steps: int = 260
    workspace_size: Tuple[float, float] = (10.0, 10.0)
    base_speed: float = 0.13
    safe_distance: float = 0.55
    payload_mass: float = 3.0
    high_risk_threshold: float = 0.65
    severe_risk_threshold: float = 0.82


@dataclass
class ControllerConfig:
    # The following values mimic the interface you can connect to your existing CVaR-TD3-SMC controller.
    cvar_alpha_default: float = 0.20
    cvar_alpha_min: float = 0.05
    cvar_alpha_max: float = 0.35
    smc_gain_min: float = 2.0
    smc_gain_max: float = 10.0
    boundary_layer_min: float = 0.03
    boundary_layer_max: float = 0.25
    torque_limit: Tuple[float, float, float] = (80.0, 55.0, 30.0)


@dataclass
class AgentConfig:
    use_external_llm: bool = False
    llm_model_name: str = "gpt-4.1-mini"
    macro_task: str = "安全搬运危险品到目标区域，同时避开高温、烟雾和坍塌区域"
    risk_weights: Dict[str, float] = field(default_factory=lambda: {
        "heat": 0.30,
        "smoke": 0.25,
        "collapse": 0.25,
        "obstacle": 0.20,
    })


@dataclass
class ProjectConfig:
    sim: SimConfig = field(default_factory=SimConfig)
    controller: ControllerConfig = field(default_factory=ControllerConfig)
    agent: AgentConfig = field(default_factory=AgentConfig)
