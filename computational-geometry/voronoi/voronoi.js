/**
 * Voronoi / Delaunay and Power Diagram / Weighted Delaunay demo.
 *
 * Ordinary mode:
 *   - Delaunay: Bowyer-Watson triangulation.
 *   - Voronoi: rasterized nearest-site regions plus circumcenter cells.
 *
 * Weighted mode:
 *   - Power diagram: rasterized power distance pi_i(x)=||x-p_i||^2-w_i.
 *   - Weighted Delaunay: dual graph extracted from adjacent power cells.
 */

const voronoiCanvas = document.getElementById('voronoiCanvas');
const delaunayCanvas = document.getElementById('delaunayCanvas');
const vCtx = voronoiCanvas.getContext('2d');
const dCtx = delaunayCanvas.getContext('2d');

const modeSelect = document.getElementById('diagramMode');
const randomCountInput = document.getElementById('randomCount');
const selectedLabel = document.getElementById('selectedLabel');
const weightSlider = document.getElementById('weightSlider');
const weightValue = document.getElementById('weightValue');
const pointList = document.getElementById('pointList');
const leftTitle = document.getElementById('leftTitle');
const rightTitle = document.getElementById('rightTitle');

let points = [];
let delaunayTriangles = [];
let voronoiCells = [];
let weightedEdges = [];
let diagramMode = 'ordinary';
let selectedPoint = -1;
let animationMode = false;
let animationInterval = null;

function randomColor() {
  const colors = [
    '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD',
    '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9', '#F1948A', '#82E0AA'
  ];
  return colors[Math.floor(Math.random() * colors.length)];
}

function hexToRgb(hex) {
  const r = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return r ? { r: parseInt(r[1], 16), g: parseInt(r[2], 16), b: parseInt(r[3], 16) } : { r: 0, g: 0, b: 0 };
}

function distSq(a, b) {
  return (a.x - b.x) ** 2 + (a.y - b.y) ** 2;
}

function siteDistanceSq(x, y, p) {
  return (x - p.x) ** 2 + (y - p.y) ** 2;
}

function normalizedWeightToPower(weight01) {
  const L2 = voronoiCanvas.width ** 2 + voronoiCanvas.height ** 2;
  return Math.max(0, Math.min(1, Number(weight01) || 0)) * L2;
}

function powerDistance(x, y, p) {
  return siteDistanceSq(x, y, p) - normalizedWeightToPower(p.weight || 0);
}

function circumcircle(p1, p2, p3) {
  const ax = p1.x, ay = p1.y;
  const bx = p2.x, by = p2.y;
  const cx = p3.x, cy = p3.y;
  const d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by));
  if (Math.abs(d) < 1e-10) return null;

  const ux = (
    (ax * ax + ay * ay) * (by - cy) +
    (bx * bx + by * by) * (cy - ay) +
    (cx * cx + cy * cy) * (ay - by)
  ) / d;
  const uy = (
    (ax * ax + ay * ay) * (cx - bx) +
    (bx * bx + by * by) * (ax - cx) +
    (cx * cx + cy * cy) * (bx - ax)
  ) / d;

  return { x: ux, y: uy, r2: (ax - ux) ** 2 + (ay - uy) ** 2 };
}

function inCircumcircle(p, tri) {
  const cc = circumcircle(tri[0], tri[1], tri[2]);
  return !!cc && distSq(p, cc) <= cc.r2 + 1e-6;
}

function delaunayTriangulate(pts) {
  const n = pts.length;
  if (n < 3) return [];

  let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
  pts.forEach((p) => {
    minX = Math.min(minX, p.x);
    maxX = Math.max(maxX, p.x);
    minY = Math.min(minY, p.y);
    maxY = Math.max(maxY, p.y);
  });

  const cx = (minX + maxX) / 2;
  const cy = (minY + maxY) / 2;
  const radius = Math.max(maxX - minX, maxY - minY, 100) * 8;
  const allPts = pts.concat([
    { x: cx - radius, y: cy - radius, _super: true },
    { x: cx + radius, y: cy - radius, _super: true },
    { x: cx, y: cy + radius, _super: true }
  ]);

  let tris = [[n, n + 1, n + 2]];

  for (let i = 0; i < n; i++) {
    const bad = new Set();
    for (let ti = 0; ti < tris.length; ti++) {
      const tri = tris[ti].map((idx) => allPts[idx]);
      if (inCircumcircle(allPts[i], tri)) bad.add(ti);
    }

    const edgeCount = new Map();
    bad.forEach((ti) => {
      const [a, b, c] = tris[ti];
      [[a, b], [b, c], [c, a]].forEach(([u, v]) => {
        const key = u < v ? `${u}|${v}` : `${v}|${u}`;
        edgeCount.set(key, (edgeCount.get(key) || 0) + 1);
      });
    });

    tris = tris.filter((_, ti) => !bad.has(ti));

    edgeCount.forEach((count, key) => {
      if (count !== 1) return;
      const [u, v] = key.split('|').map(Number);
      tris.push([u, v, i]);
    });
  }

  return tris
    .filter(([a, b, c]) => a < n && b < n && c < n)
    .map(([a, b, c]) => [pts[a], pts[b], pts[c]]);
}

function buildVoronoi(pts, triangles) {
  const adjTris = new Map();
  pts.forEach((p) => adjTris.set(p.id, []));

  triangles.forEach((tri) => {
    tri.forEach((p) => adjTris.get(p.id)?.push(tri));
  });

  return pts.map((pt) => {
    const centers = [];
    (adjTris.get(pt.id) || []).forEach((tri) => {
      const cc = circumcircle(tri[0], tri[1], tri[2]);
      if (cc) centers.push(cc);
    });
    centers.sort((a, b) => Math.atan2(a.y - pt.y, a.x - pt.x) - Math.atan2(b.y - pt.y, b.x - pt.x));
    return centers;
  });
}

function nearestSiteIndex(x, y, weighted) {
  let best = 0;
  let bestValue = Infinity;
  for (let i = 0; i < points.length; i++) {
    const value = weighted ? powerDistance(x, y, points[i]) : siteDistanceSq(x, y, points[i]);
    if (value < bestValue) {
      bestValue = value;
      best = i;
    }
  }
  return best;
}

function drawRasterDiagram(ctx, weighted) {
  const W = voronoiCanvas.width;
  const H = voronoiCanvas.height;
  const imgData = ctx.createImageData(W, H);
  const data = imgData.data;
  const labels = new Int16Array(W * H);

  for (let y = 0; y < H; y++) {
    for (let x = 0; x < W; x++) {
      const site = nearestSiteIndex(x, y, weighted);
      labels[y * W + x] = site;
      const c = hexToRgb(points[site].color);
      const idx = (y * W + x) * 4;
      data[idx] = c.r;
      data[idx + 1] = c.g;
      data[idx + 2] = c.b;
      data[idx + 3] = 82;
    }
  }

  ctx.putImageData(imgData, 0, 0);
  drawCellBoundaries(ctx, labels, W, H);
  return labels;
}

function drawCellBoundaries(ctx, labels, W, H) {
  ctx.fillStyle = 'rgba(0,0,0,0.55)';
  for (let y = 1; y < H; y++) {
    for (let x = 1; x < W; x++) {
      const a = labels[y * W + x];
      if (a !== labels[y * W + x - 1] || a !== labels[(y - 1) * W + x]) {
        ctx.fillRect(x, y, 1, 1);
      }
    }
  }
}

function extractWeightedDelaunayEdges(labels) {
  const W = voronoiCanvas.width;
  const H = voronoiCanvas.height;
  const edges = new Set();

  for (let y = 0; y < H - 1; y++) {
    for (let x = 0; x < W - 1; x++) {
      const a = labels[y * W + x];
      const right = labels[y * W + x + 1];
      const down = labels[(y + 1) * W + x];
      if (a !== right) edges.add(edgeKey(a, right));
      if (a !== down) edges.add(edgeKey(a, down));
    }
  }

  return Array.from(edges).map((key) => key.split('|').map(Number));
}

function edgeKey(a, b) {
  return a < b ? `${a}|${b}` : `${b}|${a}`;
}

function drawSites(ctx, showWeights) {
  points.forEach((p, i) => {
    if (showWeights) {
      const r = Math.sqrt(normalizedWeightToPower(p.weight || 0));
      ctx.strokeStyle = 'rgba(0,123,255,.28)';
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      ctx.arc(p.x, p.y, Math.min(80, r), 0, Math.PI * 2);
      ctx.stroke();
    }

    ctx.fillStyle = p.color;
    ctx.beginPath();
    ctx.arc(p.x, p.y, i === selectedPoint ? 7 : 5, 0, Math.PI * 2);
    ctx.fill();
    ctx.strokeStyle = i === selectedPoint ? '#111' : '#fff';
    ctx.lineWidth = i === selectedPoint ? 3 : 2;
    ctx.stroke();

    ctx.fillStyle = '#222';
    ctx.font = '11px sans-serif';
    ctx.fillText(String(i), p.x + 8, p.y - 8);
  });
}

function drawVoronoi() {
  vCtx.clearRect(0, 0, voronoiCanvas.width, voronoiCanvas.height);
  if (points.length === 0) return;

  const weighted = diagramMode === 'power';
  drawRasterDiagram(vCtx, weighted);

  if (!weighted) {
    vCtx.strokeStyle = 'rgba(0,0,0,0.35)';
    vCtx.lineWidth = 1;
    voronoiCells.forEach((cell) => {
      if (cell.length < 2) return;
      vCtx.beginPath();
      vCtx.moveTo(cell[0].x, cell[0].y);
      for (let i = 1; i < cell.length; i++) vCtx.lineTo(cell[i].x, cell[i].y);
      vCtx.closePath();
      vCtx.stroke();
    });
  }

  drawSites(vCtx, weighted);
}

function drawDelaunay() {
  dCtx.clearRect(0, 0, delaunayCanvas.width, delaunayCanvas.height);
  if (points.length === 0) return;

  if (diagramMode === 'power') {
    drawWeightedDelaunay();
  } else {
    drawOrdinaryDelaunay();
  }

  drawSites(dCtx, diagramMode === 'power');
}

function drawOrdinaryDelaunay() {
  dCtx.strokeStyle = '#007bff';
  dCtx.lineWidth = 1.5;
  delaunayTriangles.forEach((tri) => {
    dCtx.beginPath();
    dCtx.moveTo(tri[0].x, tri[0].y);
    dCtx.lineTo(tri[1].x, tri[1].y);
    dCtx.lineTo(tri[2].x, tri[2].y);
    dCtx.closePath();
    dCtx.stroke();
  });

  if (points.length <= 15) {
    dCtx.strokeStyle = 'rgba(255,107,107,0.28)';
    dCtx.lineWidth = 0.5;
    delaunayTriangles.forEach((tri) => {
      const cc = circumcircle(tri[0], tri[1], tri[2]);
      if (!cc) return;
      dCtx.beginPath();
      dCtx.arc(cc.x, cc.y, Math.sqrt(cc.r2), 0, Math.PI * 2);
      dCtx.stroke();
    });
  }
}

function drawWeightedDelaunay() {
  dCtx.strokeStyle = '#7c3aed';
  dCtx.lineWidth = 2;
  weightedEdges.forEach(([i, j]) => {
    const a = points[i];
    const b = points[j];
    if (!a || !b) return;
    dCtx.beginPath();
    dCtx.moveTo(a.x, a.y);
    dCtx.lineTo(b.x, b.y);
    dCtx.stroke();
  });

  dCtx.fillStyle = 'rgba(124,58,237,.08)';
  weightedEdges.forEach(([i, j]) => {
    const a = points[i];
    const b = points[j];
    if (!a || !b) return;
    dCtx.beginPath();
    dCtx.arc((a.x + b.x) / 2, (a.y + b.y) / 2, 3, 0, Math.PI * 2);
    dCtx.fill();
  });
}

function updateCanvases() {
  points.forEach((p, i) => { p.id = i; });
  leftTitle.textContent = diagramMode === 'power' ? 'Power Diagram（带权 Voronoi）' : 'Voronoi 图';
  rightTitle.textContent = diagramMode === 'power' ? 'Weighted Delaunay（对偶图）' : 'Delaunay 三角化';

  delaunayTriangles = delaunayTriangulate(points);
  voronoiCells = buildVoronoi(points, delaunayTriangles);

  if (diagramMode === 'power' && points.length > 0) {
    const labels = drawRasterDiagram(vCtx, true);
    weightedEdges = extractWeightedDelaunayEdges(labels);
  } else {
    weightedEdges = [];
  }

  drawVoronoi();
  drawDelaunay();
  renderPointList();
}

function addPoint(x, y, weight = 0) {
  points.push({ id: points.length, x, y, weight: clampWeight01(weight), color: randomColor() });
  selectedPoint = points.length - 1;
}

function addRandomPoints() {
  const count = Math.max(1, Math.min(80, parseInt(randomCountInput.value, 10) || 10));
  points = [];
  for (let i = 0; i < count; i++) {
    addPoint(
      24 + Math.random() * (voronoiCanvas.width - 48),
      24 + Math.random() * (voronoiCanvas.height - 48),
      diagramMode === 'power' ? Math.random() : 0
    );
  }
  selectedPoint = points.length ? 0 : -1;
  syncSelectedWeightControls();
  updateCanvases();
}

function clearPoints() {
  points = [];
  delaunayTriangles = [];
  voronoiCells = [];
  weightedEdges = [];
  selectedPoint = -1;
  syncSelectedWeightControls();
  updateCanvases();
}

function toggleAnimation() {
  animationMode = !animationMode;
  if (animationMode) {
    animationInterval = setInterval(() => {
      if (points.length < 45) {
        addPoint(
          24 + Math.random() * (voronoiCanvas.width - 48),
          24 + Math.random() * (voronoiCanvas.height - 48),
          diagramMode === 'power' ? Math.random() : 0
        );
        updateCanvases();
      } else {
        clearInterval(animationInterval);
        animationMode = false;
      }
    }, 450);
  } else {
    clearInterval(animationInterval);
  }
}

function setMode(mode) {
  diagramMode = mode;
  updateCanvases();
}

function setSelectedWeight(value) {
  if (selectedPoint < 0 || !points[selectedPoint]) return;
  const weight = clampWeight01(value);
  points[selectedPoint].weight = weight;
  weightSlider.value = weight;
  weightValue.textContent = formatWeight(weight);
  updateCanvases();
}

function setPointWeight(index, value) {
  if (!points[index]) return;
  points[index].weight = clampWeight01(value);
  selectedPoint = index;
  syncSelectedWeightControls();
  updateCanvases();
}

function randomizeWeights() {
  points.forEach((p) => {
    p.weight = Math.random();
  });
  syncSelectedWeightControls();
  updateCanvases();
}

function resetWeights() {
  points.forEach((p) => { p.weight = 0; });
  syncSelectedWeightControls();
  updateCanvases();
}

function selectNearestPoint(x, y) {
  let best = -1;
  let bestD = 12 * 12;
  points.forEach((p, i) => {
    const d = siteDistanceSq(x, y, p);
    if (d < bestD) {
      best = i;
      bestD = d;
    }
  });
  return best;
}

function handleCanvasClick(canvas, e) {
  const r = canvas.getBoundingClientRect();
  const x = (e.clientX - r.left) * (canvas.width / r.width);
  const y = (e.clientY - r.top) * (canvas.height / r.height);
  const nearest = selectNearestPoint(x, y);
  if (nearest >= 0) {
    selectedPoint = nearest;
  } else {
    addPoint(x, y, 0);
  }
  syncSelectedWeightControls();
  updateCanvases();
}

function syncSelectedWeightControls() {
  const p = points[selectedPoint];
  if (!p) {
    selectedLabel.textContent = '未选中节点';
    weightSlider.value = 0;
    weightValue.textContent = '0.000';
    return;
  }
  selectedLabel.textContent = `节点 ${selectedPoint}`;
  weightSlider.value = p.weight || 0;
  weightValue.textContent = formatWeight(p.weight || 0);
}

function clampWeight01(value) {
  return Math.max(0, Math.min(1, Number(value) || 0));
}

function formatWeight(value) {
  return clampWeight01(value).toFixed(3);
}

function renderPointList() {
  pointList.innerHTML = '';
  points.forEach((p, i) => {
    const row = document.createElement('div');
    row.className = 'point-row' + (i === selectedPoint ? ' selected' : '');
    row.innerHTML = `
      <span><span class="swatch" style="background:${p.color}"></span> #${i} (${Math.round(p.x)}, ${Math.round(p.y)})</span>
      <label style="display:flex;align-items:center;gap:6px;">
        w
        <input type="range" min="0" max="1" value="${p.weight || 0}" step="0.001" style="width:120px">
        <span class="weight-value">${formatWeight(p.weight || 0)}</span>
      </label>
    `;
    row.addEventListener('click', () => {
      selectedPoint = i;
      syncSelectedWeightControls();
      updateCanvases();
    });
    row.querySelector('input').addEventListener('click', (e) => e.stopPropagation());
    row.querySelector('input').addEventListener('input', (e) => setPointWeight(i, e.target.value));
    pointList.appendChild(row);
  });
}

voronoiCanvas.addEventListener('click', (e) => handleCanvasClick(voronoiCanvas, e));
delaunayCanvas.addEventListener('click', (e) => handleCanvasClick(delaunayCanvas, e));

window.addRandomPoints = addRandomPoints;
window.clearPoints = clearPoints;
window.toggleAnimation = toggleAnimation;
window.setMode = setMode;
window.setSelectedWeight = setSelectedWeight;
window.randomizeWeights = randomizeWeights;
window.resetWeights = resetWeights;

addRandomPoints();
