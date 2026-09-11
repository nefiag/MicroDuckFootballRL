# MicroduckTraining

专注于《MicroDuck 足球 AI 实战：从强化学习到 Sim2Real》的单课程项目，面向没有强化学习基础的学习者。

## 足球 AI 与 Sim2Real 实战课

网站内置完整的 8 集《MicroDuck 足球 AI 实战：从强化学习到 Sim2Real》，每集包含可播放动画、8–12 分钟视频脚本、动画分镜、实操代码和学习检查。从足球环境、奖励函数、PPO 和课程学习，逐步进入 Sim2Real、域随机化与真实机器人部署，最后展示 MicroDuck 射门与多智能体对抗路线。

可运行的零依赖教学环境位于 `examples/microduck_football_env.py`：

```bash
python3 examples/microduck_football_env.py
```

## 启动

后端：

```bash
cd backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn app.main:app --reload --port 8001
```

前端：

```bash
cd frontend
npm install
npm run dev
```

Vite 开发服务器会把 `/api` 和 `/ws` 代理至 `localhost:8001`。生产环境可设置 `VITE_API_URL`。

## 线上环境

- 前端：https://microduck-training.vercel.app
- 后端：https://microduck-training-api.onrender.com
- GitHub：https://github.com/nefiag/MicroduckTraining
