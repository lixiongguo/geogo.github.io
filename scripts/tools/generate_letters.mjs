import * as THREE from 'three';
import { Font } from 'three/examples/jsm/loaders/FontLoader.js';
import { TextGeometry } from 'three/examples/jsm/geometries/TextGeometry.js';
import fs from 'fs';
import path from 'path';

// 下载字体文件到本地
const FONT_URL = 'https://cdn.jsdelivr.net/npm/three@0.117.0/examples/fonts/helvetiker_regular.typeface.json';
const FONT_PATH = './assets/charaters/helvetiker_regular.typeface.json';

async function downloadFont() {
  if (fs.existsSync(FONT_PATH)) {
    console.log('字体文件已存在');
    return;
  }
  console.log('下载字体文件...');
  const resp = await fetch(FONT_URL);
  const data = await resp.text();
  fs.writeFileSync(FONT_PATH, data);
  console.log('字体下载完成');
}

function exportOBJ(positions, faces, filePath) {
  const lines = [];
  lines.push('# Generated mesh');
  lines.push(`# vertices: ${positions.length}, faces: ${faces.length}`);
  lines.push('');

  // 顶点
  for (const p of positions) {
    lines.push(`v ${p[0].toFixed(6)} ${p[1].toFixed(6)} ${p[2].toFixed(6)}`);
  }

  // 面 (OBJ 索引从 1 开始)
  for (const f of faces) {
    lines.push(`f ${f[0] + 1} ${f[1] + 1} ${f[2] + 1}`);
  }

  fs.writeFileSync(filePath, lines.join('\n'), 'utf-8');
}

// 注册 FontLoader 所需的自定义 JSON loader
// 直接读取 JSON 并构造 Font 对象
function loadFontData(filePath) {
  const raw = fs.readFileSync(filePath, 'utf-8');
  return JSON.parse(raw);
}

// 手动创建 Font 对象
function createFont(typefaceData) {
  return new Font(typefaceData);
}

async function main() {
  await downloadFont();

  const typefaceData = loadFontData(FONT_PATH);
  const font = createFont(typefaceData);

  const outDir = './assets/charaters';
  if (!fs.existsSync(outDir)) fs.mkdirSync(outDir, { recursive: true });

  const letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('');

  for (const letter of letters) {
    console.log(`生成字母: ${letter}...`);

    // 3D 挤出字母
    const geom3d = new TextGeometry(letter, {
      font: font,
      size: 1.0,
      height: 0.2,
      curveSegments: 4,
      bevelEnabled: true,
      bevelThickness: 0.03,
      bevelSize: 0.02,
      bevelSegments: 3
    });
    geom3d.center();

    // 提取位置和面
    const posAttr = geom3d.attributes.position;
    const idx = geom3d.index;
    const positions = [];
    for (let i = 0; i < posAttr.count; i++) {
      positions.push([posAttr.getX(i), posAttr.getY(i), posAttr.getZ(i)]);
    }
    const faces = [];
    if (idx) {
      for (let i = 0; i < idx.count; i += 3) {
        faces.push([idx.getX(i), idx.getX(i + 1), idx.getX(i + 2)]);
      }
    }

    exportOBJ(positions, faces, path.join(outDir, `${letter}.obj`));

    // 2D 平面字母
    const shapes = font.generateShapes(letter, 1.0);
    if (shapes && shapes.length > 0) {
      const allPos = [];
      const allFaces = [];
      let vertOffset = 0;

      for (const shape of shapes) {
        const sg = new THREE.ShapeGeometry(shape, 16);
        const sp = sg.attributes.position;
        const si = sg.index;
        for (let i = 0; i < sp.count; i++) {
          allPos.push([sp.getX(i), sp.getY(i), 0]);
        }
        if (si) {
          for (let i = 0; i < si.count; i += 3) {
            allFaces.push([
              si.getX(i) + vertOffset,
              si.getX(i + 1) + vertOffset,
              si.getX(i + 2) + vertOffset
            ]);
          }
        }
        vertOffset += sp.count;
        sg.dispose();
      }

      // 居中
      if (allPos.length > 0) {
        let cx = 0, cy = 0;
        for (const p of allPos) { cx += p[0]; cy += p[1]; }
        cx /= allPos.length; cy /= allPos.length;
        for (const p of allPos) { p[0] -= cx; p[1] -= cy; }

        exportOBJ(allPos, allFaces, path.join(outDir, `${letter}_2d.obj`));
      }
    }

    geom3d.dispose();
  }

  console.log(`\n完成！所有字母已保存到 ${outDir}/`);
  console.log(`3D: A.obj ... Z.obj`);
  console.log(`2D: A_2d.obj ... Z_2d.obj`);
}

main().catch(err => {
  console.error('错误:', err);
  process.exit(1);
});
