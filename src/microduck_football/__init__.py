"""MicroDuck 足球强化学习环境。"""

from gymnasium.envs.registration import register, registry

from .env import MicroDuckFootballEnv
from .randomization import DomainRandomization, DomainSample

if "MicroDuckFootball-v0" not in registry:
    register(
        id="MicroDuckFootball-v0",
        entry_point="microduck_football.env:MicroDuckFootballEnv",
        max_episode_steps=400,
    )

__all__ = ["DomainRandomization", "DomainSample", "MicroDuckFootballEnv"]
