(() => {
  const canvas = document.getElementById('reactor-canvas');
  const context = canvas && canvas.getContext('2d', { alpha: true });
  if (!canvas || !context) return;

  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const pointer = { x: -1000, y: -1000, active: false };
  const ripples = [];
  let particles = [];
  let width = 0;
  let height = 0;
  let ratio = 1;
  let lastFrame = 0;
  let raf = 0;

  function resize() {
    width = window.innerWidth;
    height = window.innerHeight;
    ratio = Math.min(window.devicePixelRatio || 1, width < 720 ? 1 : 1.35);
    canvas.width = Math.round(width * ratio);
    canvas.height = Math.round(height * ratio);
    context.setTransform(ratio, 0, 0, ratio, 0, 0);
    const count = Math.max(22, Math.min(64, Math.round((width * height) / 23000)));
    particles = Array.from({ length: count }, () => ({
      x: Math.random() * width,
      y: Math.random() * height,
      vx: (Math.random() - .5) * 8,
      vy: (Math.random() - .5) * 8,
      radius: .65 + Math.random() * 1.5,
      hue: Math.random() > .56 ? '0,204,255' : '255,49,84',
      phase: Math.random() * Math.PI * 2
    }));
    paint(performance.now(), 0);
  }

  function paint(now, delta) {
    context.clearRect(0, 0, width, height);
    const seconds = delta / 1000;
    for (const particle of particles) {
      particle.x += particle.vx * seconds;
      particle.y += particle.vy * seconds;
      if (particle.x < -12) particle.x = width + 12;
      if (particle.x > width + 12) particle.x = -12;
      if (particle.y < -12) particle.y = height + 12;
      if (particle.y > height + 12) particle.y = -12;
      particle.phase += seconds * 1.6;
    }

    const maxDistance = width < 720 ? 88 : 128;
    for (let i = 0; i < particles.length; i += 1) {
      const a = particles[i];
      for (let j = i + 1; j < particles.length; j += 1) {
        const b = particles[j];
        const dx = a.x - b.x;
        const dy = a.y - b.y;
        const distance = Math.hypot(dx, dy);
        if (distance < maxDistance) {
          context.globalAlpha = (1 - distance / maxDistance) * .13;
          context.strokeStyle = a.hue === b.hue ? `rgb(${a.hue})` : '#93cfff';
          context.lineWidth = .7;
          context.beginPath();
          context.moveTo(a.x, a.y);
          context.lineTo(b.x, b.y);
          context.stroke();
        }
      }
      const pulse = .55 + Math.sin(a.phase) * .24;
      context.globalAlpha = pulse;
      context.fillStyle = `rgb(${a.hue})`;
      context.shadowBlur = 10;
      context.shadowColor = `rgba(${a.hue},.7)`;
      context.beginPath();
      context.arc(a.x, a.y, a.radius, 0, Math.PI * 2);
      context.fill();
      context.shadowBlur = 0;
    }

    if (pointer.active && !reducedMotion.matches) {
      const glow = context.createRadialGradient(pointer.x, pointer.y, 0, pointer.x, pointer.y, 180);
      glow.addColorStop(0, 'rgba(0,204,255,.10)');
      glow.addColorStop(1, 'rgba(0,204,255,0)');
      context.globalAlpha = 1;
      context.fillStyle = glow;
      context.fillRect(pointer.x - 180, pointer.y - 180, 360, 360);
    }

    for (let i = ripples.length - 1; i >= 0; i -= 1) {
      const ripple = ripples[i];
      const age = (now - ripple.started) / 950;
      if (age >= 1) { ripples.splice(i, 1); continue; }
      context.globalAlpha = (1 - age) * .34;
      context.strokeStyle = '#63eaff';
      context.lineWidth = 1.2;
      context.beginPath();
      context.arc(ripple.x, ripple.y, 10 + age * 78, 0, Math.PI * 2);
      context.stroke();
    }
    context.globalAlpha = 1;
    context.shadowBlur = 0;
  }

  function animate(now) {
    if (document.hidden) { raf = 0; return; }
    raf = window.requestAnimationFrame(animate);
    if (now - lastFrame < 32) return;
    const delta = Math.min(80, now - (lastFrame || now));
    lastFrame = now;
    paint(now, delta);
  }

  function start() {
    window.cancelAnimationFrame(raf);
    lastFrame = 0;
    if (document.hidden) { paint(performance.now(), 0); return; }
    if (reducedMotion.matches) paint(performance.now(), 0);
    else raf = window.requestAnimationFrame(animate);
  }

  window.addEventListener('resize', resize, { passive: true });
  window.addEventListener('pointermove', (event) => {
    pointer.x = event.clientX;
    pointer.y = event.clientY;
    pointer.active = true;
  }, { passive: true });
  window.addEventListener('pointerleave', () => { pointer.active = false; }, { passive: true });
  window.addEventListener('pointerdown', (event) => {
    ripples.push({ x: event.clientX, y: event.clientY, started: performance.now() });
    if (ripples.length > 4) ripples.shift();
  }, { passive: true });
  document.addEventListener('visibilitychange', start);
  reducedMotion.addEventListener?.('change', start);

  document.querySelectorAll('.project-card').forEach((card) => {
    card.addEventListener('pointermove', (event) => {
      const bounds = card.getBoundingClientRect();
      card.style.setProperty('--pointer-x', `${event.clientX - bounds.left}px`);
      card.style.setProperty('--pointer-y', `${event.clientY - bounds.top}px`);
    }, { passive: true });
  });

  const progress = document.querySelector('.scroll-meter span');
  if (progress) {
    const updateProgress = () => {
      const maxScroll = document.documentElement.scrollHeight - window.innerHeight;
      progress.style.transform = `scaleX(${maxScroll > 0 ? Math.min(1, window.scrollY / maxScroll) : 0})`;
    };
    window.addEventListener('scroll', updateProgress, { passive: true });
    window.addEventListener('resize', updateProgress, { passive: true });
    updateProgress();
  }

  resize();
  start();
})();
