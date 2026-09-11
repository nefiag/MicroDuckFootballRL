"""随机策略示例：验证 Gymnasium 环境与域随机化。"""

from microduck_football import MicroDuckFootballEnv


def main() -> None:
    env = MicroDuckFootballEnv(level=2, domain_randomization=True, render_mode="ansi")
    observation, info = env.reset(seed=7)
    total_reward = 0.0
    terminated = truncated = False
    while not (terminated or truncated):
        action = env.action_space.sample()
        observation, reward, terminated, truncated, info = env.step(action)
        total_reward += reward
    print(
        {
            "reward": round(total_reward, 3),
            "observation_shape": observation.shape,
            "scored": info["scored"],
            "domain": info["domain"],
        }
    )
    env.close()


if __name__ == "__main__":
    main()
