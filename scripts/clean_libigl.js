const fs = require('fs'), path = require('path');
const base = 'c:/Users/lixio/OneDrive/Desktop/MyDoc/lixiongguo.github.io/cpp/deps/Libigl-Discrete-Geometry/libigl/include/igl';

// Directories to remove (rendering/IO/external)
const rmDirs = ['opengl', 'png', 'xml', 'copyleft', 'embree', 'triangle'];
for (const d of rmDirs) {
  const p = path.join(base, d);
  if (fs.existsSync(p)) { fs.rmSync(p, { recursive: true, force: true }); console.log('rm dir: ' + d); }
}

// Files to remove
const rmFiles = [
  // Viewer / GL / display
  'Viewport.h', 'viewer', 'gl_', 'glut_', 'trackball', 'colormap',
  'two_axis_valuator_fixed_up', 'opengl',
  // Colormap stuff
  'jet', 'turbo', 'parula', 'inferno', 'magma', 'plasma', 'viridis',
  'falsecolor', 'isolines', 'n_polyvector',
  // GLTF / WRL
  'readWRL', 'writeWRL', 'writeGLTF', 'readGLTF',
  // Web/online
  'report_gl_error',
];
let count = 0;
for (const f of fs.readdirSync(base)) {
  for (const pat of rmFiles) {
    if (f === pat + '.cpp' || f === pat + '.h' || f === pat + '.hpp' || f === pat) {
      try { fs.rmSync(path.join(base, f)); console.log('rm: ' + f); count++; } catch (e) {}
      break;
    }
    // Also match prefixes (like gl_*.h)
    if (f.startsWith(pat) && (f.endsWith('.h') || f.endsWith('.cpp'))) {
      try { fs.rmSync(path.join(base, f)); console.log('rm: ' + f); count++; } catch (e) {}
      break;
    }
  }
}
console.log('\nRemoved ' + rmDirs.length + ' dirs + ' + count + ' files');
console.log('Remaining: ' + fs.readdirSync(base).length + ' entries');
