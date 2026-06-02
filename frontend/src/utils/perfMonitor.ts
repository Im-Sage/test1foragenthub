/** 轻量级 FPS 与内存监控 Hook (React 示例) */
import { useEffect, useRef, useState } from 'react';

export function usePerfMonitor(interval = 1000) {
  const [fps, setFps] = useState(0);
  const frames = useRef(0);
  const lastTime = useRef(performance.now());

  useEffect(() => {
    let rafId: number;
    const loop = () => {
      frames.current++;
      const now = performance.now();
      if (now - lastTime.current >= interval) {
        setFps(Math.round((frames.current * 1000) / (now - lastTime.current)));
        frames.current = 0;
        lastTime.current = now;
      }
      rafId = requestAnimationFrame(loop);
    };
    rafId = requestAnimationFrame(loop);
    return () => cancelAnimationFrame(rafId);
  }, [interval]);

  return { fps, mem: performance.memory ? performance.memory.usedJSHeapSize : null };
}