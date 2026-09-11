"""符合 Gymnasium API 的 MicroDuck 二维足球环境。"""

from collections import deque
from dataclasses import dataclass
from math import cos, hypot, pi, sin
from typing import Any
import random

import gymnasium as gym
import numpy as np
from gymnasium import spaces

from .randomization import DomainRandomization, DomainSample


@dataclass
class Body:
    x: float
    y: float
    angle: float = 0.0


class MicroDuckFootballEnv(gym.Env[np.ndarray, int]):
    """离散动作足球环境。

    动作：0 等待、1 前进、2 左转、3 右转、4 踢球。
    观测：球相对位置、球门相对位置、朝向 sin/cos、球速度。
    """

    metadata = {"render_modes": ["ansi", "rgb_array"], "render_fps": 20}
    ACTIONS = ("等待", "前进", "左转", "右转", "踢球")

    def __init__(
        self,
        level: int = 1,
        domain_randomization: bool = True,
        max_steps: int = 400,
        render_mode: str | None = None,
    ) -> None:
        super().__init__()
        self.level = int(np.clip(level, 1, 4))
        self.max_steps = max_steps
        self.render_mode = render_mode
        self.action_space = spaces.Discrete(len(self.ACTIONS))
        self.observation_space = spaces.Box(
            low=np.array([-7, -4, -7, -4, -1, -1, -1, -1], dtype=np.float32),
            high=np.array([7, 4, 7, 4, 1, 1, 1, 1], dtype=np.float32),
            dtype=np.float32,
        )
        self.randomizer = DomainRandomization(enabled=domain_randomization)
        self._python_rng = random.Random()
        self.goal = Body(2.8, 0.0)
        self.domain = DomainSample()
        self._action_queue: deque[int] = deque()

    def set_curriculum(self, level: int) -> None:
        self.level = int(np.clip(level, 1, 4))

    def reset(
        self, *, seed: int | None = None, options: dict[str, Any] | None = None
    ) -> tuple[np.ndarray, dict[str, Any]]:
        super().reset(seed=seed)
        if seed is not None:
            self._python_rng.seed(seed)
        if options and "level" in options:
            self.set_curriculum(int(options["level"]))
        radius = (0.15, 0.5, 1.5, 2.5)[self.level - 1]
        self.robot = Body(-1.8, self._python_rng.uniform(-0.35, 0.35))
        self.ball = Body(
            self.robot.x + self._python_rng.uniform(0.12, radius),
            self.robot.y + self._python_rng.uniform(-radius / 2, radius / 2),
        )
        self.ball_vx = self.ball_vy = 0.0
        self.steps = 0
        self.domain = self.randomizer.sample(self._python_rng)
        self._action_queue = deque([0] * self.domain.motor_delay_steps)
        return self._observation(), self._info(False, False)

    def _observation(self) -> np.ndarray:
        values = np.array(
            [
                self.ball.x - self.robot.x,
                self.ball.y - self.robot.y,
                self.goal.x - self.ball.x,
                self.goal.y - self.ball.y,
                sin(self.robot.angle),
                cos(self.robot.angle),
                self.ball_vx,
                self.ball_vy,
            ],
            dtype=np.float32,
        )
        if self.domain.observation_noise:
            noise = self.np_random.normal(0, self.domain.observation_noise, values.shape)
            values += noise.astype(np.float32)
        return np.clip(values, self.observation_space.low, self.observation_space.high)

    def step(self, action: int) -> tuple[np.ndarray, float, bool, bool, dict[str, Any]]:
        if not self.action_space.contains(action):
            raise ValueError(f"无效动作 {action}；应为 0–{self.action_space.n - 1}")
        self._action_queue.append(int(action))
        applied_action = self._action_queue.popleft()
        old_ball_distance = hypot(self.ball.x - self.robot.x, self.ball.y - self.robot.y)
        old_goal_distance = hypot(self.goal.x - self.ball.x, self.goal.y - self.ball.y)

        speed = 0.09 * self.domain.motor_power / self.domain.robot_mass_scale
        if applied_action == 1:
            self.robot.x += cos(self.robot.angle) * speed
            self.robot.y += sin(self.robot.angle) * speed
        elif applied_action == 2:
            self.robot.angle = (self.robot.angle + 0.13 + pi) % (2 * pi) - pi
        elif applied_action == 3:
            self.robot.angle = (self.robot.angle - 0.13 + pi) % (2 * pi) - pi

        touched = hypot(self.ball.x - self.robot.x, self.ball.y - self.robot.y) < 0.20
        kicked = applied_action == 4 and touched
        if kicked:
            impulse = 0.30 * self.domain.motor_power / self.domain.robot_mass_scale
            self.ball_vx += cos(self.robot.angle) * impulse
            self.ball_vy += sin(self.robot.angle) * impulse

        damping = 0.90 + self.domain.friction * 0.06
        self.ball.x += self.ball_vx
        self.ball.y += self.ball_vy
        self.ball_vx *= damping
        self.ball_vy *= damping
        self.steps += 1

        ball_distance = hypot(self.ball.x - self.robot.x, self.ball.y - self.robot.y)
        goal_distance = hypot(self.goal.x - self.ball.x, self.goal.y - self.ball.y)
        scored = self.ball.x >= self.goal.x and abs(self.ball.y) < 0.55
        out = abs(self.ball.y) > 1.8 or self.ball.x < -3.2 or self.ball.x > 3.2
        terminated = scored or out
        truncated = self.steps >= self.max_steps
        reward = (
            -0.002
            + (old_ball_distance - ball_distance) * 1.2
            + (old_goal_distance - goal_distance) * 2.0
            + (0.1 if touched else 0.0)
            + (1.0 if kicked else 0.0)
            + (100.0 if scored else 0.0)
            - (5.0 if out else 0.0)
        )
        return self._observation(), reward, terminated, truncated, self._info(scored, touched)

    def _info(self, scored: bool, touched: bool) -> dict[str, Any]:
        return {
            "scored": scored,
            "touched": touched,
            "level": self.level,
            "steps": self.steps,
            "domain": self.domain.to_dict(),
        }

    def render(self) -> str | np.ndarray | None:
        if self.render_mode == "ansi":
            return f"duck=({self.robot.x:.2f},{self.robot.y:.2f}) ball=({self.ball.x:.2f},{self.ball.y:.2f})"
        if self.render_mode == "rgb_array":
            frame = np.zeros((360, 640, 3), dtype=np.uint8)
            frame[:] = (72, 153, 79)
            self._draw_disc(frame, self.robot.x, self.robot.y, 13, (255, 210, 51))
            self._draw_disc(frame, self.ball.x, self.ball.y, 8, (245, 245, 245))
            return frame
        return None

    @staticmethod
    def _draw_disc(frame: np.ndarray, x: float, y: float, radius: int, color: tuple[int, int, int]) -> None:
        cx, cy = int((x + 3.2) / 6.4 * 639), int((y + 1.8) / 3.6 * 359)
        yy, xx = np.ogrid[: frame.shape[0], : frame.shape[1]]
        frame[(xx - cx) ** 2 + (yy - cy) ** 2 <= radius**2] = color
