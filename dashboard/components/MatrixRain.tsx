"use client";

import { useEffect, useRef } from "react";

export default function StarField() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d")!;

    const resize = () => {
      canvas.width = canvas.offsetWidth;
      canvas.height = canvas.offsetHeight;
    };
    resize();
    window.addEventListener("resize", resize);

    // Stars: [x, y, radius, speed, brightness, twinkleOffset]
    const NUM_STARS = 260;
    const stars = Array.from({ length: NUM_STARS }, () => ({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      r: Math.random() * 1.4 + 0.2,
      speed: Math.random() * 0.08 + 0.01,
      bright: Math.random(),
      phase: Math.random() * Math.PI * 2,
      color: Math.random() > 0.8
        ? (Math.random() > 0.5 ? "#b0d4ff" : "#ffd4b0")  // blue/warm giants
        : "#ffffff",
    }));

    // Shooting stars
    const shoots: { x: number; y: number; vx: number; vy: number; life: number; maxLife: number }[] = [];
    const spawnShoot = () => {
      if (shoots.length > 3) return;
      const angle = (Math.random() * 30 + 15) * Math.PI / 180;
      shoots.push({
        x: Math.random() * canvas.width * 0.6,
        y: Math.random() * canvas.height * 0.4,
        vx: Math.cos(angle) * 8,
        vy: Math.sin(angle) * 8,
        life: 0,
        maxLife: 30 + Math.random() * 20,
      });
    };

    let frame = 0;
    const draw = () => {
      frame++;
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // Draw stars
      const t = frame * 0.02;
      for (const star of stars) {
        const tw = 0.5 + 0.5 * Math.sin(t + star.phase);
        ctx.beginPath();
        ctx.arc(star.x, star.y, star.r, 0, Math.PI * 2);
        ctx.fillStyle = star.color;
        ctx.globalAlpha = 0.3 + 0.7 * tw * star.bright;
        ctx.fill();

        // Subtle cross flare for bright stars
        if (star.r > 1.1) {
          ctx.globalAlpha = 0.12 * tw;
          ctx.strokeStyle = star.color;
          ctx.lineWidth = 0.5;
          ctx.beginPath();
          ctx.moveTo(star.x - star.r * 3, star.y);
          ctx.lineTo(star.x + star.r * 3, star.y);
          ctx.moveTo(star.x, star.y - star.r * 3);
          ctx.lineTo(star.x, star.y + star.r * 3);
          ctx.stroke();
        }
      }

      // Shooting stars
      if (frame % 180 === 0) spawnShoot();
      ctx.lineWidth = 2;
      for (let i = shoots.length - 1; i >= 0; i--) {
        const s = shoots[i];
        const progress = s.life / s.maxLife;
        const tail = 60 * progress;
        ctx.globalAlpha = (1 - progress) * 0.9;
        const grad = ctx.createLinearGradient(s.x - s.vx * tail / s.vx, s.y - s.vy * tail / s.vy, s.x, s.y);
        grad.addColorStop(0, "transparent");
        grad.addColorStop(1, "#ffffff");
        ctx.strokeStyle = grad;
        ctx.beginPath();
        ctx.moveTo(s.x - s.vx * (tail / 8), s.y - s.vy * (tail / 8));
        ctx.lineTo(s.x, s.y);
        ctx.stroke();
        s.x += s.vx;
        s.y += s.vy;
        s.life++;
        if (s.life >= s.maxLife) shoots.splice(i, 1);
      }

      ctx.globalAlpha = 1;
    };

    const id = setInterval(draw, 50);
    return () => {
      clearInterval(id);
      window.removeEventListener("resize", resize);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="absolute inset-0 w-full h-full pointer-events-none"
    />
  );
}
