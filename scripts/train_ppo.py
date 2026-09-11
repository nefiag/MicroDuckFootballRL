"""使用 Stable-Baselines3 PPO 训练 MicroDuck 足球策略。"""

import argparse
import json
from pathlib import Path

from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import CheckpointCallback
from stable_baselines3.common.env_checker import check_env
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.vec_env import DummyVecEnv

from microduck_football import MicroDuckFootballEnv


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=ROOT / "configs/ppo.json")
    parser.add_argument("--steps", type=int, help="覆盖配置中的训练步数")
    parser.add_argument("--level", type=int, default=1, choices=range(1, 5))
    parser.add_argument("--no-randomization", action="store_true")
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    total_timesteps = args.steps or config.pop("total_timesteps")

    sample_env = MicroDuckFootballEnv(args.level, not args.no_randomization)
    check_env(sample_env, warn=True)
    sample_env.close()
    env = DummyVecEnv(
        [lambda: Monitor(MicroDuckFootballEnv(args.level, not args.no_randomization))]
    )
    (ROOT / "models/checkpoints").mkdir(parents=True, exist_ok=True)
    (ROOT / "logs").mkdir(exist_ok=True)
    model = PPO("MlpPolicy", env, verbose=1, tensorboard_log=str(ROOT / "logs"), **config)
    callback = CheckpointCallback(
        save_freq=50_000,
        save_path=str(ROOT / "models/checkpoints"),
        name_prefix="football_policy",
    )
    model.learn(total_timesteps=total_timesteps, callback=callback)
    model.save(ROOT / "models/football_policy")
    print(f"模型已保存：{ROOT / 'models/football_policy.zip'}")


if __name__ == "__main__":
    main()
