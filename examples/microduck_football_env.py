"""MicroDuck 足球 AI 教程：零依赖 2D 环境与随机策略基线。"""

from dataclasses import dataclass
from math import cos, hypot, pi, sin
import random


@dataclass
class Body:
    x: float
    y: float
    angle: float = 0.0


class MicroDuckFootballEnv:
    """Gym 风格教学环境：reset() / step(action)。

    动作：0 等待、1 前进、2 左转、3 右转、4 踢球。
    状态：球相对机器人坐标、球门相对球坐标、机器人朝向。
    """

    ACTIONS = ("等待", "前进", "左转", "右转", "踢球")

    def __init__(self, level: int = 1, domain_randomization: bool = False, seed: int = 7):
        self.level = max(1, min(4, level))
        self.domain_randomization = domain_randomization
        self.rng = random.Random(seed)
        self.goal = Body(2.8, 0.0)
        self.reset()

    def reset(self):
        radius = (0.15, 0.5, 1.5, 2.5)[self.level - 1]
        self.robot = Body(-1.8, self.rng.uniform(-0.35, 0.35))
        self.ball = Body(
            self.robot.x + self.rng.uniform(0.12, radius),
            self.robot.y + self.rng.uniform(-radius / 2, radius / 2),
        )
        self.ball_vx = self.ball_vy = 0.0
        self.steps = 0
        self.friction = self.rng.uniform(0.4, 1.2) if self.domain_randomization else 0.82
        self.motor_power = self.rng.uniform(0.8, 1.1) if self.domain_randomization else 1.0
        return self.observation()

    def observation(self):
        return (
            self.ball.x - self.robot.x,
            self.ball.y - self.robot.y,
            self.goal.x - self.ball.x,
            self.goal.y - self.ball.y,
            self.robot.angle / pi,
        )

    def step(self, action: int):
        old_ball_distance = hypot(self.ball.x - self.robot.x, self.ball.y - self.robot.y)
        old_goal_distance = hypot(self.goal.x - self.ball.x, self.goal.y - self.ball.y)

        if action == 1:
            self.robot.x += cos(self.robot.angle) * 0.09 * self.motor_power
            self.robot.y += sin(self.robot.angle) * 0.09 * self.motor_power
        elif action == 2:
            self.robot.angle += 0.13 * self.motor_power
        elif action == 3:
            self.robot.angle -= 0.13 * self.motor_power

        touched = hypot(self.ball.x - self.robot.x, self.ball.y - self.robot.y) < 0.20
        kicked = action == 4 and touched
        if kicked:
            self.ball_vx += cos(self.robot.angle) * 0.30 * self.motor_power
            self.ball_vy += sin(self.robot.angle) * 0.30 * self.motor_power

        damping = 0.90 + self.friction * 0.06
        self.ball.x += self.ball_vx
        self.ball.y += self.ball_vy
        self.ball_vx *= damping
        self.ball_vy *= damping
        self.steps += 1

        ball_distance = hypot(self.ball.x - self.robot.x, self.ball.y - self.robot.y)
        goal_distance = hypot(self.goal.x - self.ball.x, self.goal.y - self.ball.y)
        scored = self.ball.x >= self.goal.x and abs(self.ball.y) < 0.55
        out = abs(self.ball.y) > 1.8 or self.ball.x < -3.2 or self.ball.x > 3.2
        truncated = self.steps >= 400

        reward = -0.002
        reward += (old_ball_distance - ball_distance) * 1.2
        reward += (old_goal_distance - goal_distance) * 2.0
        if touched:
            reward += 0.1
        if kicked:
            reward += 1.0
        if scored:
            reward += 100.0
        if out:
            reward -= 5.0

        info = {"scored": scored, "touched": touched, "friction": self.friction}
        return self.observation(), reward, scored or out or truncated, info


if __name__ == "__main__":
    env = MicroDuckFootballEnv(level=2, domain_randomization=True)
    total = 0.0
    observation = env.reset()
    for _ in range(400):
        action = env.rng.randrange(len(env.ACTIONS))
        observation, reward, done, info = env.step(action)
        total += reward
        if done:
            break
    print({"reward": round(total, 3), "state": observation, **info})
