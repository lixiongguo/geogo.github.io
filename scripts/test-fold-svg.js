/**
 * Quick sanity check for Origami Simulator SVG stroke colors.
 * Run: node scripts/test-fold-svg.js
 */
const fs = require('fs');
const path = require('path');

const sample = `<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100">
<rect width="100" height="100" fill="#ffffff"/>
<g>
  <path stroke="#000000" stroke-width="1" fill="none" d="M10,10L90,10"/>
  <path stroke="#0000ff" stroke-width="1" fill="none" d="M10,50L90,50"/>
  <path stroke="#ff0000" stroke-width="1" fill="none" d="M10,90L90,90"/>
</g>
</svg>`;

function typeForStroke(stroke) {
  stroke = stroke.replace(/\s/g, '').toLowerCase();
  if (stroke === '#000000' || stroke === '#000' || stroke === 'black' || stroke === 'rgb(0,0,0)') return 'border';
  if (stroke === '#ff0000' || stroke === '#f00' || stroke === 'red' || stroke === 'rgb(255,0,0)') return 'mountain';
  if (stroke === '#0000ff' || stroke === '#00f' || stroke === 'blue' || stroke === 'rgb(0,0,255)') return 'valley';
  return null;
}

const strokes = [...sample.matchAll(/stroke="([^"]+)"/g)].map(m => m[1]);
const types = strokes.map(typeForStroke);

if (types.join(',') !== 'border,valley,mountain') {
  console.error('FAIL: unexpected stroke classification', types);
  process.exit(1);
}

const bridgePath = path.join(__dirname, '../origami-simulator/js/uvUnwrapBridge.js');
const mainPath = path.join(__dirname, '../origami-simulator/js/main.js');
const indexPath = path.join(__dirname, '../origami-simulator/index.html');

for (const p of [bridgePath, mainPath, indexPath]) {
  if (!fs.existsSync(p)) {
    console.error('FAIL: missing', p);
    process.exit(1);
  }
}

if (!fs.readFileSync(indexPath, 'utf8').includes('uvUnwrapBridge.js')) {
  console.error('FAIL: index.html does not include uvUnwrapBridge.js');
  process.exit(1);
}

if (!fs.readFileSync(mainPath, 'utf8').includes('autoload=')) {
  console.error('FAIL: main.js autoload skip not patched');
  process.exit(1);
}

const uvHtml = fs.readFileSync(path.join(__dirname, '../uv-unwrap.html'), 'utf8');
if (!uvHtml.includes('function buildFoldSVG()') || !uvHtml.includes('stroke="#ff0000"')) {
  console.error('FAIL: uv-unwrap.html missing buildFoldSVG or correct colors');
  process.exit(1);
}

// Synthetic open mesh: two triangles sharing edge 0-1 (internal), boundary edges 0-2, 1-2, 2-3, 1-3
function buildMeshEdgeSetsTriangle(faces) {
  const intEdgeSet = new Set();
  const bndEdgeSet = new Set();
  function addEdge(a, b) {
    const key = Math.min(a, b) + '_' + Math.max(a, b);
    if (intEdgeSet.has(key)) intEdgeSet.delete(key);
    else if (bndEdgeSet.has(key)) { bndEdgeSet.delete(key); intEdgeSet.add(key); }
    else bndEdgeSet.add(key);
  }
  for (const f of faces) {
    addEdge(f[0], f[1]);
    addEdge(f[1], f[2]);
    addEdge(f[2], f[0]);
  }
  return { intEdgeSet, bndEdgeSet };
}

const edges = buildMeshEdgeSetsTriangle([[0, 1, 2], [1, 3, 2]]);
if (!edges.intEdgeSet.has('1_2') || edges.intEdgeSet.size !== 1) {
  console.error('FAIL: internal edge detection', [...edges.intEdgeSet]);
  process.exit(1);
}
if (edges.bndEdgeSet.size !== 4) {
  console.error('FAIL: boundary edge count', [...edges.bndEdgeSet]);
  process.exit(1);
}

const bridge = fs.readFileSync(bridgePath, 'utf8');
if (!bridge.includes('uv-fold-svg') || !bridge.includes('uvFoldPatternSvg')) {
  console.error('FAIL: bridge script incomplete');
  process.exit(1);
}

console.log('OK: SVG colors, bridge, edge sets, and integration files present');
