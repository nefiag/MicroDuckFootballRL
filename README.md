# MicroDuck 足球强化学习课程

独立的足球 AI 教学项目，从二维足球环境和奖励函数出发，逐步学习 PPO、课程学习、Sim2Real、域随机化与真实机器人安全部署。

## 课程内容

- 8 集、约 80 分钟的课程路线
- MicroDuck 足球动作动画
- 动画与代码逐行同步执行
- 视频旁白、动画分镜和 AI 视频提示词
- 代码结构、语句含义与代码规范
- 可运行的零依赖二维足球环境
- 从 Mac mini M4 训练到真实机器人的迁移路线

## 本地运行

```bash
cd frontend
npm install
npm run dev
```

生产构建：

```bash
cd frontend
npm run build
npm run preview
```

运行足球环境示例：

```bash
python3 examples/microduck_football_env.py
```

## 项目结构

```text
MicroDuckFootballRL/
├── examples/
│   └── microduck_football_env.py
└── frontend/
    ├── src/components/FootballCourse.tsx
    ├── src/football-course.css
    ├── src/App.tsx
    └── vercel.json
```
