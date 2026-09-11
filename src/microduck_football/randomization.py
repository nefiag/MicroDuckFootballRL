"""Sim2Real 域随机化参数与采样器。"""

from dataclasses import asdict, dataclass
import random


@dataclass(frozen=True)
class DomainSample:
    friction: float = 0.82
    robot_mass_scale: float = 1.0
    motor_power: float = 1.0
    motor_delay_steps: int = 0
    observation_noise: float = 0.0

    def to_dict(self) -> dict[str, float | int]:
        return asdict(self)


@dataclass(frozen=True)
class DomainRandomization:
    enabled: bool = True
    friction: tuple[float, float] = (0.4, 1.2)
    robot_mass_scale: tuple[float, float] = (0.85, 1.15)
    motor_power: tuple[float, float] = (0.8, 1.1)
    motor_delay_steps: tuple[int, int] = (0, 3)
    observation_noise: tuple[float, float] = (0.0, 0.02)

    def sample(self, rng: random.Random) -> DomainSample:
        if not self.enabled:
            return DomainSample()
        return DomainSample(
            friction=rng.uniform(*self.friction),
            robot_mass_scale=rng.uniform(*self.robot_mass_scale),
            motor_power=rng.uniform(*self.motor_power),
            motor_delay_steps=rng.randint(*self.motor_delay_steps),
            observation_noise=rng.uniform(*self.observation_noise),
        )
