/**
 * Computational Geometry Polygon Mesh Background
 * 多边形网格 + Delaunay三角化 科技感背景
 * 鼠标互动：轻微排斥粒子
 */
class GeoMeshBackground {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    if (!this.canvas) return;
    this.ctx = this.canvas.getContext('2d');

    this.config = {
      particleCount: 70,
      maxLinkDist: 140,
      mouseRadius: 180,
      particleSpeed: 0.25,
      fillOpacity: 0.018,
      linkOpacity: 0.08,
      particleSize: 1.8,
      color: [99, 102, 241]  // 统一 Indigo
    };

    this.mouse = { x: undefined, y: undefined };
    this.points = [];

    this.init();
  }

  init() {
    this.resize();
    window.addEventListener('resize', () => this.resize());
    this.createPoints();

    window.addEventListener('mousemove', (e) => {
      this.mouse.x = e.clientX;
      this.mouse.y = e.clientY;
    });
    window.addEventListener('mouseleave', () => {
      this.mouse.x = undefined;
      this.mouse.y = undefined;
    });

    this.animate();
  }

  createPoints() {
    this.points = [];
    const w = window.innerWidth;
    const h = window.innerHeight;

    for (let i = 0; i < this.config.particleCount; i++) {
      this.points.push({
        x: Math.random() * w,
        y: Math.random() * h,
        vx: (Math.random() - 0.5) * this.config.particleSpeed,
        vy: (Math.random() - 0.5) * this.config.particleSpeed,
        baseRadius: Math.random() * 1 + 1.5,
        radius: 2
      });
    }
  }

  resize() {
    const dpr = Math.min(window.devicePixelRatio, 2);
    this.canvas.width = window.innerWidth * dpr;
    this.canvas.height = window.innerHeight * dpr;
    this.canvas.style.width = window.innerWidth + 'px';
    this.canvas.style.height = window.innerHeight + 'px';
    this.ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }

  // Bowyer-Watson Delaunay 三角化
  delaunay(points) {
    if (points.length < 3) return [];
    const w = window.innerWidth;
    const h = window.innerHeight;
    const margin = 500;
    const st = [
      { x: -margin, y: -margin },
      { x: w + margin, y: -margin },
      { x: w / 2, y: h + margin * 2 }
    ];

    let triangles = [{ a: st[0], b: st[1], c: st[2] }];

    for (const p of points) {
      let badTriangles = [];
      for (const tri of triangles) {
        if (this.inCircumcircle(p, tri)) badTriangles.push(tri);
      }

      let polygon = [];
      for (const tri of badTriangles) {
        const edges = [[tri.a, tri.b], [tri.b, tri.c], [tri.c, tri.a]];
        for (const edge of edges) {
          let shared = false;
          for (const other of badTriangles) {
            if (other === tri) continue;
            const otherEdges = [[other.a, other.b], [other.b, other.c], [other.c, other.a]];
            for (const oe of otherEdges) {
              if ((edge[0] === oe[0] && edge[1] === oe[1]) ||
                  (edge[0] === oe[1] && edge[1] === oe[0])) {
                shared = true;
                break;
              }
            }
            if (shared) break;
          }
          if (!shared) polygon.push(edge);
        }
      }

      triangles = triangles.filter(t => !badTriangles.includes(t));
      for (const edge of polygon) {
        triangles.push({ a: edge[0], b: edge[1], c: p });
      }
    }

    return triangles.filter(tri =>
      !st.includes(tri.a) && !st.includes(tri.b) && !st.includes(tri.c)
    );
  }

  inCircumcircle(p, tri) {
    const ax = tri.a.x - p.x, ay = tri.a.y - p.y;
    const bx = tri.b.x - p.x, by = tri.b.y - p.y;
    const cx = tri.c.x - p.x, cy = tri.c.y - p.y;
    const det = (ax * ax + ay * ay) * (bx * cy - cx * by)
              - (bx * bx + by * by) * (ax * cy - cx * ay)
              + (cx * cx + cy * cy) * (ax * by - bx * ay);
    const orient = (tri.b.x - tri.a.x) * (tri.c.y - tri.a.y)
                 - (tri.b.y - tri.a.y) * (tri.c.x - tri.a.x);
    return orient > 0 ? det > 0 : det < 0;
  }

  update() {
    const w = window.innerWidth;
    const h = window.innerHeight;
    const cfg = this.config;

    for (const p of this.points) {
      // 鼠标排斥（温和持续）
      if (this.mouse.x !== undefined) {
        const dx = p.x - this.mouse.x;
        const dy = p.y - this.mouse.y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < cfg.mouseRadius && dist > 0) {
          const force = (1 - dist / cfg.mouseRadius);
          p.vx += (dx / dist) * force * 0.03;
          p.vy += (dy / dist) * force * 0.03;
        }
      }

      p.vx *= 0.99;
      p.vy *= 0.99;

      const speed = Math.sqrt(p.vx * p.vx + p.vy * p.vy);
      if (speed < cfg.particleSpeed * 0.3) {
        p.vx += (Math.random() - 0.5) * 0.05;
        p.vy += (Math.random() - 0.5) * 0.05;
      }
      if (speed > cfg.particleSpeed * 3) {
        p.vx *= 0.95;
        p.vy *= 0.95;
      }

      p.x += p.vx;
      p.y += p.vy;

      if (p.x < -20) p.x = w + 20;
      if (p.x > w + 20) p.x = -20;
      if (p.y < -20) p.y = h + 20;
      if (p.y > h + 20) p.y = -20;
    }
  }

  draw() {
    const ctx = this.ctx;
    const w = window.innerWidth;
    const h = window.innerHeight;
    const cfg = this.config;
    const [r, g, b] = cfg.color;

    ctx.clearRect(0, 0, w, h);
    const tris = this.delaunay(this.points);

    // 三角形填充（统一颜色）
    ctx.fillStyle = `rgba(${r},${g},${b},${cfg.fillOpacity})`;
    for (const tri of tris) {
      ctx.beginPath();
      ctx.moveTo(tri.a.x, tri.a.y);
      ctx.lineTo(tri.b.x, tri.b.y);
      ctx.lineTo(tri.c.x, tri.c.y);
      ctx.closePath();
      ctx.fill();
    }

    // 边
    ctx.lineWidth = 0.5;
    ctx.strokeStyle = `rgba(${r},${g},${b},${cfg.linkOpacity})`;
    for (const tri of tris) {
      const edges = [[tri.a, tri.b], [tri.b, tri.c], [tri.c, tri.a]];
      for (const [a, e] of edges) {
        const edgeLen = Math.sqrt((a.x - e.x) ** 2 + (a.y - e.y) ** 2);
        if (edgeLen > cfg.maxLinkDist * 1.5) continue;
        ctx.beginPath();
        ctx.moveTo(a.x, a.y);
        ctx.lineTo(e.x, e.y);
        ctx.stroke();
      }
    }

    // 顶点
    ctx.fillStyle = `rgba(${r},${g},${b},0.35)`;
    for (const p of this.points) {
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.baseRadius, 0, Math.PI * 2);
      ctx.fill();
    }
  }

  animate() {
    this.update();
    this.draw();
    requestAnimationFrame(() => this.animate());
  }
}

document.addEventListener('DOMContentLoaded', () => {
  new GeoMeshBackground('particle-canvas');
});
