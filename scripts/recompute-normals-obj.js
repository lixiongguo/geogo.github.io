/**
 * recompute-normals-obj.js — 计算 OBJ 顶点法线并导出
 *
 * 用法: node scripts/recompute-normals-obj.js <directory...>
 *       node scripts/recompute-normals-obj.js <file.obj...>
 *
 * 等价于 MeshLab: Filter → Normals → Compute → Export OBJ (with normals)
 * 对每个 OBJ:
 *   1. 读取 v / f
 *   2. 计算面法线（叉积）
 *   3. 平均到顶点法线（角度加权）
 *   4. 重写 OBJ，添加 vn 行和 f v/vt/vn 索引
 */

const fs = require('fs');
const path = require('path');

// 3D 向量运算
function sub(a, b) { return [a[0]-b[0], a[1]-b[1], a[2]-b[2]]; }
function cross(a, b) { return [a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0]]; }
function len(v) { return Math.sqrt(v[0]*v[0] + v[1]*v[1] + v[2]*v[2]); }
function normalize(v) { const l = len(v) || 1e-12; return [v[0]/l, v[1]/l, v[2]/l]; }
function add(a, b) { return [a[0]+b[0], a[1]+b[1], a[2]+b[2]]; }
function scale(v, s) { return [v[0]*s, v[1]*s, v[2]*s]; }
function dot(a, b) { return a[0]*b[0] + a[1]*b[1] + a[2]*b[2]; }

/** 向量夹角（弧度） */
function angleBetween(a, b, n) {
  const d = dot(a, b) / (len(a) * len(b));
  return Math.acos(Math.max(-1, Math.min(1, d)));
}

/** 三角面法线（按顶点顺序 CCW 指向外） */
function faceNormal(v0, v1, v2) {
  return normalize(cross(sub(v1, v0), sub(v2, v0)));
}

function processObj(filepath) {
  const content = fs.readFileSync(filepath, 'utf-8');
  const lines = content.split(/\r?\n/);

  // ---- 解析 ----
  const vertices = [];  // indexed by 0-based position
  let maxVi = 0;
  const faceLines = [];
  const texcoords = [];

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    if (line.startsWith('v ') && !line.startsWith('vt ') && !line.startsWith('vn ')) {
      const p = line.slice(2).trim().split(/\s+/).map(Number);
      if (p.length >= 3) vertices.push([p[0], p[1], p[2]]);
    } else if (line.startsWith('vt ')) {
      const t = line.slice(3).trim().split(/\s+/).map(Number);
      if (t.length >= 2) texcoords.push([t[0], t[1]]);
    } else if (line.startsWith('f ')) {
      const parts = line.slice(2).trim().split(/\s+/);
      const vIdx = [], faceT = [], faceN = [];
      for (const tok of parts) {
        const split = tok.split('/');
        const vi = parseInt(split[0]) - 1;
        if (isNaN(vi) || vi < 0) continue;
        vIdx.push(vi);
        if (vi + 1 > maxVi) maxVi = vi + 1;
        faceT.push(split.length > 1 && split[1] ? parseInt(split[1]) - 1 : -1);
        faceN.push(split.length > 2 && split[2] ? parseInt(split[2]) - 1 : -1);
      }
      if (vIdx.length >= 3) faceLines.push({ lineIdx: i, rawParts: parts, vIdx, faceT, faceN });
    }
  }

  if (vertices.length === 0 || faceLines.length === 0) {
    console.log(`  [跳过] 无数据: ${path.basename(filepath)}`);
    return;
  }

  // 确保顶点数组足够大
  const nV = Math.max(vertices.length, maxVi);
  while (vertices.length < nV) vertices.push([0, 0, 0]);

  // ---- 计算顶点法线（角度加权平均） ----
  const vertNorms = Array.from({ length: nV }, () => [0, 0, 0]);
  const vNormCount = new Array(nV).fill(0);

  const faceNorms = [];  // 每面的法线（1-indexed by face order）
  const faceVertPairs = [];  // faceVertPairs[fi][k] = { vi, vn }

  for (let fi = 0; fi < faceLines.length; fi++) {
    const fl = faceLines[fi];
    const nv = fl.vIdx.length;
    if (nv < 3) continue;

    // 扇三角化：用第一个顶点作为锚点
    for (let k = 1; k < nv - 1; k++) {
      const i0 = fl.vIdx[0], i1 = fl.vIdx[k], i2 = fl.vIdx[k + 1];
      const v0 = vertices[i0], v1 = vertices[i1], v2 = vertices[i2];
      const fn = faceNormal(v0, v1, v2);

      // 角度加权累加到各顶点
      for (const viTri of [i0, i1, i2]) {
        const curr = vertices[viTri];
        const others = [i0, i1, i2].filter(x => x !== viTri);
        const a = sub(vertices[others[0]], curr);
        const b = sub(vertices[others[1]], curr);
        const angle = angleBetween(a, b, fn);
        vertNorms[viTri] = add(vertNorms[viTri], scale(fn, angle));
        vNormCount[viTri]++;
      }
    }
  }

  // 归一化所有顶点法线
  for (let i = 0; i < nV; i++) {
    vertNorms[i] = normalize(vertNorms[i]);
  }

  // ---- 重写 OBJ ----
  const outLines = [];
  let vi = 0, ti = 0, fi = 0;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    if (line.startsWith('v ')) {
      outLines.push(`v ${vertices[vi][0].toFixed(6)} ${vertices[vi][1].toFixed(6)} ${vertices[vi][2].toFixed(6)}`);
      vi++;
    } else if (line.startsWith('vt ')) {
      outLines.push(line);
      ti++;
    } else if (line.startsWith('vn ') || line.startsWith('s ') || line.startsWith('mtllib ') || line.startsWith('usemtl ')) {
      // 跳过旧法线、smoothing group、材质引用
      continue;
    } else if (line.startsWith('f ')) {
      const fl = faceLines[fi++];
      const faceStr = fl.rawParts.map(tok => {
        const split = tok.split('/');
        const viIdx = parseInt(split[0]);    // 1-based
        const tiIdx = (split.length > 1 && split[1]) ? parseInt(split[1]) : 0;
        // 使用计算出的顶点法线索引（= vertex index, 因为 per-vertex normal）
        if (tiIdx > 0) {
          return `${viIdx}/${tiIdx}/${viIdx}`;
        } else {
          return `${viIdx}//${viIdx}`;
        }
      }).join(' ');
      outLines.push(`f ${faceStr}`);
    } else {
      outLines.push(line);
    }
  }

  // 在顶点之后、面之前插入法线
  const vEndIdx = outLines.findIndex((l, idx) => {
    // 找到最后一个 v 行
    const lastV = outLines.map((l, i) => l.startsWith('v ') ? i : -1).filter(x => x >= 0).pop();
    return idx > lastV;
  });
  const insertAt = outLines.findIndex((l, idx) => {
    if (idx <= vEndIdx) return false;
    return l.startsWith('f ') || l.startsWith('#') || l.startsWith('v') || l.trim() === '';
  });
  const vnLines = vertNorms.map(n => `vn ${n[0].toFixed(6)} ${n[1].toFixed(6)} ${n[2].toFixed(6)}`);
  const insPos = insertAt >= 0 ? insertAt : outLines.length;
  outLines.splice(insPos, 0, ...vnLines);

  fs.writeFileSync(filepath, outLines.join('\n'), 'utf-8');

  console.log(`  [完成] ${path.basename(filepath)}`);
  console.log(`    顶点: ${vertices.length}  面: ${faceLines.length}  法线: ${vertNorms.length}`);
}

// ============= 入口 =============
function walkDir(dir) {
  const files = [];
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) files.push(...walkDir(full));
    else if (entry.name.endsWith('.obj')) files.push(full);
  }
  return files;
}

function main() {
  const args = process.argv.slice(2);
  if (args.length === 0) {
    console.log('用法: node scripts/recompute-normals-obj.js <directory|file.obj> ...');
    process.exit(1);
  }

  const targets = args.flatMap(arg => {
    const stat = fs.statSync(arg);
    if (stat.isDirectory()) return walkDir(arg);
    return [path.resolve(arg)];
  });

  console.log(`处理 ${targets.length} 个文件...`);
  targets.forEach(f => processObj(f));
  console.log('全部完成!');
}

main();
