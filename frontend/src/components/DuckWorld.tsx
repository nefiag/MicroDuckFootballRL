import { useEffect, useRef } from "react";
export type Frame = {
  duck_x: number;
  ball_x: number;
  reward?: number;
  action_name?: string;
};
export function DuckWorld({ frames = [] }: { frames?: Frame[] }) {
  const canvas = useRef<HTMLCanvasElement>(null);
  useEffect(() => {
    const c = canvas.current;
    if (!c) return;
    const x = c.getContext("2d")!;
    let i = 0,
      t = 0;
    const draw = () => {
      const f = frames.length ? frames[i] : { duck_x: 90, ball_x: 360 };
      x.clearRect(0, 0, 800, 400);
      const g = x.createLinearGradient(0, 0, 0, 400);
      g.addColorStop(0, "#dff7ff");
      g.addColorStop(1, "#fff9df");
      x.fillStyle = g;
      x.fillRect(0, 0, 800, 400);
      x.strokeStyle = "#a9d2b5";
      x.lineWidth = 3;
      for (let n = 0; n < 800; n += 50) {
        x.beginPath();
        x.moveTo(n, 0);
        x.lineTo(n, 350);
        x.stroke();
      }
      x.fillStyle = "#75bb82";
      x.fillRect(0, 350, 800, 50);
      x.fillStyle = "#fff";
      x.fillRect(690, 250, 8, 100);
      x.fillStyle = "#ff7467";
      x.fillRect(698, 250, 70, 38);
      x.save();
      x.translate(f.duck_x, 320);
      x.fillStyle = "#ffd23f";
      x.beginPath();
      x.ellipse(0, 0, 32, 23, 0, 0, 7);
      x.fill();
      x.beginPath();
      x.arc(25, -22, 18, 0, 7);
      x.fill();
      x.fillStyle = "#f5822b";
      x.beginPath();
      x.moveTo(41, -23);
      x.lineTo(62, -15);
      x.lineTo(41, -9);
      x.fill();
      x.fillStyle = "#142b3f";
      x.beginPath();
      x.arc(31, -27, 3, 0, 7);
      x.fill();
      x.restore();
      x.fillStyle = "#ff694f";
      x.beginPath();
      x.arc(f.ball_x, 332, 17, 0, 7);
      x.fill();
      x.fillStyle = "#17324d";
      x.font = "600 17px system-ui";
      x.fillText(
        `${f.action_name ?? "等待开始"}  奖励 ${Number(f.reward ?? 0).toFixed(2)}`,
        20,
        30,
      );
      if (frames.length) i = (i + 1) % frames.length;
      t = requestAnimationFrame(draw);
    };
    draw();
    return () => cancelAnimationFrame(t);
  }, [frames]);
  return <canvas ref={canvas} width="800" height="400" />;
}
