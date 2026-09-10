# MicroduckTraining

兴趣导向的 Microduck 仿真训练入门课程。学习顺序是“先看到动作 → 修改动作 → 自己定义环境 → 强化学习 → 理解物理 → 升级复杂仿真”，面向没有强化学习基础的学习者。

## 五阶段

1. 看得见的动作：直接播放向右跑、踢球和助跑动画。
2. 自己写环境：使用简单动作指令操作 2D duck 踢球环境，并认识状态、动作、奖励和结束条件。
3. 强化学习训练：使用 Q-learning 训练 Microduck 踢球，实时展示训练动作和奖励曲线。
4. 仿真与物理：修改加速度、摩擦和踢球冲量，预测并观察结果。
5. 升级路线：理解 Canvas 2D → Box2D → MuJoCo 的能力增量。

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

- 前端：https://frontend-iota-sage-58.vercel.app
- 后端：https://microduck-training-api.onrender.com
- GitHub：https://github.com/nefiag/MicroduckTraining
