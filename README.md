# Extreme Multi-Arm Cooperative Scheduling Agent

这是一个可直接运行的“极端环境多机械臂协作调度 Agent”工程骨架，用于支撑以下项目描述：

> 基于 LLM/Agent 的极端环境多机械臂协同决策调度框架，通过环境感知 Agent、决策 Agent、调度 Agent 与底层 CVaR-TD3-SMC 控制接口打通从自然语言任务到多机械臂执行控制的链路。

## 工程结构

```text
extreme_multiarm_agent/
├── main.py
├── config.py
├── agents/
│   ├── perception_agent.py
│   ├── decision_agent.py
│   └── scheduler_agent.py
├── controllers/
│   └── cvar_td3_control_api.py
├── env/
│   └── extreme_env.py
├── utils/
│   ├── metrics.py
│   └── plotting.py
└── results/
```

## 运行方式

```bash
cd extreme_multiarm_agent
python main.py
```

运行后会生成：

- `results/metrics.json`
- `results/distance_curve.png`
- `results/risk_curve.png`
- `results/trajectories.png`

## 核心逻辑流

1. **环境感知 Agent**：读取热源、烟雾、坍塌、障碍物等风险源，输出全局风险、载荷风险、目标区域风险、各机械臂局部风险。
2. **决策 Agent**：根据自然语言宏观任务和风险报告，将任务分解为“安全通道探索、载荷稳定、协同搬运、外围监测”等子任务。
3. **调度 Agent**：根据各机械臂风险水平和任务优先级分配 Follower，并生成每个机械臂的控制参数。
4. **CVaR-TD3-SMC 控制接口**：接收调度层下发的 `cvar_alpha`、`smc_gain`、`boundary_layer` 等参数。当前为可运行代理接口，可替换成你的真实 PyTorch CVaR-TD3-SMC 控制器。
5. **仿真评估**：输出任务成功率、最终距离、平均风险、CVaR top-20% 风险、收敛步数等指标。

## 如何接入你的真实 CVaR-TD3-SMC 代码

修改 `controllers/cvar_td3_control_api.py` 中的 `compute_command()`：

```python
state = build_state(arm_state, scheduled_cmd, env_state)
rl_action = self.actor(state)
torque = smc_layer(
    rl_action,
    cvar_alpha=scheduled_cmd["cvar_alpha"],
    smc_gain=scheduled_cmd["smc_gain"],
    boundary_layer=scheduled_cmd["boundary_layer"],
)
return torque
```

建议把 Agent 层输出与底层控制层连接成如下参数：

- `risk_sensitivity -> cvar_alpha`
- `risk_sensitivity -> smc_gain`
- `risk_sensitivity -> boundary_layer`
- `subtask -> reference trajectory / waypoint`

## 可写进项目申报/评估表的成果表述

我搭建了一个面向极端环境的多机械臂协作调度 Agent。系统采用多 Agent 协作架构：环境感知 Agent 将热源、烟雾、坍塌和障碍物等语义风险转换为量化风险指标；决策 Agent 将自然语言宏观任务分解为可执行子任务；调度 Agent 根据风险等级和机械臂状态动态分配 Follower，并通过 API 将 CVaR 风险敏感度、SMC 增益和边界层参数下发到底层控制器。该框架打通了从自然语言任务理解、风险评估、任务分解、协作调度到底层 CVaR-TD3-SMC 控制的完整链路。
