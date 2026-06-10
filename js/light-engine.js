/**
 * 动态闪烁灯光核心引擎
 * - Canvas 渲染 + 径向渐变模拟光晕
 * - 基于相位累加的正弦频率算法
 * - requestAnimationFrame 驱动
 * - 鼠标/键盘交互响应
 */
class LightEngine {
  constructor(canvas) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.lights = [];
    this.paused = false;
    this.globalSpeed = 1.0;
    this.lastTime = 0;
    this.mouse = { x: -999, y: -999 };

    this._init();
  }

  _init() {
    this._resize();
    window.addEventListener('resize', () => this._resize());
    this._bindEvents();
    requestAnimationFrame((t) => this._loop(t));
  }

  _resize() {
    const dpr = window.devicePixelRatio || 1;
    this.canvas.width = window.innerWidth * dpr;
    this.canvas.height = window.innerHeight * dpr;
    this.canvas.style.width = `${window.innerWidth}px`;
    this.canvas.style.height = `${window.innerHeight}px`;
    this.ctx.scale(dpr, dpr);
  }

  _bindEvents() {
    // 鼠标交互
    this.canvas.addEventListener('click', (e) => this.addLight(e.clientX, e.clientY));
    this.canvas.addEventListener('mousemove', (e) => {
      this.mouse.x = e.clientX;
      this.mouse.y = e.clientY;
    });

    // 键盘快捷键
    window.addEventListener('keydown', (e) => {
      const key = e.key.toLowerCase();
      switch (key) {
        case ' ':
          this.paused = !this.paused;
          break;
        case '+': case '=':
          this.globalSpeed = Math.min(5.0, this.globalSpeed + 0.2);
          break;
        case '-': case '_':
          this.globalSpeed = Math.max(0.1, this.globalSpeed - 0.2);
          break;
        case 'c':
          this.lights = [];
          break;
      }
    });
  }

  // 随机生成灯光节点
  addLight(x, y) {
    this.lights.push({
      x, y,
      baseRadius: 15 + Math.random() * 25,
      hue: Math.random() * 360,
      freq: 0.4 + Math.random() * 2.5,   // 基础闪烁频率 (Hz)
      phase: Math.random() * Math.PI * 2, // 初始相位偏移
      hovered: false
    });
  }

  // 核心更新算法
  _update(dt) {
    const speedFactor = this.paused ? 0 : this.globalSpeed;

    this.lights.forEach(light => {
      // 1. 频率控制：相位累加 (phase += freq * dt * 2π)
      light.phase += light.freq * speedFactor * dt * Math.PI * 2;

      // 2. 鼠标交互：悬停检测
      const dist = Math.hypot(light.x - this.mouse.x, light.y - this.mouse.y);
      const isHovered = dist < light.baseRadius + 10;
      if (isHovered !== light.hovered) {
        light.hovered = isHovered;
        if (isHovered) {
          light.hue = (light.hue + 30) % 360; // 悬停变色
        }
      }

      // 3. 亮度/透明度计算：正弦波映射到 [0.15, 1.0] 区间
      // 公式: opacity = min + range * (sin(phase) * 0.5 + 0.5)
      light.opacity = 0.15 + 0.85 * (0.5 + 0.5 * Math.sin(light.phase));
      
      // 悬停时频率临时加速（视觉反馈）
      const visualFreq = isHovered ? light.freq * 2.5 : light.freq;
      // 注意：这里不改变实际 phase 累加速度，仅用于呼吸感微调（可选）
    });
  }

  _draw() {
    this.ctx.clearRect(0, 0, window.innerWidth, window.innerHeight);
    
    // 启用 additive 混合模式，让重叠光效更明亮
    this.ctx.globalCompositeOperation = 'lighter';

    this.lights.forEach(light => {
      const { x, y, baseRadius, hue, opacity } = light;
      const r = baseRadius * (0.8 + opacity * 0.4); // 随亮度微缩膨胀

      const grad = this.ctx.createRadialGradient(x, y, 0, x, y, r);
      grad.addColorStop(0, `hsla(${hue}, 85%, 65%, ${opacity})`);
      grad.addColorStop(0.4, `hsla(${hue}, 80%, 55%, ${opacity * 0.6})`);
      grad.addColorStop(1, `hsla(${hue}, 80%, 45%, 0)`);

      this.ctx.fillStyle = grad;
      this.ctx.beginPath();
      this.ctx.arc(x, y, r, 0, Math.PI * 2);
      this.ctx.fill();
    });

    // 恢复默认混合模式
    this.ctx.globalCompositeOperation = 'source-over';
  }

  // 渲染循环
  _loop(timestamp) {
    if (!this.lastTime) this.lastTime = timestamp;
    const dt = Math.min((timestamp - this.lastTime) / 1000, 0.1); // 限制最大 dt 防跳帧
    this.lastTime = timestamp;

    this._update(dt);
    this._draw();
    requestAnimationFrame((t) => this._loop(t));
  }
}

// 初始化
document.addEventListener('DOMContentLoaded', () => {
  const canvas = document.getElementById('canvas');
  new LightEngine(canvas);

  // 预置几个灯光
  const engine = canvas._engine || (window._engine = new LightEngine(canvas));
  for (let i = 0; i < 6; i++) {
    engine.addLight(
      window.innerWidth * (0.2 + Math.random() * 0.6),
      window.innerHeight * (0.2 + Math.random() * 0.6)
    );
  }
});