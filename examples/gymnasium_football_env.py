"""MicroDuck 足球 Gymnasium 环境。

安装：pip install gymnasium numpy
运行：python examples/gymnasium_football_env.py
"""

from dataclasses import dataclass
from enum import IntEnum
from math import atan2, cos, hypot, pi, sin
from typing import Any

import gymnasium as gym
import numpy as np
from gymnasium import spaces


@dataclass
class MicroDuck:
    """MicroDuck 的二维位姿。"""

    x: float
    y: float
    angle: float
    radius: float = 0.14


@dataclass
class Ball:
    """足球的位置、速度和半径。"""

    x: float
    y: float
    vx: float = 0.0
    vy: float = 0.0
    radius: float = 0.09


@dataclass(frozen=True)
class Goal:
    """球门位于球场右侧，y 表示球门中心。"""

    x: float
    y: float
    width: float


class Action(IntEnum):
    """离散动作编号。"""

    FORWARD = 0
    TURN_LEFT = 1
    TURN_RIGHT = 2
    KICK = 3


class MicroDuckFootballEnv(gym.Env[np.ndarray, int]):
    """使用 Gymnasium API 的二维足球环境。

    观测向量共 10 项：
    [
        duck_x, duck_y,
        sin(duck_angle), cos(duck_angle),
        ball_x - duck_x, ball_y - duck_y,
        goal_x - ball_x, goal_y - ball_y,
        ball_vx, ball_vy,
    ]

    动作：前进、左转、右转、踢球。
    奖励：接近球、首次碰到球、踢动球、进球。
    """

    metadata = {"render_modes": ["ansi", "rgb_array"], "render_fps": 20}

    FIELD_X_LIMIT = 3.2
    FIELD_Y_LIMIT = 1.8
    MAX_BALL_SPEED = 0.45

    def __init__(
        self,
        render_mode: str | None = None,
        max_steps: int = 400,
    ) -> None:
        super().__init__()
        if render_mode not in self.metadata["render_modes"] and render_mode is not None:
            raise ValueError(f"不支持 render_mode={render_mode!r}")

        self.render_mode = render_mode
        self.max_steps = max_steps
        self.action_space = spaces.Discrete(len(Action))
        self.observation_space = spaces.Box(
            low=np.array(
                [-3.2, -1.8, -1.0, -1.0, -6.4, -3.6, -6.4, -3.6, -0.45, -0.45],
                dtype=np.float32,
            ),
            high=np.array(
                [3.2, 1.8, 1.0, 1.0, 6.4, 3.6, 6.4, 3.6, 0.45, 0.45],
                dtype=np.float32,
            ),
            dtype=np.float32,
        )

        self.goal = Goal(x=3.0, y=0.0, width=1.0)
        self.duck = MicroDuck(x=-2.0, y=0.0, angle=0.0)
        self.ball = Ball(x=0.0, y=0.0)
        self.steps = 0
        self.has_touched_ball = False

    def reset(
        self,
        *,
        seed: int | None = None,
        options: dict[str, Any] | None = None,
    ) -> tuple[np.ndarray, dict[str, Any]]:
        """重置一个回合，并返回 `(observation, info)`。"""

        super().reset(seed=seed)
        options = options or {}

        self.duck = MicroDuck(
            x=float(options.get("duck_x", self.np_random.uniform(-2.6, -1.4))),
            y=float(options.get("duck_y", self.np_random.uniform(-0.8, 0.8))),
            angle=float(options.get("duck_angle", self.np_random.uniform(-0.35, 0.35))),
        )
        self.ball = Ball(
            x=float(options.get("ball_x", self.np_random.uniform(-0.4, 1.0))),
            y=float(options.get("ball_y", self.np_random.uniform(-1.0, 1.0))),
        )
        self.steps = 0
        self.has_touched_ball = False
        return self._get_observation(), self._get_info()

    def step(
        self,
        action: int,
    ) -> tuple[np.ndarray, float, bool, bool, dict[str, Any]]:
        """执行一个动作，返回 Gymnasium 标准五元组。"""

        if not self.action_space.contains(action):
            raise ValueError(f"动作必须为 0–{self.action_space.n - 1}，收到 {action}")

        previous_duck_ball_distance = self._duck_ball_distance()
        previous_ball_x = self.ball.x
        reward_terms = {
            "approach_ball": 0.0,
            "touch_ball": 0.0,
            "move_ball": 0.0,
            "score_goal": 0.0,
        }

        if action == Action.FORWARD:
            self._move_forward()
        elif action == Action.TURN_LEFT:
            self.duck.angle = self._wrap_angle(self.duck.angle + 0.16)
        elif action == Action.TURN_RIGHT:
            self.duck.angle = self._wrap_angle(self.duck.angle - 0.16)
        elif action == Action.KICK:
            self._kick_ball()

        touching = self._duck_ball_distance() <= self.duck.radius + self.ball.radius
        if touching and not self.has_touched_ball:
            reward_terms["touch_ball"] = 1.0
            self.has_touched_ball = True

        self._advance_ball_physics()
        self.steps += 1

        current_distance = self._duck_ball_distance()
        distance_progress = previous_duck_ball_distance - current_distance
        reward_terms["approach_ball"] = float(np.clip(distance_progress * 2.0, -0.2, 0.2))

        ball_progress = self.ball.x - previous_ball_x
        if ball_progress > 0.005:
            reward_terms["move_ball"] = min(ball_progress * 8.0, 2.0)

        scored = self._is_goal()
        if scored:
            reward_terms["score_goal"] = 100.0

        ball_out = (
            abs(self.ball.x) > self.FIELD_X_LIMIT
            or abs(self.ball.y) > self.FIELD_Y_LIMIT
        )
        terminated = scored or ball_out
        truncated = self.steps >= self.max_steps
        reward = float(sum(reward_terms.values()))
        info = self._get_info()
        info["reward_terms"] = reward_terms
        info["action_name"] = {
            Action.FORWARD: "前进",
            Action.TURN_LEFT: "左转",
            Action.TURN_RIGHT: "右转",
            Action.KICK: "踢球",
        }[Action(action)]
        return self._get_observation(), reward, terminated, truncated, info

    def _move_forward(self) -> None:
        """沿 MicroDuck 当前朝向前进，并处理身体推球。"""

        step_size = 0.09
        self.duck.x = float(
            np.clip(
                self.duck.x + cos(self.duck.angle) * step_size,
                -self.FIELD_X_LIMIT,
                self.FIELD_X_LIMIT,
            )
        )
        self.duck.y = float(
            np.clip(
                self.duck.y + sin(self.duck.angle) * step_size,
                -self.FIELD_Y_LIMIT,
                self.FIELD_Y_LIMIT,
            )
        )

        if self._duck_ball_distance() <= self.duck.radius + self.ball.radius:
            self.ball.vx += cos(self.duck.angle) * 0.035
            self.ball.vy += sin(self.duck.angle) * 0.035

    def _kick_ball(self) -> None:
        """球在脚边且大致位于正面时施加冲量。"""

        dx = self.ball.x - self.duck.x
        dy = self.ball.y - self.duck.y
        distance = hypot(dx, dy)
        ball_direction = atan2(dy, dx)
        angle_error = abs(self._wrap_angle(ball_direction - self.duck.angle))
        kick_reach = self.duck.radius + self.ball.radius + 0.08

        if distance <= kick_reach and angle_error <= pi / 3:
            kick_power = 0.32
            self.ball.vx += cos(self.duck.angle) * kick_power
            self.ball.vy += sin(self.duck.angle) * kick_power

    def _advance_ball_physics(self) -> None:
        """推进足球位置，并用阻尼模拟地面摩擦。"""

        speed = hypot(self.ball.vx, self.ball.vy)
        if speed > self.MAX_BALL_SPEED:
            scale = self.MAX_BALL_SPEED / speed
            self.ball.vx *= scale
            self.ball.vy *= scale

        self.ball.x += self.ball.vx
        self.ball.y += self.ball.vy
        self.ball.vx *= 0.92
        self.ball.vy *= 0.92

    def _get_observation(self) -> np.ndarray:
        observation = np.array(
            [
                self.duck.x,
                self.duck.y,
                sin(self.duck.angle),
                cos(self.duck.angle),
                self.ball.x - self.duck.x,
                self.ball.y - self.duck.y,
                self.goal.x - self.ball.x,
                self.goal.y - self.ball.y,
                self.ball.vx,
                self.ball.vy,
            ],
            dtype=np.float32,
        )
        return np.clip(
            observation,
            self.observation_space.low,
            self.observation_space.high,
        )

    def _get_info(self) -> dict[str, Any]:
        return {
            "steps": self.steps,
            "duck_ball_distance": self._duck_ball_distance(),
            "ball_goal_distance": hypot(
                self.goal.x - self.ball.x,
                self.goal.y - self.ball.y,
            ),
            "touched_ball": self.has_touched_ball,
            "scored": self._is_goal(),
        }

    def _duck_ball_distance(self) -> float:
        return hypot(self.ball.x - self.duck.x, self.ball.y - self.duck.y)

    def _is_goal(self) -> bool:
        return self.ball.x >= self.goal.x and abs(self.ball.y - self.goal.y) <= self.goal.width / 2

    @staticmethod
    def _wrap_angle(angle: float) -> float:
        return (angle + pi) % (2 * pi) - pi

    def render(self) -> str | np.ndarray | None:
        if self.render_mode == "ansi":
            return (
                f"MicroDuck=({self.duck.x:.2f}, {self.duck.y:.2f}) "
                f"Ball=({self.ball.x:.2f}, {self.ball.y:.2f}) "
                f"Goal=({self.goal.x:.2f}, {self.goal.y:.2f})"
            )
        if self.render_mode == "rgb_array":
            return self._render_rgb_array()
        return None

    def _render_rgb_array(self) -> np.ndarray:
        height, width = 360, 640
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        frame[:] = (74, 158, 82)
        frame[[0, -1], :] = 255
        frame[:, [0, -1]] = 255

        goal_x, goal_y = self._world_to_pixel(self.goal.x, self.goal.y, width, height)
        half_goal = int(self.goal.width / (2 * self.FIELD_Y_LIMIT) * height / 2)
        frame[max(0, goal_y - half_goal) : min(height, goal_y + half_goal), max(0, goal_x - 4) : goal_x + 1] = (255, 255, 255)
        self._draw_disc(frame, self.ball.x, self.ball.y, 9, (245, 245, 245))
        self._draw_disc(frame, self.duck.x, self.duck.y, 14, (255, 210, 51))
        return frame

    def _draw_disc(
        self,
        frame: np.ndarray,
        x: float,
        y: float,
        radius: int,
        color: tuple[int, int, int],
    ) -> None:
        cx, cy = self._world_to_pixel(x, y, frame.shape[1], frame.shape[0])
        yy, xx = np.ogrid[: frame.shape[0], : frame.shape[1]]
        frame[(xx - cx) ** 2 + (yy - cy) ** 2 <= radius**2] = color

    @classmethod
    def _world_to_pixel(
        cls,
        x: float,
        y: float,
        width: int,
        height: int,
    ) -> tuple[int, int]:
        px = int((x + cls.FIELD_X_LIMIT) / (2 * cls.FIELD_X_LIMIT) * (width - 1))
        py = int((y + cls.FIELD_Y_LIMIT) / (2 * cls.FIELD_Y_LIMIT) * (height - 1))
        return px, py


def run_random_demo() -> None:
    """运行随机策略，演示标准 Gymnasium 使用方式。"""

    env = MicroDuckFootballEnv(render_mode="ansi")
    observation, info = env.reset(seed=42)
    total_reward = 0.0
    terminated = truncated = False

    while not (terminated or truncated):
        action = env.action_space.sample()
        observation, reward, terminated, truncated, info = env.step(action)
        total_reward += reward

    print(env.render())
    print(f"总奖励：{total_reward:.2f}")
    print(f"是否进球：{info['scored']}")
    print(f"最终状态维度：{observation.shape}")
    env.close()


if __name__ == "__main__":
    from gymnasium.utils.env_checker import check_env

    check_env(MicroDuckFootballEnv())
    run_random_demo()
