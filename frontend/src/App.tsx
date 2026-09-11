import { FootballCourse } from "./components/FootballCourse";

export function App() {
  return (
    <div className="football-app">
      <header className="site-header">
        <div className="site-brand">
          <span className="duck-mark">MD</span>
          <div>
            <b>MicroDuck 足球强化学习课程</b>
            <small>Football RL · 从仿真到真实机器人</small>
          </div>
        </div>
        <div className="course-meta">
          <span>8 集课程</span>
          <span>约 80 分钟</span>
          <span>Mac mini M4</span>
        </div>
      </header>
      <main>
        <FootballCourse />
      </main>
      <footer>MicroDuck 足球 AI 实战 · 仿真训练 → 域随机化 → 真实机器人</footer>
    </div>
  );
}
