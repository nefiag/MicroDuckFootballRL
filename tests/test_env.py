import gymnasium as gym
import numpy as np

from microduck_football import MicroDuckFootballEnv


def test_environment_uses_gymnasium_spaces() -> None:
    env = MicroDuckFootballEnv(domain_randomization=False)
    assert isinstance(env.action_space, gym.spaces.Discrete)
    assert isinstance(env.observation_space, gym.spaces.Box)
    observation, info = env.reset(seed=42)
    assert observation.dtype == np.float32
    assert env.observation_space.contains(observation)
    assert info["domain"]["friction"] == 0.82


def test_registered_environment_id() -> None:
    env = gym.make("MicroDuckFootball-v0", domain_randomization=False)
    observation, _ = env.reset(seed=8)
    assert env.observation_space.contains(observation)
    env.close()


def test_step_follows_five_value_api() -> None:
    env = MicroDuckFootballEnv(max_steps=1)
    env.reset(seed=3)
    observation, reward, terminated, truncated, info = env.step(0)
    assert env.observation_space.contains(observation)
    assert isinstance(reward, float)
    assert isinstance(terminated, bool)
    assert truncated is True
    assert info["steps"] == 1


def test_domain_randomization_is_reproducible() -> None:
    first = MicroDuckFootballEnv(domain_randomization=True)
    second = MicroDuckFootballEnv(domain_randomization=True)
    _, first_info = first.reset(seed=99)
    _, second_info = second.reset(seed=99)
    assert first_info["domain"] == second_info["domain"]


def test_curriculum_changes_spawn_range() -> None:
    env = MicroDuckFootballEnv(level=1)
    env.set_curriculum(4)
    _, info = env.reset(seed=5)
    assert info["level"] == 4
