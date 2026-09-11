"""在关闭域随机化的固定环境中评估策略。"""

import argparse
from pathlib import Path

from stable_baselines3 import PPO

from microduck_football import MicroDuckFootballEnv


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=Path, default=ROOT / "models/football_policy.zip")
    parser.add_argument("--episodes", type=int, default=50)
    args = parser.parse_args()
    model = PPO.load(args.model)
    env = MicroDuckFootballEnv(level=4, domain_randomization=False)
    successes, rewards = 0, []
    for episode in range(args.episodes):
        observation, _ = env.reset(seed=10_000 + episode)
        total_reward = 0.0
        terminated = truncated = False
        while not (terminated or truncated):
            action, _ = model.predict(observation, deterministic=True)
            observation, reward, terminated, truncated, info = env.step(int(action))
            total_reward += reward
        successes += int(info["scored"])
        rewards.append(total_reward)
    print(f"回合={args.episodes} 成功率={successes / args.episodes:.1%} 平均奖励={sum(rewards) / len(rewards):.2f}")


if __name__ == "__main__":
    main()
