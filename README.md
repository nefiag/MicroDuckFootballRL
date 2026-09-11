# MicroDuck 足球强化学习课程

基于 Gymnasium 与 Stable-Baselines3 PPO 的完整足球 AI 课程项目，支持 Sim2Real 域随机化、8 集网页动画课程，以及教程、视频脚本和动画提示词自动生成。

## 快速开始

```bash
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"

# 验证 Gymnasium 环境
.venv/bin/python examples/microduck_football_env.py
.venv/bin/pytest

# 快速试训；正式训练去掉 --steps
.venv/bin/python scripts/train_ppo.py --steps 10000
.venv/bin/python scripts/evaluate.py
.venv/bin/python scripts/export_policy.py

# 重新生成全部课程材料
.venv/bin/python scripts/generate_materials.py
```

环境也已注册，可直接使用标准 Gymnasium 创建方式：

```python
import gymnasium as gym
import microduck_football

env = gym.make("MicroDuckFootball-v0", domain_randomization=True)
observation, info = env.reset(seed=42)
```

前端课程：

```bash
cd frontend
npm install
npm run dev
```

## 完整目录

```text
MicroDuckFootballRL/
├── configs/
│   ├── domain_randomization.json  # Sim2Real 参数范围
│   └── ppo.json                   # PPO 超参数
├── course/
│   └── episodes.json              # 8 集课程唯一内容源
├── examples/
│   ├── gymnasium_football_env.py  # 三对象、四动作、每回合域随机化的完整环境
│   └── microduck_football_env.py  # Gymnasium 随机策略示例
├── frontend/
│   ├── src/
│   │   ├── components/FootballCourse.tsx
│   │   ├── App.tsx
│   │   ├── football-course.css
│   │   ├── main.tsx
│   │   └── styles.css
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   ├── vercel.json
│   └── vite.config.ts
├── generated/
│   ├── animation_prompts.md       # 自动生成动画提示词
│   ├── tutorial.md                # 自动生成教程
│   └── video_scripts.md           # 自动生成视频脚本
├── models/                        # PPO 模型输出（不提交大文件）
├── scripts/
│   ├── evaluate.py                # 固定环境策略评估
│   ├── export_policy.py           # 导出 TorchScript
│   ├── generate_materials.py      # 三类材料生成器
│   └── train_ppo.py               # SB3 PPO 训练入口
├── src/microduck_football/
│   ├── __init__.py
│   ├── curriculum.py
│   ├── env.py                     # Gymnasium 足球环境
│   └── randomization.py           # Sim2Real 域随机化
├── tests/
│   └── test_env.py
├── pyproject.toml
└── requirements.txt
```

## 8 集课程

1. [让鸭子学会踢足球：强化学习与项目规划](course/episodes/01-让鸭子学会踢足球.md) · [10 分钟动画分镜](course/episodes/01-animation-storyboard.md)
2. Gymnasium 足球场、状态空间和动作空间
3. 奖励函数与奖励塑形
4. Stable-Baselines3 PPO 训练
5. Curriculum Learning 逐关升级
6. Sim2Real 差距分析
7. Domain Randomization 域随机化
8. 策略导出、真实机器人安全测试与最终射门

`course/episodes.json` 是课程材料的唯一数据源。修改它后运行 `scripts/generate_materials.py`，即可同步生成三个 Markdown 文件，避免教程、视频和提示词内容不一致。

## Mac mini M4

`configs/ppo.json` 默认使用 `device: auto`。Stable-Baselines3 会选择可用设备；小型 MLP 策略通常使用 CPU 已足够。训练前建议先用 `--steps 10000` 验证完整流程，再启动 500,000 步正式训练。
