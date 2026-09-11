"""从 course/episodes.json 自动生成教程、视频脚本和动画提示词。"""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "course/episodes.json"
OUTPUT = ROOT / "generated"


def tutorial(episodes: list[dict]) -> str:
    lines = ["# MicroDuck 足球强化学习完整教程", "", "> 本文件由 `scripts/generate_materials.py` 自动生成，请编辑课程数据源而非本文件。", ""]
    for item in episodes:
        lines += [f"## 第 {item['number']} 集：{item['title']}", "", f"- 时长：{item['duration']}", f"- 目标：{item['goal']}", f"- 核心概念：{'、'.join(item['concepts'])}", "", "### 学习步骤", "", "1. 观看同步动画并预测动作结果。", "2. 对照高亮代码，解释输入、处理和输出。", "3. 修改一个参数，记录奖励和成功率。", "4. 完成本集检查并保存实验。", ""]
    return "\n".join(lines)


def video_scripts(episodes: list[dict]) -> str:
    lines = ["# MicroDuck 足球强化学习视频脚本", "", "> 自动生成文件。", ""]
    for item in episodes:
        lines += [f"## 第 {item['number']} 集：{item['title']}", "", f"预计时长：{item['duration']}", "", "### 旁白", ""]
        lines += [f"- {text}" for text in item["narration"]]
        lines += ["", "### 分镜", ""]
        lines += [f"{index}. {shot}" for index, shot in enumerate(item["shots"], 1)]
        lines += ["", "### 结尾", "", f"本集目标是：{item['goal']}。完成实验后进入下一集。", ""]
    return "\n".join(lines)


def animation_prompts(episodes: list[dict]) -> str:
    lines = ["# MicroDuck 动画生成提示词", "", "> 适用于 Sora、Runway 等视频生成工具；自动生成文件。", ""]
    for item in episodes:
        lines += [f"## 第 {item['number']} 集：{item['title']}", "", "```text", item["prompt"], "```", ""]
    return "\n".join(lines)


def main() -> None:
    episodes = json.loads(SOURCE.read_text(encoding="utf-8"))
    OUTPUT.mkdir(exist_ok=True)
    files = {
        "tutorial.md": tutorial(episodes),
        "video_scripts.md": video_scripts(episodes),
        "animation_prompts.md": animation_prompts(episodes),
    }
    for name, content in files.items():
        path = OUTPUT / name
        path.write_text(content + "\n", encoding="utf-8")
        print(f"已生成：{path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
