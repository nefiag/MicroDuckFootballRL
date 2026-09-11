"""使用 macOS say 生成中文旁白，并通过 FFmpeg 合成到第一集视频。"""

import argparse
import re
import shutil
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCRIPT = ROOT / "course/episodes/01-bilibili-voiceover.md"
DEFAULT_OUTPUT = ROOT / "media/video/microduck_episode_01_voiced.mp4"
SECTION_PATTERN = re.compile(
    r"^## (\d{2}):(\d{2})–(\d{2}):(\d{2})｜[^\n]*\n(.*?)(?=^## |\Z)",
    re.MULTILINE | re.DOTALL,
)


def run(command: list[str]) -> None:
    subprocess.run(command, check=True)


def require(command: str) -> str:
    path = shutil.which(command)
    if not path:
        raise SystemExit(f"缺少命令：{command}。请先安装 FFmpeg，且需在 macOS 运行。")
    return path


def clean_narration(markdown: str) -> str:
    text = re.sub(r"\[[^\]]+\]", "", markdown)
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"\*\*([^*]*)\*\*", r"\1", text)
    return "\n".join(
        line
        for raw_line in text.splitlines()
        if (line := raw_line.strip())
        and not line.startswith(("#", "- ", ">", "---"))
    )


def sections(path: Path) -> list[tuple[int, str]]:
    markdown = path.read_text(encoding="utf-8").split("## 录音提示")[0]
    result: list[tuple[int, str]] = []
    for start_min, start_sec, end_min, end_sec, body in SECTION_PATTERN.findall(markdown):
        start = int(start_min) * 60 + int(start_sec)
        end = int(end_min) * 60 + int(end_sec)
        narration = clean_narration(body)
        if not narration:
            raise ValueError(f"{start_min}:{start_sec} 没有可朗读内容")
        result.append((end - start, narration))
    if len(result) != 10 or sum(duration for duration, _ in result) != 600:
        raise ValueError("旁白必须包含 10 个时间段，总计 600 秒")
    return result


def audio_duration(ffprobe: str, path: Path) -> float:
    completed = subprocess.run(
        [ffprobe, "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        check=True,
        capture_output=True,
        text=True,
    )
    return float(completed.stdout.strip())


def atempo_filter(factor: float) -> str:
    factors: list[float] = []
    while factor > 2.0:
        factors.append(2.0)
        factor /= 2.0
    while factor < 0.5:
        factors.append(0.5)
        factor /= 0.5
    factors.append(factor)
    return ",".join(f"atempo={value:.6f}" for value in factors)


def synthesize_track(script: Path, voice: str, rate: int, workspace: Path) -> Path:
    say, ffmpeg, ffprobe = require("say"), require("ffmpeg"), require("ffprobe")
    segment_paths: list[Path] = []
    for index, (target_duration, narration) in enumerate(sections(script), start=1):
        raw_audio = workspace / f"raw-{index:02d}.aiff"
        segment_audio = workspace / f"segment-{index:02d}.wav"
        run([say, "-v", voice, "-r", str(rate), "-o", str(raw_audio), narration])
        source_duration = audio_duration(ffprobe, raw_audio)
        speed_factor = source_duration / target_duration
        audio_filter = f"{atempo_filter(speed_factor)},apad=pad_dur={target_duration},atrim=0:{target_duration}"
        run([
            ffmpeg, "-y", "-loglevel", "error", "-i", str(raw_audio),
            "-af", audio_filter, "-ar", "48000", "-ac", "2", str(segment_audio),
        ])
        print(f"旁白 {index:02d}/10：原始 {source_duration:.1f}s → 目标 {target_duration}s")
        segment_paths.append(segment_audio)

    concat_file = workspace / "segments.txt"
    concat_file.write_text(
        "".join(f"file '{path.as_posix()}'\n" for path in segment_paths),
        encoding="utf-8",
    )
    narration_track = workspace / "narration.wav"
    run([
        ffmpeg, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
        "-i", str(concat_file), "-c:a", "pcm_s16le", str(narration_track),
    ])
    return narration_track


def find_default_video() -> Path:
    candidates = sorted(
        (ROOT / "media").glob("videos/**/microduck_episode_01.mp4"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    if not candidates:
        raise SystemExit("找不到无声视频，请先运行 bash scripts/render_episode_01.sh")
    return candidates[0]


def main() -> None:
    parser = argparse.ArgumentParser(description="生成并合成第一集中文旁白")
    parser.add_argument("--video", type=Path, help="无声 Manim MP4；默认自动查找")
    parser.add_argument("--script", type=Path, default=DEFAULT_SCRIPT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--voice", default="Tingting", help="macOS 中文语音名称")
    parser.add_argument("--rate", type=int, default=210, help="macOS say 初始语速")
    args = parser.parse_args()
    video = args.video or find_default_video()
    ffmpeg = require("ffmpeg")
    args.output.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="microduck-voice-") as directory:
        narration = synthesize_track(args.script, args.voice, args.rate, Path(directory))
        run([
            ffmpeg, "-y", "-loglevel", "error", "-i", str(video), "-i", str(narration),
            "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac",
            "-b:a", "192k", "-t", "600", str(args.output),
        ])
    print(f"有声视频已输出：{args.output}")


if __name__ == "__main__":
    main()
