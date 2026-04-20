/**
 * normalize-obj.js - OBJ 顶点坐标归一化脚本
 * 
 * 用法: node scripts/normalize-obj.js <file.obj> [file.obj ...]
 *       node scripts/normalize-obj.js <directory>
 * 
 * 将 OBJ 文件的顶点居中到原点，并缩放到单位尺寸（最大维度为 1.0）
 */

const fs = require('fs');
const path = require('path');

function normalizeObj(filepath) {
  const content = fs.readFileSync(filepath, 'utf-8');
  const lines = content.split(/\r?\n/);

  const vertices = [];
  const vIndices = [];

  lines.forEach((line, i) => {
    if (line.startsWith('v ')) {
      const parts = line.slice(2).trim().split(/\s+/);
      vertices.push([parseFloat(parts[0]), parseFloat(parts[1]), parseFloat(parts[2])]);
      vIndices.push(i);
    }
  });

  if (vertices.length === 0) {
    console.log(`  [跳过] 无顶点数据: ${filepath}`);
    return;
  }

  // 计算包围盒
  const xs = vertices.map(v => v[0]);
  const ys = vertices.map(v => v[1]);
  const zs = vertices.map(v => v[2]);
  const xmin = Math.min(...xs), xmax = Math.max(...xs);
  const ymin = Math.min(...ys), ymax = Math.max(...ys);
  const zmin = Math.min(...zs), zmax = Math.max(...zs);
  const center = [(xmin + xmax) / 2, (ymin + ymax) / 2, (zmin + zmax) / 2];
  const maxDim = Math.max(xmax - xmin, ymax - ymin, zmax - zmin);

  // 归一化顶点
  vIndices.forEach((lineIdx, vi) => {
    const v = vertices[vi];
    const nv = [
      (v[0] - center[0]) / maxDim,
      (v[1] - center[1]) / maxDim,
      (v[2] - center[2]) / maxDim
    ];
    lines[lineIdx] = `v ${nv[0].toFixed(6)} ${nv[1].toFixed(6)} ${nv[2].toFixed(6)}`;
  });

  fs.writeFileSync(filepath, lines.join('\n'), 'utf-8');

  // 验证
  const newXs = vertices.map(v => (v[0] - center[0]) / maxDim);
  const newYs = vertices.map(v => (v[1] - center[1]) / maxDim);
  const newZs = vertices.map(v => (v[2] - center[2]) / maxDim);
  const newMaxDim = Math.max(
    Math.max(...newXs) - Math.min(...newXs),
    Math.max(...newYs) - Math.min(...newYs),
    Math.max(...newZs) - Math.min(...newZs)
  );

  console.log(`  [完成] ${path.basename(filepath)}`);
  console.log(`    顶点: ${vertices.length}, 包围盒中心: [${center.map(c => c.toFixed(2)).join(', ')}]`);
  console.log(`    归一化后范围: X[${Math.min(...newXs).toFixed(4)}, ${Math.max(...newXs).toFixed(4)}]  Y[${Math.min(...newYs).toFixed(4)}, ${Math.max(...newYs).toFixed(4)}]  Z[${Math.min(...newZs).toFixed(4)}, ${Math.max(...newZs).toFixed(4)}]  maxDim=${newMaxDim.toFixed(4)}`);
}

function walkDir(dir) {
  const files = [];
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      files.push(...walkDir(full));
    } else if (entry.name.endsWith('.obj')) {
      files.push(full);
    }
  }
  return files;
}

function main() {
  const args = process.argv.slice(2);

  if (args.length === 0 || args.includes('--help') || args.includes('-h')) {
    console.log('用法: node scripts/normalize-obj.js <file.obj> [file.obj ...]');
    console.log('      node scripts/normalize-obj.js <directory>');
    console.log('');
    console.log('示例:');
    console.log('  node scripts/normalize-obj.js model.obj');
    console.log('  node scripts/normalize-obj.js assets/Models/');
    process.exit(args.includes('--help') || args.includes('-h') ? 0 : 1);
  }

  const targets = args.flatMap(arg => {
    const stat = fs.statSync(arg);
    if (stat.isDirectory()) {
      return walkDir(arg);
    }
    return [path.resolve(arg)];
  });

  console.log(`归一化 ${targets.length} 个文件...`);
  targets.forEach(f => normalizeObj(f));
  console.log('全部完成!');
}

main();
