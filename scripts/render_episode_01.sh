#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
manim -c manim/manim.cfg manim/episode_01.py EpisodeOne

echo "Video: media/videos/episode_01/720p24/microduck_episode_01.mp4"
