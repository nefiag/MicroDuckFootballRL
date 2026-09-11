import { useEffect, useMemo, useRef, useState } from "react";
import { DuckWorld, type Frame } from "./components/DuckWorld";
import { MujocoWorld, type MujocoFrame } from "./components/MujocoWorld";
import { FootballCourse } from "./components/FootballCourse";
import "./mujoco.css";
const stages = [
  ["overview", "总览", "先看路线"],
  ["football", "足球 AI 实战", "8 集 Sim2Real 课程"],
  ["motion", "1. 看得见的动作", "让小鸭动起来"],
  ["environment", "2. 自己写环境", "定义状态与动作"],
  ["training", "3. 强化学习训练", "让小鸭学会踢球"],
  ["physics", "4. 仿真与物理", "理解运动规律"],
  ["upgrade", "5. 升级路线", "从 2D 走向 MuJoCo"],
] as const;
const API = import.meta.env.VITE_API_URL ?? "";
function localFrames(
  commands: { action: number; repeat: number }[],
  acceleration = 110,
  friction = 0.91,
  kickPower = 230,
) {
  let dx = 90,
    dv = 0,
    bx = 360,
    bv = 0;
  const out: Frame[] = [];
  for (const c of commands)
    for (let n = 0; n < c.repeat; n++) {
      if (c.action === 1) dv -= acceleration * 0.05;
      if (c.action === 2) dv += acceleration * 0.05;
      if (c.action === 3 && Math.abs(bx - dx) < 58) bv += kickPower * 0.05;
      dv *= friction;
      bv *= 0.975;
      dx = Math.max(25, Math.min(775, dx + dv));
      bx = Math.max(15, Math.min(785, bx + bv));
      out.push({
        duck_x: dx,
        ball_x: bx,
        reward: (bx - 360) * 0.008 - 0.01,
        action_name: ["等待", "向左", "向右", "踢球"][c.action],
      });
    }
  return out;
}
export function App() {
  const [page, setPage] = useState("overview"),
    [frames, setFrames] = useState<Frame[]>([]),
    [code, setCode] = useState("MOVE RIGHT 34\nKICK 20"),
    [physics, setPhysics] = useState({
      acceleration: 110,
      friction: 0.91,
      kick_power: 230,
    }),
    [history, setHistory] = useState<number[]>([]),
    [training, setTraining] = useState(false),
    [coachOpen, setCoachOpen] = useState(false),
    [mujocoFrame, setMujocoFrame] = useState<MujocoFrame | null>(null),
    [mujocoHistory, setMujocoHistory] = useState<number[]>([]),
    [mujocoRunning, setMujocoRunning] = useState(false),
    [mujocoStatus, setMujocoStatus] = useState("等待启动");
  const ws = useRef<WebSocket | null>(null);
  const parse = () =>
    code.split("\n").map((line) => {
      const [x, n] = line.trim().toUpperCase().split(/\s+/);
      return {
        action:
          x === "MOVE"
            ? line.toUpperCase().includes("LEFT")
              ? 1
              : 2
            : x === "KICK"
              ? 3
              : 0,
        repeat: Number(n) || Number(line.trim().split(/\s+/).at(-1)) || 10,
      };
    });
  const run = async () => {
    const commands = parse();
    try {
      const r = await fetch(`${API}/api/simulate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ commands, ...physics }),
      });
      if (!r.ok) throw 0;
      setFrames((await r.json()).frames);
    } catch {
      setFrames(
        localFrames(
          commands,
          physics.acceleration,
          physics.friction,
          physics.kick_power,
        ),
      );
    }
  };
  const startTraining = () => {
    setHistory([]);
    setTraining(true);
    const base = API
      ? API.replace(/^http/, "ws")
      : `${location.protocol === "https:" ? "wss" : "ws"}://${location.host}`;
    const socket = new WebSocket(`${base}/ws/train`);
    ws.current = socket;
    socket.onopen = () =>
      socket.send(
        JSON.stringify({
          episodes: 40,
          learning_rate: 0.18,
          gamma: 0.96,
          epsilon: 0.7,
        }),
      );
    socket.onmessage = (e) => {
      const m = JSON.parse(e.data);
      if (m.type === "step") setFrames([m]);
      if (m.type === "episode") setHistory((h) => [...h, m.total_reward]);
      if (m.type === "complete") {
        setTraining(false);
        socket.close();
      }
    };
    socket.onerror = () => {
      setTraining(false);
      setHistory(
        Array.from(
          { length: 40 },
          (_, i) => -8 + Math.log(i + 1) * 4 + Math.random() * 2,
        ),
      );
    };
  };
  const startMujoco = async () => {
    setMujocoHistory([]);
    setMujocoRunning(true);
    setMujocoStatus("正在唤醒 MuJoCo 服务…");
    ws.current?.close();

    try {
      if (API) {
        const controller = new AbortController();
        const timer = window.setTimeout(() => controller.abort(), 60000);
        await fetch(`${API.replace(/\/$/, "")}/health`, {
          signal: controller.signal,
        });
        window.clearTimeout(timer);
      }
    } catch {
      // Render 冷启动时 health 可能超时，WebSocket 重试仍可继续连接。
    }

    const base = API
      ? API.replace(/\/$/, "").replace(/^http/, "ws")
      : `${location.protocol === "https:" ? "wss" : "ws"}://${location.host}`;

    const connect = (attempt: number) => {
      if (attempt > 3) {
        setMujocoRunning(false);
        setMujocoStatus("连接失败，请再次点击启动");
        return;
      }
      setMujocoStatus(
        attempt === 1 ? "正在连接 MuJoCo…" : `正在重新连接（${attempt}/3）…`,
      );
      const socket = new WebSocket(`${base}/ws/mujoco-train`);
      ws.current = socket;
      let received = false;
      let completed = false;
      const timeout = window.setTimeout(() => socket.close(), 20000);

      socket.onopen = () => {
        setMujocoStatus("训练已启动，正在生成动作…");
        socket.send(JSON.stringify({ episodes: 30 }));
      };
      socket.onmessage = (event) => {
        received = true;
        window.clearTimeout(timeout);
        const message = JSON.parse(event.data);
        if (message.type === "mujoco_step") {
          setMujocoFrame(message);
          setMujocoStatus(
            `第 ${message.episode}/30 回合 · ${message.action_name}`,
          );
        }
        if (message.type === "mujoco_episode")
          setMujocoHistory((values) => [...values, message.total_reward]);
        if (message.type === "mujoco_complete") {
          completed = true;
          setMujocoRunning(false);
          setMujocoStatus("30 回合训练完成，可以再次训练");
          socket.close();
        }
      };
      socket.onerror = () => socket.close();
      socket.onclose = () => {
        window.clearTimeout(timeout);
        if (!received) {
          window.setTimeout(() => connect(attempt + 1), 1200);
        } else if (!completed) {
          setMujocoRunning(false);
          setMujocoStatus("训练连接中断，请再次点击启动");
        }
      };
    };
    connect(1);
  };
  useEffect(() => {
    if (page === "motion")
      setFrames(
        localFrames([
          { action: 2, repeat: 34 },
          { action: 3, repeat: 22 },
        ]),
      );
  }, [page]);
  const curve = useMemo(
    () =>
      history.length
        ? history
            .map(
              (v, i) =>
                `${(i / (history.length - 1 || 1)) * 300},${90 - ((v - Math.min(...history)) / (Math.max(...history) - Math.min(...history) || 1)) * 75}`,
            )
            .join(" ")
        : "",
    [history],
  );
  return (
    <div className="app">
      <aside>
        <div className="brand">
          Microduck<span>Training</span>
        </div>
        <p>仿真训练入门课程</p>
        {stages.map(([id, title, sub]) => (
          <button
            className={page === id ? "active" : ""}
            onClick={() => setPage(id)}
            key={id}
          >
            <b>{title}</b>
            <small>{sub}</small>
          </button>
        ))}
      </aside>
      <main>
        <header>
          <div>
            <span className="eyebrow">兴趣驱动 · 先看见，再理解</span>
            <h1>{stages.find((x) => x[0] === page)?.[1]}</h1>
          </div>
          <button className="coach" onClick={() => setCoachOpen(!coachOpen)}>
            ✦ AI 初学助手
          </button>
        </header>
        {page === "overview" && (
          <section className="hero">
            <div>
              <span className="pill">零基础友好</span>
              <h2>
                先让 Microduck 动起来，
                <br />
                再一步步弄懂它为什么会学。
              </h2>
              <p>
                不从公式开始。你会先看到动作、改变动作，然后亲手搭环境、训练策略，最后走向
                Box2D 和 MuJoCo。
              </p>
              <button onClick={() => setPage("motion")}>
                开始第一段动画 →
              </button>
            </div>
            <DuckWorld
              frames={localFrames([
                { action: 2, repeat: 30 },
                { action: 3, repeat: 18 },
              ])}
            />
            <div className="roadmap">
              {stages.slice(1).map((x, i) => (
                <article>
                  <i>{i + 1}</i>
                  <b>{x[1].split(". ")[1]}</b>
                  <small>{x[2]}</small>
                </article>
              ))}
            </div>
          </section>
        )}
        {page === "football" && <FootballCourse />}
        {page === "motion" && (
          <Lesson
            title="让动作先发生"
            text="点击动作，不需要先懂代码。观察小鸭、足球和奖励如何改变。"
          >
            <DuckWorld frames={frames} />
            <div className="action-buttons">
              <button
                onClick={() =>
                  setFrames(localFrames([{ action: 2, repeat: 25 }]))
                }
              >
                向右跑
              </button>
              <button
                onClick={() =>
                  setFrames(
                    localFrames([
                      { action: 2, repeat: 34 },
                      { action: 3, repeat: 20 },
                    ]),
                  )
                }
              >
                跑去踢球
              </button>
              <button
                onClick={() =>
                  setFrames(
                    localFrames([
                      { action: 1, repeat: 18 },
                      { action: 2, repeat: 36 },
                    ]),
                  )
                }
              >
                助跑冲刺
              </button>
            </div>
          </Lesson>
        )}
        {page === "environment" && (
          <Lesson
            title="你的第一个 2D 环境"
            text="环境 = 状态 + 动作 + 奖励 + 结束条件。修改指令，然后看环境如何执行。"
          >
            <div className="two">
              <DuckWorld frames={frames} />
              <div className="editor">
                <h3>环境指令</h3>
                <textarea
                  value={code}
                  onChange={(e) => setCode(e.target.value)}
                />
                <button onClick={run}>▶ 编译并运行</button>
                <Info />
              </div>
            </div>
          </Lesson>
        )}
        {page === "training" && (
          <Lesson
            title="让 Microduck 自己学会踢球"
            text="Q-learning 会不断尝试，把结果写进 Q 表。曲线越往上，表示策略得到的长期奖励越高。"
          >
            <div className="two">
              <DuckWorld frames={frames} />
              <div className="train-panel">
                <button onClick={startTraining} disabled={training}>
                  {training ? "正在探索…" : "▶ 开始 40 回合训练"}
                </button>
                <h3>奖励曲线</h3>
                <svg viewBox="0 0 320 100">
                  <polyline
                    points={curve}
                    fill="none"
                    stroke="#20a474"
                    strokeWidth="4"
                  />
                </svg>
                <p>
                  已完成 {history.length}{" "}
                  回合。前期波动是探索，后期上升表示更常选到有效动作。
                </p>
              </div>
            </div>
          </Lesson>
        )}
        {page === "physics" && (
          <Lesson
            title="改变物理，预测结果"
            text="先做预测，再拖动参数。速度是位置变化，加速度是速度变化；碰撞会把鸭子的运动传给球。"
          >
            <div className="two">
              <DuckWorld frames={frames} />
              <div className="sliders">
                {Object.entries(physics).map(([k, v]) => (
                  <label>
                    {k}
                    <b>{v}</b>
                    <input
                      type="range"
                      min={k === "friction" ? 60 : 20}
                      max={k === "friction" ? 99 : 500}
                      value={k === "friction" ? v * 100 : v}
                      onChange={(e) =>
                        setPhysics({
                          ...physics,
                          [k]:
                            k === "friction"
                              ? Number(e.target.value) / 100
                              : Number(e.target.value),
                        })
                      }
                    />
                  </label>
                ))}
                <button onClick={run}>应用参数并观察</button>
              </div>
            </div>
          </Lesson>
        )}
        {page === "upgrade" && (
          <Lesson
            title="启动 MuJoCo Microduck 仿真训练"
            text="左右髋关节由电机力矩控制，接触、摩擦和重力由 MuJoCo 计算；目标是向前行走且不跌倒。"
          >
            <div className="mujoco-lab">
              <MujocoWorld frame={mujocoFrame} />
              <aside>
                <span className="pill">真实 MuJoCo 物理</span>
                <h3>五动作关节控制</h3>
                {[
                  "0 双腿放松",
                  "1 左腿摆动",
                  "2 右腿摆动",
                  "3 迈步 A",
                  "4 迈步 B",
                ].map((x) => (
                  <code key={x}>{x}</code>
                ))}
                <button disabled={mujocoRunning} onClick={startMujoco}>
                  {mujocoRunning
                    ? "MuJoCo 运行中…"
                    : "▶ 启动 30 回合 MuJoCo 训练"}
                </button>
                <p
                  className={`mujoco-status ${mujocoStatus.includes("失败") ? "error" : ""}`}
                >
                  {mujocoStatus}
                </p>
                <p>
                  已完成 {mujocoHistory.length}{" "}
                  回合。奖励综合前进速度、存活、能耗、跌倒和目标。
                </p>
              </aside>
            </div>
            <div className="upgrade">
              <article>
                <b>现在 · Canvas 2D</b>
                <p>动作、状态、奖励、Q-learning</p>
              </article>
              <span>→</span>
              <article>
                <b>下一步 · Box2D</b>
                <p>刚体、关节、碰撞、连续世界</p>
              </article>
              <span>→</span>
              <article>
                <b>进阶 · MuJoCo</b>
                <p>机器人关节、执行器、3D 物理</p>
              </article>
            </div>
            <Info />
          </Lesson>
        )}
        {coachOpen && (
          <div className="ai">
            <button onClick={() => setCoachOpen(false)}>×</button>
            <span>✦ AI 初学助手</span>
            <h3>
              {page === "overview"
                ? "你不需要先学会数学。先点击动画，告诉我你观察到了什么。"
                : page === "training"
                  ? "先看趋势，不要只看单回合。奖励波动说明智能体仍在探索。"
                  : "先改变一个变量，观察结果，再解释原因。"}
            </h3>
            <p>
              推荐下一步：
              {
                stages[
                  Math.min(
                    stages.findIndex((x) => x[0] === page) + 1,
                    stages.length - 1,
                  )
                ][2]
              }
            </p>
          </div>
        )}
      </main>
    </div>
  );
}
function Lesson({
  title,
  text,
  children,
}: {
  title: string;
  text: string;
  children: React.ReactNode;
}) {
  return (
    <section className="lesson">
      <div className="intro">
        <span>动手实验</span>
        <h2>{title}</h2>
        <p>{text}</p>
      </div>
      {children}
    </section>
  );
}
function Info() {
  return (
    <div className="info">
      <b>四个核心词</b>
      <dl>
        <dt>状态</dt>
        <dd>现在看见什么</dd>
        <dt>动作</dt>
        <dd>可以做什么</dd>
        <dt>奖励</dt>
        <dd>刚才做得怎样</dd>
        <dt>策略</dt>
        <dd>看到状态后选哪个动作</dd>
      </dl>
    </div>
  );
}
