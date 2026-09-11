#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
bash scripts/render_episode_01.sh
python3 scripts/add_voiceover.py "$@"
echo "Voiced video: media/video/microduck_episode_01_voiced.mp4"
