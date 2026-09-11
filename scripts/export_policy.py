"""将 SB3 PPO 策略网络导出为 TorchScript，供真实机器人推理。"""

import argparse
from pathlib import Path

import torch
from stable_baselines3 import PPO


ROOT = Path(__file__).resolve().parents[1]


class DeterministicPolicy(torch.nn.Module):
    def __init__(self, policy: torch.nn.Module) -> None:
        super().__init__()
        self.policy = policy

    def forward(self, observation: torch.Tensor) -> torch.Tensor:
        return self.policy(observation, deterministic=True)[0]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=Path, default=ROOT / "models/football_policy.zip")
    parser.add_argument("--output", type=Path, default=ROOT / "models/football_policy.pt")
    args = parser.parse_args()
    model = PPO.load(args.model, device="cpu")
    wrapper = DeterministicPolicy(model.policy).eval()
    traced = torch.jit.trace(wrapper, torch.zeros(1, 8))
    traced.save(str(args.output))
    print(f"部署模型已导出：{args.output}")


if __name__ == "__main__":
    main()
