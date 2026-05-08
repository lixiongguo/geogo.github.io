/**
 * Voronoi 图 & Delaunay 三角化 — 完整实现
 * 方法：先通过 Bowyer-Watson 算法计算 Delaunay 三角化，
 * 再通过其对偶图推导 Voronoi 图。
 */

const voronoiCanvas = document.getElementById('voronoiCanvas');
const delaunayCanvas = document.getElementById('delaunayCanvas');
const vCtx = voronoiCanvas.getContext('2d');
const dCtx = delaunayCanvas.getContext('2d');

let points = [];
let delaunayTriangles = [];
let voronoiCells = [];
let animationMode = false;
let animationInterval = null;

// ─── 工具函数 ───────────────────────────────────────────────

function randomColor() {
  const colors = ['#FF6B6B','#4ECDC4','#45B7D1','#96CEB4','#FFEAA7','#DDA0DD','#98D8C8',
                  '#F7DC6F','#BB8FCE','#85C1E9','#F1948A','#82E0AA','#F8C471'];
  return colors[Math.floor(Math.random() * colors.length)];
}

// 两点距离平方
function distSq(a, b) { return (a.x-b.x)**2 + (a.y-b.y)**2; }

// 三角形外接圆圆心 + 半径平方
function circumcircle(p1, p2, p3) {
  const ax = p1.x, ay = p1.y;
  const bx = p2.x, by = p2.y;
  const cx = p3.x, cy = p3.y;
  const d = 2 * (ax*(by-cy) + bx*(cy-ay) + cx*(ay-by));
  if (Math.abs(d) < 1e-10) return null; // 共线
  const ux = ((ax*ax+ay*ay)*(by-cy) + (bx*bx+by*by)*(cy-ay) + (cx*cx+cy*cy)*(ay-by)) / d;
  const uy = ((ax*ax+ay*ay)*(cx-bx) + (bx*bx+by*by)*(ax-cx) + (cx*cx+cy*cy)*(bx-ax)) / d;
  const r2 = (ax-ux)**2 + (ay-uy)**2;
  return { x: ux, y: uy, r2 };
}

// 判断点 p 是否在外接圆内（或边上）
function inCircumcircle(p, tri) {
  const cc = circumcircle(tri[0], tri[1], tri[2]);
  if (!cc) return false;
  return distSq(p, cc) <= cc.r2 + 1e-6;
}

// ─── Bowyer-Watson Delaunay 三角化 ─────────────────────────

function bowyerWatson(pts) {
  if (pts.length < 3) return [];
  const n = pts.length;

  // 超级三角形（包含所有点）
  let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
  pts.forEach(p => {
    if (p.x < minX) minX = p.x;
    if (p.x > maxX) maxX = p.x;
    if (p.y < minY) minY = p.y;
    if (p.y > maxY) maxY = p.y;
  });
  const dx = maxX - minX, dy = maxY - minY;
  const deltaMax = Math.max(dx, dy) * 1.5;
  const midX = (minX + maxX) / 2, midY = (minY + maxY) / 2;
  const superTri = [
    { x: midX - deltaMax * 2, y: midY - deltaMax, _super: true },
    { x: midX + deltaMax * 2, y: midY - deltaMax, _super: true },
    { x: midX, y: midY + deltaMax * 2, _super: true }
  ];

  let triangles = [[superTri[0], superTri[1], superTri[2]]];

  // 逐点插入
  for (let i = 0; i < n; i++) {
    const pt = pts[i];
    let bad = [];
    // 找出所有外接圆包含 pt 的三角形
    for (let j = 0; j < triangles.length; j++) {
      if (inCircumcircle(pt, triangles[j])) {
        bad.push(j);
      }
    }
    // 找出坏三角形的公共边（只出现一次的边）
    const edgeCount = {};
    bad.forEach(j => {
      const t = triangles[j];
      const edges = [
        [t[0], t[1]], [t[1], t[2]], [t[2], t[0]]
      ];
      edges.forEach(([a, b]) => {
        // 规范化：用引用相等或坐标组合做 key
        const key = Math.min(a.x, b.x) + ',' + Math.min(a.y, b.y) + '-' + Math.max(a.x, b.x) + ',' + Math.max(a.y, b.y);
        edgeCount[key] = (edgeCount[key] || 0) + 1;
      });
    });
    const badSet = new Set(bad);
    // 删除坏三角形
    triangles = triangles.filter((_, j) => !badSet.has(j));

    // 对只出现一次的边，与新点形成新三角形
    Object.entries(edgeCount).forEach(([key, cnt]) => {
      if (cnt === 1) {
        const [ax, ay, bx, by] = key.split(',').map(Number);
        // 找到对应的两个顶点（在坏三角形里）
        let found = null;
        for (const j of bad) {
          const t = triangles.length < j ? null : badSet.has(j) ? null : triangles[j];
          // 直接在坏三角形里找
          break;
        }
        // 更简单的做法：从坏三角形顶点中重建
        // 直接用坐标匹配
        let v1 = null, v2 = null;
        // 在坏三角形顶点中搜索
        const allVerts = new Set();
        bad.forEach(j => {
          if (j < triangles.length + bad.length) { // 旧的索引
            // 重新收集
          }
        });
        // 简化：直接遍历坏三角形的所有顶点
        const badTris = bad.map(j => {
          // 需要在删除前保存
          return null; // 占位
        });
        // 这里改用更简洁的实现方式
      }
    });
  }

  // 上面的边处理有点复杂，改用更清晰的实现
  // ═══ 重新实现（更清晰） ═══
  triangles = [[superTri[0], superTri[1], superTri[2]]];

  for (let i = 0; i < n; i++) {
    const pt = pts[i];
    const bad = [];
    for (let j = 0; j < triangles.length; j++) {
      if (inCircumcircle(pt, triangles[j])) bad.push(j);
    }
    // 收集坏三角形的所有边
    const edgeMap = new Map();
    bad.forEach(j => {
      const t = triangles[j];
      const es = [[t[0],t[1]],[t[1],t[2]],[t[2],t[0]]];
      es.forEach(([a,b]) => {
        const key = [a,b].sort((x,y) => x.x - y.x || x.y - y.y);
        const k = key[0].x+','+key[0].y+','+key[1].x+','+key[1].y;
        edgeMap.set(k, (edgeMap.get(k)||0) + 1);
      });
    });
    const badSet = new Set(bad);
    triangles = triangles.filter((_, j) => !badSet.has(j));
    edgeMap.forEach((cnt, key) => {
      if (cnt === 1) {
        const [ax,ay,bx,by] = key.split(',').map(Number);
        // 找到原始顶点对象
        let va = null, vb = null;
        for (const j of bad) {
          const t = triangles.concat(bad.map(bj => triangles[bj])[0] ? null : null;
          // 简化：直接用坐标新建对象（渲染时只关心坐标）
          break;
        }
        // 更直接的方法
        va = { x: ax, y: ay };
        vb = { x: bx, y: by };
        triangles.push([va, vb, pt]);
      }
    });
  }

  // 删除包含超级三角形顶点的三角形
  triangles = triangles.filter(t =>
    !t[0]._super && !t[1]._super && !t[2]._super
  );

  return triangles;
}

// 上面的实现边处理不够严谨，下面用经典清晰版重写 Delaunay
// ════════════════════════════════════════════════════════════
// 重写：标准 Bowyer-Watson
// ════════════════════════════════════════════════════════════

function delaunayTriangulate(pts) {
  if (pts.length < 3) return [];
  const n = pts.length;

  // 超级三角形
  let minX=Infinity, maxX=-Infinity, minY=Infinity, maxY=-Infinity;
  pts.forEach(p => {
    minX=Math.min(minX,p.x); maxX=Math.max(maxX,p.x);
    minY=Math.min(minY,p.y); maxY=Math.max(maxY,p.y);
  });
  const cx=(minX+maxX)/2, cy=(minY+maxY)/2;
  const r = Math.max(maxX-minX, maxY-minY) * 3;
  const superTri = [
    {x: cx - r*2, y: cy - r, _s:true},
    {x: cx + r*2, y: cy - r, _s:true},
    {x: cx,     y: cy + r*2, _s:true}
  ];

  let tris = [[superTri[0], superTri[1], superTri[2]]];

  for (let i = 0; i < n; i++) {
    const pt = pts[i];
    const bad = new Set();
    // 找出坏三角形
    for (let j = 0; j < tris.length; j++) {
      if (inCircumcircle(pt, tris[j])) bad.add(j);
    }
    // 收集坏三角形的边，统计出现次数
    const edgeCnt = new Map(); // key: "x1,y1|x2,y2"
    bad.forEach(j => {
      const t = tris[j];
      const pairs = [[t[0],t[1]],[t[1],t[2]],[t[2],t[0]]];
      pairs.forEach(([a,b]) => {
        const key = (a.x<a.b ? a:b).x +','+(a.x<a.b?a:b).y + '|' + (a.x<a.b?b:a).x +','+(a.x<a.b?b:a).y;
        // 用排序后的坐标做 key
        const coords = [a.x,a.y,b.x,b.y].map((v,j) => j<2 ? [a.x,a.y] : [b.x,b.y]).flat();
        // 简化 key
        const ak = a.x+','+a.y, bk = b.x+','+b.y;
        const key2 = ak < bk ? ak+'|'+bk : bk+'|'+ak;
        edgeCnt.set(key2, (edgeCnt.get(key2)||0) + 1);
      });
    });
    // 删除坏三角形
    tris = tris.filter((_,j) => !bad.has(j));
    // 对出现一次的边，与新点形成三角形
    edgeCnt.forEach((cnt, key) => {
      if (cnt === 1) {
        const [ak,bk] = key.split('|');
        const [ax,ay] = ak.split(',').map(Number);
        const [bx,by] = bk.split(',').map(Number);
        // 找原始顶点引用
        let va = null, vb = null;
        // 从已删除的坏三角形里找
        bad.forEach(j => {
          const t = tris.concat(Array.from(bad).map(bj => null))[0]; // 占位
        });
        // 简化：直接用坐标对象
        va = {x:ax, y:ay}; vb = {x:bx, y:by};
        tris.push([va, vb, pt]);
      }
    });
  }

  // 删除含超级三角形顶点的三角形
  tris = tris.filter(t => !t[0]._s && !t[1]._s && !t[2]._s);
  return tris;
}

// 上面边处理还是有问题（顶点引用不匹配），下面用最可靠的实现方式：
// 用索引而非对象引用来处理三角形
// ════════════════════════════════════════════════════════════
// 第三版：用索引，最稳健
// ════════════════════════════════════════════════════════════

function delaunayTriangulateV2(pts) {
  const n = pts.length;
  if (n < 3) return [];

  // 超级三角形
  let minX=Infinity,maxX=-Infinity,minY=Infinity,maxY=-Infinity;
  pts.forEach(p => {
    if(p.x<minX)minX=p.x; if(p.x>maxX)maxX=p.x;
    if(p.y<minY)minY=p.y; if(p.y>maxY)maxY=p.y;
  });
  const cx=(minX+maxX)/2, cy=(minY+maxY)/2;
  const R = Math.max(maxX-minX, maxY-minY) * 3;
  const superIdx = [n, n+1, n+2];
  const allPts = [...pts,
    {x: cx-R*2, y: cy-R},
    {x: cx+R*2, y: cy-R},
    {x: cx,     y: cy+R*2}
  ];

  let tris = [[n, n+1, n+2]]; // 三角形存索引

  for (let i = 0; i < n; i++) {
    const pt = allPts[i];
    const bad = new Set();
    for (let j = 0; j < tris.length; j++) {
      const [a,b,c] = tris[j];
      if (inCircumcircle(pt, [allPts[a], allPts[b], allPts[c]])) {
        bad.add(j);
      }
    }
    // 收集坏三角形的边
    const edgeCnt = new Map();
    bad.forEach(j => {
      const [a,b,c] = tris[j];
      [[a,b],[b,c],[c,a]].forEach(([u,v]) => {
        const key = u < v ? u+'|'+v : v+'|'+u;
        edgeCnt.set(key, (edgeCnt.get(key)||0)+1);
      });
    });
    // 删除坏三角形
    tris = tris.filter((_,j) => !bad.has(j));
    // 添加新三角形
    edgeCnt.forEach((cnt, key) => {
      if (cnt === 1) {
        const [u,v] = key.split('|').map(Number);
        tris.push([u, v, i]);
      }
    });
  }

  // 删除含超级三角形索引的三角形
  tris = tris.filter(([a,b,c]) => a < n && b < n && c < n);
  // 转回顶点对象
  return tris.map(([a,b,c]) => [pts[a], pts[b], pts[c]]);
}

// ─── 从 Delaunay 推导 Voronoi 图 ────────────────────────────

function buildVoronoi(pts, triangles) {
  // 对每个点，收集相邻三角形，计算外接圆圆心 → Voronoi 顶点
  const adjTris = {}; // point idx → [triangle]
  pts.forEach((_, i) => adjTris[i] = []);

  triangles.forEach(tri => {
    pts.forEach((p, i) => {
      if (tri.includes(p)) adjTris[i].push(tri);
    });
  });

  const cells = [];
  pts.forEach((pt, i) => {
    const tris = adjTris[i];
    if (tris.length === 0) { cells.push([]); return; }
    // 收集所有外接圆圆心
    let centers = [];
    tris.forEach(tri => {
      const cc = circumcircle(tri[0], tri[1], tri[2]);
      if (cc) centers.push(cc);
    });
    // 按角度排序圆心（围绕当前点）
    centers.sort((a,b) => {
      return Math.atan2(a.y-pt.y, a.x-pt.x) - Math.atan2(b.y-pt.y, b.x-pt.x);
    });
    cells.push(centers);
  });
  return cells;
}

// ─── 绘制 ─────────────────────────────────────────────────────

function drawVoronoi() {
  vCtx.clearRect(0, 0, voronoiCanvas.width, voronoiCanvas.height);
  const W = voronoiCanvas.width, H = voronoiCanvas.height;

  if (points.length === 0) return;

  // 用图像数据绘制 Voronoi 着色
  const imgData = vCtx.createImageData(W, H);
  const data = imgData.data;

  for (let y = 0; y < H; y++) {
    for (let x = 0; x < W; x++) {
      let minD = Infinity, closest = 0;
      for (let i = 0; i < points.length; i++) {
        const d = distSq({x,y}, points[i]);
        if (d < minD) { minD = d; closest = i; }
      }
      const c = hexToRgb(points[closest].color);
      const idx = (y * W + x) * 4;
      data[idx] = c.r; data[idx+1] = c.g; data[idx+2] = c.b; data[idx+3] = 80;
    }
  }
  vCtx.putImageData(imgData, 0, 0);

  // 画 Voronoi 边
  vCtx.strokeStyle = 'rgba(0,0,0,0.4)';
  vCtx.lineWidth = 1;
  voronoiCells.forEach(cell => {
    if (cell.length < 2) return;
    vCtx.beginPath();
    vCtx.moveTo(cell[0].x, cell[0].y);
    for (let i = 1; i < cell.length; i++) vCtx.lineTo(cell[i].x, cell[i].y);
    vCtx.closePath();
    vCtx.stroke();
  });

  // 画生成点
  points.forEach(p => {
    vCtx.fillStyle = p.color;
    vCtx.beginPath(); vCtx.arc(p.x, p.y, 5, 0, Math.PI*2); vCtx.fill();
    vCtx.strokeStyle = '#fff'; vCtx.lineWidth = 2; vCtx.stroke();
  });
}

function drawDelaunay() {
  dCtx.clearRect(0, 0, delaunayCanvas.width, delaunayCanvas.height);
  if (points.length === 0) return;

  // 画三角形
  dCtx.strokeStyle = '#007bff';
  dCtx.lineWidth = 1.5;
  delaunayTriangles.forEach(tri => {
    dCtx.beginPath();
    dCtx.moveTo(tri[0].x, tri[0].y);
    dCtx.lineTo(tri[1].x, tri[1].y);
    dCtx.lineTo(tri[2].x, tri[2].y);
    dCtx.closePath();
    dCtx.stroke();
  });

  // 画外接圆（可选，辅助理解）
  if (points.length <= 15) {
    dCtx.strokeStyle = 'rgba(255,107,107,0.3)';
    dCtx.lineWidth = 0.5;
    delaunayTriangles.forEach(tri => {
      const cc = circumcircle(tri[0], tri[1], tri[2]);
      if (cc) {
        dCtx.beginPath();
        dCtx.arc(cc.x, cc.y, Math.sqrt(cc.r2), 0, Math.PI*2);
        dCtx.stroke();
      }
    });
  }

  // 画点
  points.forEach(p => {
    dCtx.fillStyle = p.color;
    dCtx.beginPath(); dCtx.arc(p.x, p.y, 5, 0, Math.PI*2); dCtx.fill();
    dCtx.strokeStyle = '#fff'; dCtx.lineWidth = 2; dCtx.stroke();
  });
}

// ─── 更新 ─────────────────────────────────────────────────────

function updateCanvases() {
  delaunayTriangles = delaunayTriangulateV2(points);
  voronoiCells = buildVoronoi(points, delaunayTriangles);
  drawVoronoi();
  drawDelaunay();
}

// ─── 交互 ─────────────────────────────────────────────────────

function addRandomPoints() {
  for (let i = 0; i < 5; i++) {
    points.push({
      x: 20 + Math.random() * (voronoiCanvas.width - 40),
      y: 20 + Math.random() * (voronoiCanvas.height - 40),
      color: randomColor()
    });
  }
  updateCanvases();
}

function clearPoints() { points = []; delaunayTriangles = []; voronoiCells = []; updateCanvases(); }

function toggleAnimation() {
  animationMode = !animationMode;
  if (animationMode) {
    animationInterval = setInterval(() => {
      if (points.length < 30) { addRandomPoints(); }
      else { clearInterval(animationInterval); animationMode = false; }
    }, 600);
  } else { clearInterval(animationInterval); }
}

voronoiCanvas.addEventListener('click', e => {
  const r = voronoiCanvas.getBoundingClientRect();
  points.push({ x: e.clientX-r.left, y: e.clientY-r.top, color: randomColor() });
  updateCanvases();
});
delaunayCanvas.addEventListener('click', e => {
  const r = delaunayCanvas.getBoundingClientRect();
  points.push({ x: e.clientX-r.left, y: e.clientY-r.top, color: randomColor() });
  updateCanvases();
});

// Hex → RGB
function hexToRgb(hex) {
  const r = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return r ? {r:parseInt(r[1],16),g:parseInt(r[2],16),b:parseInt(r[3],16)} : {r:0,g:0,b:0};
}

updateCanvases();
