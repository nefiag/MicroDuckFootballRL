"""MuJoCo + 强化学习机器人 AI 训练课程，10 分钟 Manim 动画。"""

from dataclasses import dataclass
from math import sin

from manim import *


FONT = "Noto Sans CJK SC"
NAVY = "#102C43"
YELLOW = "#FFD333"
GREEN = "#35D49A"
BLUE = "#48A9E6"
ORANGE = "#F47C28"
MUTED = "#B8D1DC"


@dataclass(frozen=True)
class Slide:
    number: int
    duration: int
    title: str
    subtitle: str
    kind: str


SLIDES = (
    Slide(1, 25, "MuJoCo × 强化学习", "先仿真后控制，先认知后优化。", "opening"),
    Slide(2, 30, "四个核心模块", "建模、环境、训练、Sim-to-Real，组成完整学习闭环。", "modules"),
    Slide(3, 35, "MJCF：机器人的数字骨架", "XML 文件定义 body、joint、geom 与 actuator。", "mjcf"),
    Slide(4, 35, "关节、执行器与碰撞体", "关节决定怎样动，执行器提供力，Geom 负责接触与碰撞。", "parts"),
    Slide(5, 30, "自由度、运动学与物理", "理解 DoF、正逆运动学，以及重力和摩擦如何改变动作。", "physics"),
    Slide(6, 35, "状态空间 Sₜ", "关节角、角速度和机身倾角，构成策略看到的观察向量。", "state"),
    Slide(7, 35, "动作空间 Aₜ", "策略输出电机控制量或目标角度，并限制在安全范围。", "action"),
    Slide(8, 35, "MDP 交互循环", "状态、动作、奖励和下一状态，共同描述一次决策。", "mdp"),
    Slide(9, 35, "封装 Gymnasium 环境", "reset 初始化回合，step 执行动作并返回训练反馈。", "gym"),
    Slide(10, 40, "奖励函数：告诉机器人什么是好", "前进速度加分；能耗、倾斜、抖动和摔倒扣分。", "reward"),
    Slide(11, 35, "第一关：站立与平衡", "先让 MicroDuck 抵抗扰动站稳，再考虑向前走。", "balance"),
    Slide(12, 35, "PPO 与 SAC", "PPO 稳定易用；SAC 适合连续动作且样本利用率高。", "algorithms"),
    Slide(13, 35, "行走、转向与目标指令", "把目标方向加入观察，让策略学会按指令改变运动。", "goal"),
    Slide(14, 30, "动作裁剪与安全边界", "网络输出必须经过缩放和裁剪，避免超出电机能力。", "clip"),
    Slide(15, 35, "AI Co-pilot 辅助调参", "结合 TensorBoard 曲线、日志和 MJCF，让 AI 帮助定位问题。", "copilot"),
    Slide(16, 35, "域随机化", "每次 reset 随机质量、摩擦、延迟和噪声，提高现实适应性。", "randomization"),
    Slide(17, 30, "ONNX 与 Sim-to-Real", "导出策略，在控制板上执行，并从低速支架测试开始。", "deploy"),
    Slide(18, 30, "梯级挑战路线", "站稳、直行、转向避障，再创造属于你的花样动作。", "finale"),
)


class MujocoRLCourse(Scene):
    """18 个场景，总时长严格为 600 秒。"""

    def construct(self) -> None:
        self.camera.background_color = NAVY
        watermark = Text(
            "制作 by 黄旭", font=FONT, font_size=18, color=WHITE
        ).set_opacity(0.72).to_corner(UL, buff=0.25).set_z_index(100)
        self.add(watermark)
        for spec in SLIDES:
            slide, focus = self.build_slide(spec)
            self.play(FadeIn(slide, shift=UP * 0.12), run_time=1)
            self.play(Indicate(focus, color=YELLOW, scale_factor=1.035), run_time=3)
            self.wait(spec.duration - 4.5)
            self.play(FadeOut(slide), run_time=0.5)

    def build_slide(self, spec: Slide) -> tuple[VGroup, Mobject]:
        badge = Text(
            f"MODULE · {spec.number:02d} / 18",
            font=FONT, font_size=19, color=GREEN,
        ).to_corner(UL, buff=0.35).shift(DOWN * 0.42)
        title = Text(spec.title, font=FONT, font_size=38, weight=BOLD, color=WHITE)
        title.to_edge(UP, buff=0.62)
        visual = self.visual(spec.kind)
        if visual.height > 3.75:
            visual.scale_to_fit_height(3.75)
        if visual.width > 11.6:
            visual.scale_to_fit_width(11.6)
        visual.move_to(UP * 0.12)
        subtitle_bg = RoundedRectangle(
            width=12.7, height=1.05, corner_radius=0.16,
            fill_color="#061723", fill_opacity=0.94,
            stroke_color="#2E5368", stroke_width=1,
        ).to_edge(DOWN, buff=0.28)
        subtitle = Text(spec.subtitle, font=FONT, font_size=24, color=WHITE)
        subtitle.scale_to_fit_width(11.8).move_to(subtitle_bg)
        progress = Rectangle(
            width=13.4 * spec.number / len(SLIDES), height=0.06,
            fill_color=YELLOW, fill_opacity=1, stroke_width=0,
        ).align_to(config.frame_x_radius * LEFT, LEFT).to_edge(DOWN, buff=0)
        return VGroup(badge, title, visual, subtitle_bg, subtitle, progress), visual

    def label(self, text: str, color: str = WHITE, size: int = 27) -> Text:
        return Text(text, font=FONT, font_size=size, color=color, weight=BOLD)

    def card(self, text: str, color: str = BLUE, width: float = 2.6) -> VGroup:
        box = RoundedRectangle(
            width=width, height=0.9, corner_radius=0.15,
            fill_color=color, fill_opacity=0.18, stroke_color=color,
        )
        label = self.label(text, color, 24).scale_to_fit_width(width - 0.25)
        return VGroup(box, label)

    def row(self, *items: str, color: str = BLUE) -> VGroup:
        return VGroup(*(self.card(item, color) for item in items)).arrange(RIGHT, buff=0.35)

    def arrows(self, items: list[str], colors: list[str] | None = None) -> VGroup:
        colors = colors or [BLUE] * len(items)
        cards = [self.card(item, colors[i], 2.25) for i, item in enumerate(items)]
        group = VGroup()
        for i, card in enumerate(cards):
            group.add(card)
            if i < len(cards) - 1:
                group.add(Arrow(LEFT, RIGHT, color=MUTED, buff=0, max_tip_length_to_length_ratio=0.18))
        return group.arrange(RIGHT, buff=0.18)

    def visual(self, kind: str) -> Mobject:
        if kind == "opening":
            duck = self.robot_duck().scale(1.2)
            brain = Circle(0.62, color=GREEN).add(self.label("AI", GREEN, 30)).next_to(duck, RIGHT, buff=1)
            return VGroup(duck, Arrow(duck.get_right(), brain.get_left(), color=YELLOW), brain)
        if kind == "modules":
            return VGroup(
                self.row("1  MuJoCo 建模", "2  RL 环境", color=BLUE),
                self.row("3  策略训练", "4  Sim-to-Real", color=GREEN),
            ).arrange(DOWN, buff=0.45)
        if kind == "mjcf":
            tree = VGroup(
                self.card("<mujoco>", GREEN, 3.0),
                self.row("<worldbody>", "<actuator>", color=BLUE),
                self.row("<body>", "<joint>", "<geom>", color=ORANGE),
            ).arrange(DOWN, buff=0.35)
            return tree
        if kind == "parts":
            return self.arrows(["Joint\n运动约束", "Actuator\n驱动力", "Geom\n碰撞接触"], [BLUE, ORANGE, GREEN])
        if kind == "physics":
            return VGroup(
                self.row("DoF 自由度", "FK / IK", color=BLUE),
                self.row("重力 ↓", "摩擦力 ↔", color=ORANGE),
            ).arrange(DOWN, buff=0.45)
        if kind == "state":
            vector = self.card("[ q₁,  dq₁,  pitch,  roll ]", BLUE, 4.5)
            return VGroup(self.label("Sₜ =", GREEN, 36), vector, self.card("策略的眼睛", GREEN)).arrange(RIGHT, buff=0.5)
        if kind == "action":
            return self.arrows(["策略网络", "Aₜ ∈ [-1, 1]", "电机目标角"], [GREEN, YELLOW, ORANGE])
        if kind == "mdp":
            nodes = VGroup(*(self.card(t, c, 2.1) for t, c in [
                ("状态 Sₜ", BLUE), ("动作 Aₜ", YELLOW), ("奖励 Rₜ", GREEN), ("下一状态", ORANGE)
            ])).arrange(RIGHT, buff=0.3)
            links = VGroup(*(Arrow(nodes[i].get_right(), nodes[i + 1].get_left(), color=WHITE, buff=0.08) for i in range(3)))
            return VGroup(nodes, links)
        if kind == "gym":
            code = Code(
                code_string="class MicroDuckEnv(gym.Env):\n    def reset(self, seed=None): ...\n    def step(self, action): ...",
                language="Python", background="window",
                paragraph_config={"font_size": 22},
            )
            return code
        if kind == "reward":
            return VGroup(
                self.row("+ 前进速度", "+ 保持站立", color=GREEN),
                self.row("− 能耗", "− 倾斜/抖动", "− 摔倒", color=ORANGE),
            ).arrange(DOWN, buff=0.45)
        if kind == "balance":
            duck = self.robot_duck().scale(1.35)
            pushes = VGroup(
                Arrow(LEFT * 2.3, LEFT * 0.7, color=ORANGE),
                Arrow(RIGHT * 2.3, RIGHT * 0.7, color=ORANGE),
            )
            ground = Line(LEFT * 3, RIGHT * 3, color=GREEN).shift(DOWN * 1.15)
            return VGroup(duck, pushes, ground)
        if kind == "algorithms":
            return self.row("PPO\n稳定 · 易调", "SAC\n连续 · 高效", color=GREEN)
        if kind == "goal":
            duck = self.robot_duck().shift(LEFT * 2.5)
            goal = Star(5, outer_radius=0.55, color=YELLOW, fill_opacity=0.4).shift(RIGHT * 2.7)
            direction = Arrow(duck.get_right(), goal.get_left(), color=GREEN)
            return VGroup(duck, direction, goal, self.label("Goal Direction", GREEN, 24).next_to(direction, UP))
        if kind == "clip":
            return self.arrows(["网络输出\n1.73", "clip", "安全动作\n1.00"], [BLUE, ORANGE, GREEN])
        if kind == "copilot":
            chart = Axes(x_range=[0, 5], y_range=[0, 4], x_length=4, y_length=2.5, tips=False)
            curve = chart.plot(lambda x: 0.6 + 0.45 * x + 0.35 * sin(4 * x), color=GREEN)
            chat = self.card("AI：检查倾斜惩罚\n与目标方向权重", YELLOW, 4.0)
            return VGroup(VGroup(chart, curve), chat).arrange(RIGHT, buff=0.6)
        if kind == "randomization":
            return VGroup(
                self.row("质量", "摩擦", "电机功率", color=BLUE),
                self.row("延迟", "观测噪声", color=ORANGE),
                self.label("每次 reset 自动随机", GREEN, 26),
            ).arrange(DOWN, buff=0.4)
        if kind == "deploy":
            return self.arrows(["MuJoCo", "PPO 权重", "ONNX", "MicroDuck"], [BLUE, GREEN, YELLOW, ORANGE])
        return VGroup(
            self.arrows(["站稳", "直行", "转向避障", "花样动作"], [BLUE, GREEN, YELLOW, ORANGE]),
            self.label("观察 → 修改 → 再训练", GREEN, 28),
        ).arrange(DOWN, buff=0.6)

    def robot_duck(self) -> VGroup:
        body = RoundedRectangle(
            width=1.35, height=1.15, corner_radius=0.28,
            fill_color=YELLOW, fill_opacity=1, stroke_color=WHITE,
        )
        head = Circle(0.43, fill_color="#FFE266", fill_opacity=1, stroke_width=0).next_to(body, UP, buff=-0.05)
        eye = Dot(radius=0.055, color=NAVY).move_to(head).shift(RIGHT * 0.14 + UP * 0.08)
        beak = Triangle(fill_color=ORANGE, fill_opacity=1, stroke_width=0).scale(0.2).rotate(-PI / 2).next_to(head, RIGHT, buff=-0.08)
        legs = VGroup(
            Line(body.get_bottom() + LEFT * 0.3, body.get_bottom() + LEFT * 0.42 + DOWN * 0.65, color=ORANGE, stroke_width=8),
            Line(body.get_bottom() + RIGHT * 0.3, body.get_bottom() + RIGHT * 0.42 + DOWN * 0.65, color=ORANGE, stroke_width=8),
        )
        joints = VGroup(*(Dot(line.get_start(), radius=0.07, color=BLUE) for line in legs))
        return VGroup(body, head, eye, beak, legs, joints)
