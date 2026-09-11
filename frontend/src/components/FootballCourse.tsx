import { useEffect, useMemo, useState } from "react";
import "../football-course.css";

type Episode = {
  title: string;
  label: string;
  duration: string;
  goal: string;
  narration: string[];
  shots: string[];
  code: string;
};

const episodes: Episode[] = [
  {
    title: "让鸭子学会踢足球！",
    label: "项目启动",
    duration: "8–10 分钟",
    goal: "先看最终效果，再建立观察 → 动作 → 奖励 → 学习的完整直觉。",
    narration: [
      "大家好，这一系列课程里，我们将使用 MicroDuck 从零训练一个足球机器人。",
      "我们不会手写每一步踢球程序，而是让 AI 通过奖励自己找到策略，最终迁移到真实机器人。",
      "直接训练完整足球任务太难，所以我们把它拆成走路、找球、踢球、带球、射门和 Sim2Real 六关。",
    ],
    shots: [
      "草坪上出现 MicroDuck 与足球",
      "小鸭撞球，足球飞入球门",
      "六关路线图逐级点亮",
      "强化学习循环箭头旋转",
    ],
    code: `observation = env.reset()\nwhile not done:\n    action = policy(observation)\n    observation, reward, done = env.step(action)\n    policy.learn(reward)`,
  },
  {
    title: "创建足球训练场",
    label: "状态空间",
    duration: "9 分钟",
    goal: "读懂机器人、球和球门的位置，并把连续世界转换成模型能接收的状态向量。",
    narration: [
      "状态是 AI 在某一刻看到的世界快照。",
      "绝对坐标可以工作，但相对坐标更容易迁移：球在我前方多少、球门在球前方多少。",
      "每次 step，环境接收动作、推进物理，再返回新状态、奖励和是否结束。",
    ],
    shots: [
      "俯视球场依次生成机器人、足球、球门",
      "robot_x、robot_y、angle 逐项闪光",
      "球与球门坐标连成状态向量",
      "动作后状态数字更新",
    ],
    code: `def observation(robot, ball, goal):\n    return [\n        ball.x - robot.x,\n        ball.y - robot.y,\n        goal.x - ball.x,\n        goal.y - ball.y,\n        robot.angle,\n    ]`,
  },
  {
    title: "奖励函数设计",
    label: "奖励塑形",
    duration: "10 分钟",
    goal: "用少量、方向明确的奖励引导接近球、触球、射门和进球。",
    narration: [
      "奖励函数不是答案，而是告诉 AI 什么结果更好。",
      "接近球给小奖励，远离球扣分；触球和朝球门推进给更强的信号。",
      "进球奖励最大，但要避免 AI 利用漏洞刷分，因此每一步也有轻微时间成本。",
    ],
    shots: [
      "接近球连续弹出 +0.1",
      "远离球弹出红色 −0.1",
      "触球爆出 +1，射门 +5",
      "进球出现光环与 +100",
    ],
    code: `reward = -0.002                  # 时间成本\nreward += old_ball_dist - ball_dist # 接近球\nif touched_ball: reward += 1.0\nreward += 2.0 * ball_goal_progress\nif scored: reward += 100.0`,
  },
  {
    title: "训练第一位足球运动员",
    label: "PPO 训练",
    duration: "10 分钟",
    goal: "在 Mac mini M4 上启动训练，正确阅读 episode reward、成功率和损失曲线。",
    narration: [
      "最开始它什么都不会，随机动作甚至碰不到球。",
      "随着经验积累，价值网络更会判断局面，策略网络更常选出有效动作。",
      "不要只看单回合奖励，要看移动平均线与固定评估局的进球率。",
    ],
    shots: [
      "Episode 1 小鸭随机乱走",
      "计数跳到 100、1000、5000",
      "奖励曲线波动上升",
      "成功率仪表盘变绿",
    ],
    code: `from stable_baselines3 import PPO\n\nenv = MicroDuckFootballEnv()\nmodel = PPO("MlpPolicy", env, verbose=1,\n            device="mps", batch_size=256)\nmodel.learn(total_timesteps=500_000)\nmodel.save("football_policy")`,
  },
  {
    title: "课程学习 Curriculum Learning",
    label: "逐关升级",
    duration: "9 分钟",
    goal: "通过四级难度课程，让策略从近距离触球逐步学会全场射门。",
    narration: [
      "像游戏升级一样，先让 AI 在容易的任务里发现有效行为。",
      "进球率稳定超过百分之八十，再扩大球的随机范围。",
      "旧关卡要保留一部分采样，避免模型学会新技能却忘掉旧技能。",
    ],
    shots: [
      "Level 1 球固定在脚下",
      "Level 2 球随机 50 厘米",
      "Level 3 扩展到整个球场",
      "Level 4 加入方向变化的球门",
    ],
    code: `if success_rate > 0.80:\n    level = min(level + 1, 4)\n\nspawn_radius = [0.15, 0.5, 1.5, 2.5][level-1]\nenv.set_curriculum(level, spawn_radius)`,
  },
  {
    title: "为什么仿真成功现实失败？",
    label: "Sim2Real 差距",
    duration: "8 分钟",
    goal: "识别摩擦、质量、传感器、电机延迟和视觉噪声造成的现实差距。",
    narration: [
      "仿真中的数字是干净的，电机响应也是即时的；真实世界不会这么配合。",
      "同一个策略在摩擦变小、摄像头延迟后，可能完全错过足球。",
      "迁移前先建立差距清单，再决定随机化范围与真实数据校准方法。",
    ],
    shots: [
      "屏幕分成仿真与真实两侧",
      "现实侧依次出现摩擦、误差、延迟、噪声",
      "机器人因延迟跌倒",
      "字幕：仿真神，现实新手",
    ],
    code: `sim2real_gap = {\n    "friction": measure_floor(),\n    "motor_delay_ms": 35,\n    "camera_fps": 30,\n    "position_noise": 0.015,\n}`,
  },
  {
    title: "域随机化 Domain Randomization",
    label: "适应现实",
    duration: "10 分钟",
    goal: "随机化动力学和视觉，让现实世界成为模型训练过的众多世界之一。",
    narration: [
      "如果机器人只在一个完美世界训练，它会记住那个世界。",
      "我们随机改变摩擦、质量、重心、功率、延迟、亮度和噪声。",
      "范围不是越大越好：先覆盖实测值，再逐步扩大，持续监控基本技能是否退化。",
    ],
    shots: [
      "随机化轮盘高速旋转",
      "木地板、草地、地毯、瓷砖切换",
      "参数数字持续变化",
      "多个世界汇聚到真实球场",
    ],
    code: `def randomize(model):\n    model.friction = random.uniform(0.4, 1.2)\n    model.mass *= random.uniform(0.85, 1.15)\n    motor.power *= random.uniform(0.8, 1.1)\n    camera.delay = random.uniform(0.02, 0.08)`,
  },
  {
    title: "真实机器人测试",
    label: "部署与决赛",
    duration: "10–12 分钟",
    goal: "导出策略，按安全检查表部署到 MicroDuck，并完成找球、接近、射门演示。",
    narration: [
      "先在低速、支架保护和急停可用的条件下测试单个动作。",
      "部署时只运行策略推理，不在机器人上继续训练；观测必须与仿真同序、同单位。",
      "最终挑战是红蓝两队多智能体对抗，但第一步永远是稳定完成一次安全射门。",
    ],
    shots: [
      "导出 football_policy.onnx",
      "仿真世界变形为真实球场",
      "小鸭找球、接近、调整角度",
      "射门进球，红蓝队与烟花登场",
    ],
    code: `model.export("football_policy.onnx")\nobs = normalize(camera.observe())\naction = policy.run(obs)\naction = safety_limit(action)\nrobot.execute(action)`,
  },
];

const codeGuides = [
  {
    structure:
      "这是强化学习最小循环：重置环境得到初始状态，在循环中选择动作、推进环境、接收反馈，再用反馈更新策略。",
    statements: [
      ["observation = env.reset()", "重置球场，并取得模型第一次看到的状态。"],
      ["while not done", "只要回合没有进球、出界或超时，就继续交互。"],
      ["env.step(action)", "执行动作，并一次性返回新状态、奖励和结束标记。"],
      [
        "policy.learn(reward)",
        "教学简写；正式算法还会使用状态、动作和价值估计。",
      ],
    ],
    standards: [
      "使用 observation、action、reward、done 等领域名称",
      "一个循环只推进一次环境",
      "真实项目应设置最大步数，避免死循环",
    ],
  },
  {
    structure:
      "函数接收三个对象并返回固定顺序的一维状态向量。前四项是相对位置，最后一项是机器人朝向。",
    statements: [
      [
        "def observation(...)",
        "def 定义可重复调用的函数，参数明确列出依赖对象。",
      ],
      ["ball.x - robot.x", "球的横坐标减机器人横坐标；正值表示球在右侧。"],
      ["goal.x - ball.x", "用球到球门的相对位置描述射门方向。"],
      [
        "return [...]",
        "返回固定长度列表；训练和真实部署必须保持完全相同顺序。",
      ],
    ],
    standards: [
      "坐标单位统一使用米，角度统一使用弧度",
      "对输入做归一化并记录上下界",
      "不要在训练与部署阶段改变特征顺序",
    ],
  },
  {
    structure:
      "奖励由时间成本、接近球进度、触球奖励、朝球门进度和进球大奖五部分相加组成。",
    statements: [
      ["reward = -0.002", "每走一步略微扣分，鼓励更快完成任务。"],
      ["reward += old - new", "距离变小时差值为正，远离时自然变成惩罚。"],
      ["if touched_ball", "事件奖励只在满足触球条件时加入。"],
      ["if scored", "终局目标权重最高，确保策略最终服务于进球。"],
    ],
    standards: [
      "各奖励项命名并分别记录到日志",
      "避免只奖励动作本身，应奖励可验证结果",
      "检查奖励量级，防止小项盖过最终目标",
    ],
  },
  {
    structure:
      "先创建环境，再构造 PPO 模型，训练固定步数，最后保存参数；模型配置与训练执行分离。",
    statements: [
      ["from stable_baselines3 import PPO", "从库中导入近端策略优化算法类。"],
      ['PPO("MlpPolicy", env, ...)', "使用多层感知机策略，并绑定足球环境。"],
      [
        'device="mps"',
        "在 Apple Silicon 上请求 Metal 加速；不支持时改为 auto。",
      ],
      [
        "model.learn(...)",
        "执行 500,000 个环境交互步，而不是 500,000 个回合。",
      ],
    ],
    standards: [
      "固定随机种子并保存全部超参数",
      "训练与评估使用不同环境实例",
      "模型文件带版本、步数和日期，不直接覆盖",
    ],
  },
  {
    structure:
      "先根据成功率判断是否升级，再从配置表读取当前关卡范围，最后通过环境方法统一更新难度。",
    statements: [
      ["success_rate > 0.80", "评估进球率超过 80% 才解锁下一关。"],
      ["min(level + 1, 4)", "把最高等级限制为 4，防止数组越界。"],
      ["[...][level - 1]", "关卡从 1 编号，列表索引从 0 开始，因此需要减 1。"],
      [
        "set_curriculum(...)",
        "把难度变化封装到环境接口，避免外部直接修改内部状态。",
      ],
    ],
    standards: [
      "升级依据使用多回合移动平均，不看单局结果",
      "关卡参数集中配置",
      "保留旧关卡抽样，检查灾难性遗忘",
    ],
  },
  {
    structure: "字典把每个现实差距映射为可测量参数，形成仿真校准清单。",
    statements: [
      ["sim2real_gap = {...}", "用键值对集中保存现实测量结果。"],
      ["measure_floor()", "通过函数读取实测摩擦，而不是把猜测散落在代码里。"],
      ["motor_delay_ms", "明确名称中携带毫秒单位，减少单位误用。"],
      ["position_noise", "位置噪声标准差用于模拟视觉测量抖动。"],
    ],
    standards: [
      "变量名携带不明显的单位后缀",
      "实测值、默认值和随机范围分开保存",
      "配置应可序列化，便于复现实验",
    ],
  },
  {
    structure:
      "randomize 函数在每回合 reset 时调用，对动力学和传感器参数分别采样。",
    statements: [
      ["random.uniform(a, b)", "从闭区间附近均匀采样一个随机浮点数。"],
      ["model.mass *= ...", "按比例缩放质量，保留模型各部件原来的相对关系。"],
      ["motor.power *= ...", "模拟不同电量、温度下的电机输出变化。"],
      ["camera.delay = ...", "随机视觉延迟，使策略不依赖零延时观测。"],
    ],
    standards: [
      "只在 reset 时随机化，避免单回合物理规律突变",
      "范围应覆盖实测值但不过分夸张",
      "记录每回合采样参数以复现失败案例",
    ],
  },
  {
    structure:
      "部署流水线依次完成模型导出、传感器读取、输入归一化、策略推理、安全限幅和机器人执行。",
    statements: [
      ["model.export(...)", "导出只含推理图的模型，真实机器人无需训练框架。"],
      [
        "normalize(camera.observe())",
        "把相机观测转换成训练时相同的范围和排列。",
      ],
      ["policy.run(obs)", "前向推理得到动作，不在真实机器人上反向传播。"],
      ["safety_limit(action)", "在执行前限制速度、力矩和关节范围。"],
    ],
    standards: [
      "安全检查永远位于推理与执行之间",
      "控制循环捕获超时并进入安全姿态",
      "先支架低速测试，再逐项提高动作范围",
    ],
  },
] as const;

const syncSequences = [
  [
    [0, "重置球场", "读取初始观察状态"],
    [1, "开始回合", "检查任务是否结束"],
    [2, "选择动作", "策略根据状态决定前进或踢球"],
    [3, "执行动作", "环境推进一步并返回奖励"],
    [4, "更新策略", "AI 从刚才的结果中学习"],
  ],
  [
    [0, "定义观察函数", "建立状态空间入口"],
    [2, "定位足球", "计算球相对机器人的横向距离"],
    [3, "定位足球", "计算球相对机器人的纵向距离"],
    [4, "定位球门", "计算球门相对足球的横向距离"],
    [6, "读取朝向", "把机器人角度加入状态"],
    [7, "输出状态", "向策略返回固定顺序的向量"],
  ],
  [
    [0, "计算时间成本", "每一步给予轻微惩罚"],
    [1, "接近足球", "距离缩短，获得正奖励"],
    [2, "触碰足球", "检测碰撞并奖励 +1"],
    [3, "推向球门", "足球朝球门移动，奖励增加"],
    [4, "完成进球", "触发本回合最高奖励 +100"],
  ],
  [
    [0, "加载 PPO", "导入强化学习算法"],
    [2, "创建球场", "实例化训练环境"],
    [3, "建立策略网络", "连接 MLP 策略与环境"],
    [4, "启用 MPS", "使用 Mac Apple Silicon 加速"],
    [5, "开始训练", "持续采集 500,000 步经验"],
    [6, "保存模型", "写出足球策略参数"],
  ],
  [
    [0, "检查成功率", "判断是否达到 80% 升级线"],
    [1, "解锁关卡", "提升等级并限制最高为 4"],
    [3, "扩大范围", "读取当前关卡的足球生成半径"],
    [4, "更新环境", "应用新的课程难度"],
  ],
  [
    [0, "建立差距清单", "收集仿真与现实参数"],
    [1, "测量摩擦", "读取真实地面摩擦"],
    [2, "加入电机延迟", "模拟命令到动作的等待时间"],
    [3, "限制相机频率", "模拟每秒 30 帧视觉输入"],
    [4, "加入位置噪声", "模拟视觉定位误差"],
  ],
  [
    [0, "开始随机化", "每回合生成一个新世界"],
    [1, "改变摩擦", "切换木板、草地、地毯和瓷砖"],
    [2, "改变质量", "模拟装配与电池重量差异"],
    [3, "改变功率", "模拟电机输出变化"],
    [4, "改变延迟", "模拟摄像头响应波动"],
  ],
  [
    [0, "导出模型", "生成可部署策略文件"],
    [1, "读取相机", "获取真实足球和球门状态"],
    [2, "策略推理", "计算机器人下一步动作"],
    [3, "安全限幅", "限制速度、力矩和关节范围"],
    [4, "执行动作", "MicroDuck 接近足球并射门"],
  ],
] as const;

const levels = [
  "学会走路",
  "学会找球",
  "学会踢球",
  "学会带球",
  "学会射门",
  "Sim2Real",
];

export function FootballCourse() {
  const [selected, setSelected] = useState(0);
  const [playing, setPlaying] = useState(true);
  const [tick, setTick] = useState(0);
  const episode = episodes[selected];

  useEffect(() => {
    if (!playing) return;
    const timer = window.setInterval(() => setTick((value) => value + 1), 1200);
    return () => window.clearInterval(timer);
  }, [playing]);

  useEffect(() => setTick(0), [selected]);

  const reward = useMemo(() => {
    if (selected === 2) return [0.1, 0.1, 1, 5, 100][tick % 5];
    return Math.min(96, 8 + tick * 3);
  }, [selected, tick]);
  const sequence = syncSequences[selected];
  const activeSync = sequence[tick % sequence.length];

  return (
    <section className="football-course">
      <div className="football-hero">
        <div>
          <span>MICRODUCK 系列课程 · 8 集 / 约 80 分钟</span>
          <h2>足球 AI 实战：从强化学习到 Sim2Real</h2>
          <p>
            使用 Mac mini M4 训练会踢球的 MicroDuck，并把策略迁移到真实机器人。
          </p>
          <div className="level-strip">
            {levels.map((level, index) => (
              <b key={level}>
                <i>{index + 1}</i>
                {level}
              </b>
            ))}
          </div>
        </div>
        <FootballAnimation
          episode={selected}
          tick={tick}
          reward={reward}
          playing={playing}
          action={activeSync[1]}
          effect={activeSync[2]}
        />
      </div>

      <nav className="episode-tabs" aria-label="课程选集">
        {episodes.map((item, index) => (
          <button
            className={selected === index ? "active" : ""}
            onClick={() => setSelected(index)}
            key={item.title}
          >
            <small>第 {index + 1} 集</small>
            <b>{item.label}</b>
          </button>
        ))}
      </nav>

      <div className="episode-heading">
        <div>
          <span>
            第 {selected + 1} 集 · {episode.duration}
          </span>
          <h3>{episode.title}</h3>
          <p>{episode.goal}</p>
        </div>
        <button onClick={() => setPlaying((value) => !value)}>
          {playing ? "❚❚ 暂停动画" : "▶ 播放动画"}
        </button>
      </div>

      <div className="course-grid">
        <article className="course-card narration">
          <span>配套视频脚本</span>
          <h4>旁白</h4>
          {episode.narration.map((line, index) => (
            <p key={line}>
              <i>{index + 1}</i>
              {line}
            </p>
          ))}
        </article>
        <article className="course-card storyboard">
          <span>动画分镜</span>
          <h4>镜头表</h4>
          {episode.shots.map((shot, index) => (
            <div key={shot}>
              <b>镜头 {index + 1}</b>
              <p>{shot}</p>
              <small>
                {index === 0
                  ? "全景 · 2 秒"
                  : index === episode.shots.length - 1
                    ? "特写 · 3 秒"
                    : "中景 · 2 秒"}
              </small>
            </div>
          ))}
        </article>
        <article className="course-card practice">
          <span>实操代码</span>
          <h4>本集实验</h4>
          <pre>
            <code className="synced-code" aria-label="同步执行代码">
              {episode.code.split("\n").map((line, index) => (
                <span
                  className={index === activeSync[0] ? "executing" : ""}
                  key={`${index}-${line}`}
                >
                  <i>{index + 1}</i>
                  <b>{line || " "}</b>
                  {index === activeSync[0] && <em>正在执行</em>}
                </span>
              ))}
            </code>
          </pre>
          <div className="execution-note" aria-live="polite">
            <b>当前动作：{activeSync[1]}</b>
            <span>{activeSync[2]}</span>
          </div>
          <button onClick={() => navigator.clipboard?.writeText(episode.code)}>
            复制代码
          </button>
        </article>
        <article className="course-card code-guide">
          <span>代码精讲</span>
          <h4>结构、语句含义与代码规范</h4>
          <div className="code-structure">
            <b>① 代码结构</b>
            <p>{codeGuides[selected].structure}</p>
          </div>
          <div className="statement-list">
            <b>② 关键语句逐句解释</b>
            {codeGuides[selected].statements.map(([statement, meaning]) => (
              <div key={statement}>
                <code>{statement}</code>
                <p>{meaning}</p>
              </div>
            ))}
          </div>
          <div className="code-standards">
            <b>③ 本集代码规范</b>
            <ul>
              {codeGuides[selected].standards.map((standard) => (
                <li key={standard}>{standard}</li>
              ))}
            </ul>
          </div>
        </article>
        <article className="course-card checklist">
          <span>学习检查</span>
          <h4>完成标准</h4>
          <label>
            <input type="checkbox" /> 能用一句话解释本集概念
          </label>
          <label>
            <input type="checkbox" /> 修改至少一个参数并预测结果
          </label>
          <label>
            <input type="checkbox" /> 播放动画并观察变化
          </label>
          <label>
            <input type="checkbox" /> 保存实验结果或截图
          </label>
        </article>
      </div>

      <div className="prompt-pack">
        <div>
          <span>AI 动画提示词</span>
          <h3>本集画面生成 Prompt</h3>
          <p>
            Cute yellow MicroDuck robot, small humanoid duck, soccer field,
            reinforcement learning visualization, futuristic laboratory, dynamic
            camera, cinematic lighting, bright educational 3D animation, 16:9,
            no text
          </p>
        </div>
        <button onClick={() => setSelected((selected + 1) % episodes.length)}>
          下一集 →
        </button>
      </div>
    </section>
  );
}

function FootballAnimation({
  episode,
  tick,
  reward,
  playing,
  action,
  effect,
}: {
  episode: number;
  tick: number;
  reward: number;
  playing: boolean;
  action: string;
  effect: string;
}) {
  const progress = (tick % 9) / 8;
  const duckX =
    episode === 5 ? 170 + Math.sin(tick) * 25 : 100 + progress * 470;
  const ballX = progress > 0.55 ? 390 + (progress - 0.55) * 570 : 390;
  const terrain =
    episode === 6 ? ["木地板", "草地", "地毯", "瓷砖"][tick % 4] : "训练草坪";
  return (
    <div
      className={`football-animation episode-${episode} ${playing ? "playing" : "paused"}`}
    >
      <div className="action-overlay" aria-live="polite">
        <small>动画与代码同步</small>
        <b>{action}</b>
        <span>{effect}</span>
      </div>
      <svg viewBox="0 0 720 390" role="img" aria-label="MicroDuck 足球训练动画">
        <defs>
          <linearGradient id="sky" x2="0" y2="1">
            <stop stopColor="#bdeeff" />
            <stop offset="1" stopColor="#efffd8" />
          </linearGradient>
          <filter id="glow">
            <feGaussianBlur stdDeviation="5" result="b" />
            <feMerge>
              <feMergeNode in="b" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>
        <rect width="720" height="390" rx="22" fill="url(#sky)" />
        <rect
          y="220"
          width="720"
          height="170"
          fill={
            episode === 6
              ? ["#bd925e", "#55a85d", "#8b6c58", "#d8d8d3"][tick % 4]
              : "#55a85d"
          }
        />
        <path d="M20 300H700M360 220V390" stroke="#ffffff88" strokeWidth="3" />
        <circle
          cx="360"
          cy="305"
          r="55"
          fill="none"
          stroke="#ffffff88"
          strokeWidth="3"
        />
        <path
          d="M650 242h48v105h-48z"
          fill="none"
          stroke="white"
          strokeWidth="6"
        />
        {episode === 5 && (
          <>
            <rect
              x="360"
              width="360"
              height="220"
              fill="#18263b"
              opacity=".2"
            />
            <text x="180" y="45">
              仿真世界
            </text>
            <text x="535" y="45">
              真实世界
            </text>
          </>
        )}
        {episode === 6 && (
          <text x="28" y="45" className="terrain">
            世界随机化：{terrain}
          </text>
        )}
        <g transform={`translate(${duckX} 260)`} className="football-duck">
          <ellipse rx="38" ry="27" fill="#ffd333" />
          <circle cx="31" cy="-30" r="23" fill="#ffe05c" />
          <path d="M51-33l28 10-28 10z" fill="#f47c28" />
          <circle cx="38" cy="-37" r="4" fill="#18334a" />
          <path
            d="M-18 22l-9 33M16 22l12 33"
            stroke="#f47c28"
            strokeWidth="8"
            strokeLinecap="round"
          />
        </g>
        <g
          transform={`translate(${Math.min(ballX, 655)} 315)`}
          className="football-ball"
        >
          <circle r="19" fill="white" stroke="#17324d" strokeWidth="3" />
          <path d="M0-8l8 6-3 10h-10l-3-10z" fill="#17324d" />
        </g>
        {episode === 2 && (
          <text
            x={duckX + 25}
            y="185"
            className={reward < 0 ? "reward bad" : "reward"}
          >
            +{reward}
          </text>
        )}
        {episode === 3 && (
          <>
            <polyline
              points={`30,170 110,${165 - progress * 25} 190,${150 - progress * 30} 270,${145 - progress * 50} 350,${120 - progress * 55} 430,${110 - progress * 65} 520,${90 - progress * 60} 620,${65 - progress * 45}`}
              fill="none"
              stroke="#ffcf33"
              strokeWidth="7"
            />
            <text x="30" y="100">
              Episode {Math.round(1 + progress * 5000)}
            </text>
          </>
        )}
        {episode === 4 && (
          <g>
            {[1, 2, 3, 4].map((n) => (
              <g key={n}>
                <circle
                  cx={130 + n * 110}
                  cy="80"
                  r="28"
                  fill={n <= 1 + (tick % 4) ? "#ffd333" : "#ffffff99"}
                />
                <text x={130 + n * 110} y="87" textAnchor="middle">
                  L{n}
                </text>
              </g>
            ))}
          </g>
        )}
        {episode === 7 && progress > 0.72 && (
          <g filter="url(#glow)">
            <text x="585" y="175" className="goal-text">
              GOAL!
            </text>
            <path
              d="M610 120l8 18 20 2-15 13 5 20-18-10-18 10 5-20-15-13 20-2z"
              fill="#ffd333"
            />
          </g>
        )}
        <rect x="20" y="338" width="265" height="34" rx="17" fill="#102c43dd" />
        <text x="38" y="361" className="hud">
          {playing ? "● 训练动画运行中" : "❚❚ 动画已暂停"} · Reward{" "}
          {Number(reward).toFixed(1)}
        </text>
      </svg>
    </div>
  );
}
