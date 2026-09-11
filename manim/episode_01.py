"""第一集：让鸭子学会踢足球——10 分钟 Manim 动画。

渲染：manim -c manim/manim.cfg manim/episode_01.py EpisodeOne
"""

from dataclasses import dataclass
from typing import Callable

from manim import *


FONT = "Noto Sans CJK SC"
NAVY = "#102C43"
YELLOW = "#FFD333"
GREEN = "#35D49A"
GRASS = "#4F9E5B"
ORANGE = "#F47C28"
MUTED = "#B8D1DC"


@dataclass(frozen=True)
class SceneSpec:
    number: int
    duration: int
    title: str
    narration: str
    visual: str


SCENES = (
    SceneSpec(1, 20, "它真的能自己学会吗？", "如果完全不告诉机器人踢球规则，它还能自己学会射门吗？", "confused"),
    SceneSpec(2, 25, "失败 → 尝试 → 进球", "它会走反、转圈、踢空，但一次次尝试之后，结果开始改变。", "attempts"),
    SceneSpec(3, 30, "MicroDuck 足球强化学习课程", "我们将从仿真环境出发，训练策略，最后迁移到真实机器人。", "title"),
    SceneSpec(4, 35, "传统方法：手写规则", "球在左边就左转，球在右边就右转，球在脚边就踢。", "rules"),
    SceneSpec(5, 30, "现实马上来拆台", "球可能在身后，地面会变滑，摄像头还可能慢半拍。", "chaos"),
    SceneSpec(6, 35, "强化学习的另一条路", "定义它看见什么、能做什么，以及什么结果值得奖励。", "questions"),
    SceneSpec(7, 40, "Agent · 智能体", "做决定和学习的角色，就是 MicroDuck。", "agent"),
    SceneSpec(8, 40, "Environment · 环境", "足球场、球门、足球以及物理规律共同组成环境。", "environment"),
    SceneSpec(9, 35, "Observation · 观察状态", "球的相对位置、球门方向和机器人朝向组成策略输入。", "observation"),
    SceneSpec(10, 35, "Action · 动作", "第一版只提供前进、左转、右转和踢球四个动作。", "actions"),
    SceneSpec(11, 40, "Reward · 奖励", "接近球、碰到球、踢动球会加分，进球得到最高奖励。", "reward"),
    SceneSpec(12, 35, "强化学习循环", "观察、动作、奖励、学习，然后再观察。", "loop"),
    SceneSpec(13, 40, "动画与代码同步", "reset 开启回合，策略选择动作，step 推进环境并返回反馈。", "code"),
    SceneSpec(14, 35, "结束并不只有一种", "terminated 是自然结束，truncated 是达到最大步数。", "termination"),
    SceneSpec(15, 35, "只有进球奖励，会怎样？", "随机策略可能几十万次都碰不到球，这就是奖励稀疏。", "sparse"),
    SceneSpec(16, 30, "像游戏一样拆成六关", "移动、找球、接近、带球、射门，最后进入 Sim2Real。", "levels"),
    SceneSpec(17, 30, "完整技术路线", "Gymnasium、PPO、固定评估、域随机化，再到真实 MicroDuck。", "pipeline"),
    SceneSpec(18, 30, "下一集：创建足球训练场", "强化学习通过状态、动作和奖励，系统地学习策略。", "finale"),
)


class EpisodeOne(Scene):
    """18 场、总计 600 秒的第一集动画。"""

    def construct(self) -> None:
        self.camera.background_color = NAVY
        for spec in SCENES:
            slide, focus = self.build_slide(spec)
            self.play(FadeIn(slide, shift=UP * 0.12), run_time=1.0)
            self.play(Indicate(focus, color=YELLOW, scale_factor=1.04), run_time=3.0)
            self.wait(spec.duration - 4.5)
            self.play(FadeOut(slide), run_time=0.5)

    def build_slide(self, spec: SceneSpec) -> tuple[VGroup, Mobject]:
        scene_badge = Text(
            f"SCENE {spec.number:02d}  ·  10:00",
            font=FONT,
            font_size=20,
            color=GREEN,
        ).to_corner(UL, buff=0.35)
        title = Text(spec.title, font=FONT, font_size=38, weight=BOLD, color=WHITE)
        title.to_edge(UP, buff=0.62)
        visual = self.visual_for(spec.visual).scale_to_fit_height(3.8).move_to(UP * 0.15)
        subtitle_bg = RoundedRectangle(
            width=12.7,
            height=1.05,
            corner_radius=0.16,
            fill_color="#061723",
            fill_opacity=0.94,
            stroke_color="#2E5368",
            stroke_width=1,
        ).to_edge(DOWN, buff=0.28)
        subtitle = Text(spec.narration, font=FONT, font_size=24, color=WHITE)
        subtitle.scale_to_fit_width(11.9).move_to(subtitle_bg)
        progress = Rectangle(
            width=13.4 * spec.number / len(SCENES),
            height=0.06,
            fill_color=YELLOW,
            fill_opacity=1,
            stroke_width=0,
        ).align_to(config.frame_x_radius * LEFT, LEFT).to_edge(DOWN, buff=0)
        return VGroup(scene_badge, title, visual, subtitle_bg, subtitle, progress), visual

    def visual_for(self, kind: str) -> Mobject:
        builders: dict[str, Callable[[], Mobject]] = {
            "confused": lambda: self.pitch(duck_x=-2.2, ball_x=0.1, mood="?"),
            "attempts": self.attempts,
            "title": self.course_title,
            "rules": self.rules,
            "chaos": self.chaos,
            "questions": self.questions,
            "agent": lambda: VGroup(self.duck().scale(1.6), self.label("AGENT", YELLOW).next_to(ORIGIN, RIGHT, buff=1.6)),
            "environment": lambda: VGroup(self.pitch().scale(0.95), SurroundingRectangle(self.pitch().scale(0.95), color=GREEN)),
            "observation": self.observation,
            "actions": self.actions,
            "reward": self.rewards,
            "loop": self.learning_loop,
            "code": self.code_sync,
            "termination": self.termination,
            "sparse": self.sparse_reward,
            "levels": self.levels,
            "pipeline": self.pipeline,
            "finale": lambda: VGroup(self.pitch(duck_x=0.8, ball_x=2.4), self.label("GOAL!", YELLOW).shift(UP * 1.5)),
        }
        return builders[kind]()

    def duck(self) -> VGroup:
        body = Ellipse(width=1.0, height=0.65, fill_color=YELLOW, fill_opacity=1, stroke_width=0)
        head = Circle(0.32, fill_color="#FFE266", fill_opacity=1, stroke_width=0).shift(RIGHT * 0.42 + UP * 0.42)
        beak = Triangle(fill_color=ORANGE, fill_opacity=1, stroke_width=0).scale(0.19).rotate(-PI / 2).shift(RIGHT * 0.83 + UP * 0.39)
        eye = Dot(radius=0.045, color=NAVY).shift(RIGHT * 0.51 + UP * 0.52)
        legs = VGroup(Line(DOWN * 0.25, DOWN * 0.68 + LEFT * 0.13, color=ORANGE, stroke_width=7), Line(DOWN * 0.25 + RIGHT * 0.25, DOWN * 0.68 + RIGHT * 0.38, color=ORANGE, stroke_width=7))
        return VGroup(body, head, beak, eye, legs)

    def ball(self) -> VGroup:
        return VGroup(Circle(0.25, fill_color=WHITE, fill_opacity=1, stroke_color=NAVY), RegularPolygon(5, radius=0.12, fill_color=NAVY, fill_opacity=1, stroke_width=0))

    def pitch(self, duck_x: float = -1.8, ball_x: float = 0.4, mood: str = "") -> VGroup:
        field = RoundedRectangle(width=8.5, height=3.7, corner_radius=0.18, fill_color=GRASS, fill_opacity=1, stroke_color=WHITE)
        center = Circle(0.7, color=WHITE).move_to(field)
        line = Line(UP * 1.85, DOWN * 1.85, color=WHITE)
        goal = Rectangle(width=0.55, height=1.55, color=WHITE).move_to(RIGHT * 4.0)
        duck = self.duck().scale(0.7).move_to(RIGHT * duck_x + DOWN * 0.4)
        ball = self.ball().scale(0.75).move_to(RIGHT * ball_x + DOWN * 0.48)
        group = VGroup(field, center, line, goal, duck, ball)
        if mood:
            group.add(Text(mood, font=FONT, font_size=42, color=YELLOW).next_to(duck, UP))
        return group

    def label(self, text: str, color: str = WHITE) -> Text:
        return Text(text, font=FONT, font_size=28, color=color, weight=BOLD)

    def attempts(self) -> VGroup:
        cards = VGroup(*[self.pitch(duck_x=-1.6 + i * 0.3, ball_x=0.2 + i * 0.4).scale(0.34) for i in range(3)]).arrange(RIGHT, buff=0.3)
        rewards = VGroup(self.label("−1", RED), self.label("+1", GREEN), self.label("+100", YELLOW)).arrange(RIGHT, buff=2.2).next_to(cards, UP)
        return VGroup(cards, rewards)

    def course_title(self) -> VGroup:
        icons = VGroup(self.label("Gymnasium", GREEN), self.label("PPO", YELLOW), self.label("Sim2Real", "#6CCBFF")).arrange(RIGHT, buff=0.65)
        return VGroup(self.duck().scale(1.5), icons.next_to(ORIGIN, DOWN, buff=1.4))

    def rules(self) -> VGroup:
        code = VGroup(*[
            Code(
                code_string=line,
                language="Python",
                background="window",
                paragraph_config={"font_size": 16},
            )
            for line in [
                "if ball_left: turn_left()",
                "elif ball_right: turn_right()",
                "elif ball_close: kick()",
            ]
        ]).arrange(DOWN, buff=0.12)
        return VGroup(code.scale(0.7).shift(LEFT * 2.7), self.pitch().scale(0.55).shift(RIGHT * 2.2))

    def chaos(self) -> VGroup:
        surfaces = VGroup(*[self.label(x, color) for x, color in [("GRASS", GREEN), ("WOOD", "#D39B62"), ("CARPET", "#A97B68")]]).arrange(RIGHT)
        return VGroup(self.duck().scale(1.25).shift(DOWN * 0.5), surfaces.shift(UP * 1.2), Cross(stroke_color=RED).scale(0.8).shift(RIGHT * 2.4))

    def questions(self) -> VGroup:
        duck = self.duck().scale(1.4)
        cards = VGroup(*[self.label(x, color) for x, color in [("SEE?", "#6CCBFF"), ("DO?", YELLOW), ("GOOD?", GREEN)]]).arrange_in_grid(rows=1, buff=1.0).next_to(duck, DOWN, buff=1.0)
        return VGroup(duck, cards)

    def observation(self) -> VGroup:
        pitch = self.pitch()
        vectors = VGroup(Arrow(LEFT * 1.8, RIGHT * 0.4, color=GREEN), Arrow(RIGHT * 0.4, RIGHT * 3.6, color="#6CCBFF")).shift(DOWN * 0.4)
        return VGroup(pitch, vectors)

    def actions(self) -> VGroup:
        return VGroup(*[VGroup(self.duck().scale(0.55), self.label(x, YELLOW).scale(0.55).next_to(ORIGIN, DOWN)) for x in ["FORWARD", "LEFT", "RIGHT", "KICK"]]).arrange(RIGHT, buff=0.65)

    def rewards(self) -> VGroup:
        return VGroup(self.pitch().scale(0.72), VGroup(*[self.label(x, c) for x, c in [("+0.1", GREEN), ("+1", GREEN), ("+2", GREEN), ("+100", YELLOW)]]).arrange(RIGHT).shift(UP * 1.4))

    def learning_loop(self) -> VGroup:
        labels = ["OBSERVE", "CHOOSE", "ACT", "REWARD", "LEARN"]
        nodes = VGroup(*[Circle(0.55, fill_color="#174E68", fill_opacity=1, stroke_color=GREEN).add(self.label(x).scale(0.42)) for x in labels])
        nodes.arrange_in_grid(rows=1, buff=0.28)
        arrows = VGroup(*[Arrow(nodes[i].get_right(), nodes[i + 1].get_left(), color=YELLOW, buff=0.06) for i in range(4)])
        return VGroup(nodes, arrows)

    def code_sync(self) -> VGroup:
        pitch = self.pitch().scale(0.55).shift(LEFT * 2.3)
        code = Code(
            code_string="observation, info = env.reset()\naction = policy.predict(observation)\nobservation, reward, terminated, truncated, info = env.step(action)",
            language="Python",
            background="window",
            paragraph_config={"font_size": 18},
        ).scale(0.72).shift(RIGHT * 2.4)
        return VGroup(pitch, code, Arrow(pitch.get_right(), code.get_left(), color=YELLOW))

    def termination(self) -> VGroup:
        return VGroup(VGroup(self.ball(), self.label("TERMINATED", GREEN).next_to(ORIGIN, DOWN)).shift(LEFT * 2), VGroup(Circle(0.55, color=YELLOW), self.label("TRUNCATED", YELLOW).next_to(ORIGIN, DOWN)).shift(RIGHT * 2))

    def sparse_reward(self) -> VGroup:
        pitch = self.pitch(duck_x=-3.0, ball_x=2.0)
        paths = VGroup(*[VMobject(stroke_color="#A5B9C2", stroke_opacity=0.25).set_points_smoothly([LEFT * 3 + DOWN * 0.5, LEFT * (2-i*0.1) + UP * ((i%3)-1), RIGHT * (i%2)]) for i in range(12)])
        return VGroup(pitch, paths)

    def levels(self) -> VGroup:
        names = ["MOVE", "FIND", "APPROACH", "DRIBBLE", "SCORE", "SIM2REAL"]
        circles = VGroup(*[Circle(0.48, fill_color=YELLOW if i < 5 else GREEN, fill_opacity=1, stroke_width=0).add(Text(str(i+1), font=FONT, color=NAVY, font_size=25)) for i in range(6)]).arrange(RIGHT, buff=0.5)
        labels = VGroup(*[self.label(x, WHITE).scale(0.36) for x in names]).arrange(RIGHT, buff=0.48).next_to(circles, DOWN)
        return VGroup(circles, labels)

    def pipeline(self) -> VGroup:
        labels = ["GYM", "STATE", "PPO", "EVAL", "RANDOM", "ROBOT"]
        boxes = VGroup(*[RoundedRectangle(width=1.25, height=0.8, corner_radius=0.12, fill_color="#174E68", fill_opacity=1, stroke_color=GREEN).add(self.label(x).scale(0.42)) for x in labels]).arrange(RIGHT, buff=0.28)
        arrows = VGroup(*[Arrow(boxes[i].get_right(), boxes[i+1].get_left(), color=YELLOW, buff=0.04) for i in range(5)])
        return VGroup(boxes, arrows)


if __name__ == "__main__":
    assert sum(scene.duration for scene in SCENES) == 600
