#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
manim -c manim/manim.cfg --fps 24 -o microduck_mujoco_rl_course.mp4 manim/mujoco_rl_course.py MujocoRLCourse
python3 scripts/add_voiceover.py --video media/videos/mujoco_rl_course/720p24/microduck_mujoco_rl_course.mp4 --script course/episodes/02-mujoco-rl-voiceover.md --output media/video/microduck_mujoco_rl_course_voiced.mp4

echo "Video: media/video/microduck_mujoco_rl_course_voiced.mp4"
