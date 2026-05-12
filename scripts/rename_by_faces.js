/**
 * rename_by_faces.js — 统计 OBJ 面数，重命名为 Name_F<faces>.obj，按面数排序
 * 用法: node scripts/rename_by_faces.js <directory...>
 */
const fs = require('fs');
const path = require('path');

function countFaces(filepath) {
  const content = fs.readFileSync(filepath, 'utf-8');
  let count = 0;
  for (const line of content.split(/\r?\n/)) {
    if (/^f\s/.test(line.trim())) count++;
  }
  return count;
}

function processDir(dir) {
  if (!fs.existsSync(dir)) { console.log(`  [跳过] 不存在: ${dir}`); return { dir, files: [] }; }
  const entries = fs.readdirSync(dir, { withFileTypes: true })
    .filter(e => e.isFile() && e.name.endsWith('.obj'))
    .map(e => ({
      name: e.name,
      path: path.join(dir, e.name),
      faces: countFaces(path.join(dir, e.name))
    }))
    .sort((a, b) => a.faces - b.faces);

  console.log(`\n=== ${dir} (${entries.length} 个模型) ===`);
  const padNum = String(entries.length).length;
  const padFaces = String(Math.max(...entries.map(e => e.faces), 1)).length;

  const renamed = [];
  for (let i = 0; i < entries.length; i++) {
    const e = entries[i];
    const base = e.name.replace(/\.obj$/i, '');
    // 移除已有的 _Fxxxxx 后缀避免重复
    const clean = base.replace(/_F\d+$/i, '');
    const newName = `${clean}_F${e.faces}.obj`;
    const newPath = path.join(dir, newName);

    const idx = String(i + 1).padStart(padNum);
    const facesStr = String(e.faces).padStart(padFaces);

    if (e.name !== newName) {
      fs.renameSync(e.path, newPath);
      console.log(`  ${idx}. ${newName}  (${facesStr} faces) ← ${e.name}`);
    } else {
      console.log(`  ${idx}. ${e.name}  (${facesStr} faces) [已命名]`);
    }
    renamed.push({ name: newName, faces: e.faces });
  }
  return { dir, files: renamed };
}

function main() {
  const args = process.argv.slice(2);
  if (args.length === 0) {
    console.log('用法: node scripts/rename_by_faces.js <目录...>');
    process.exit(1);
  }

  const results = [];
  for (const arg of args) results.push(processDir(arg));

  // 汇总
  console.log('\n=== 汇总（按面数） ===');
  const all = results.flatMap(r => r.files.map(f => ({ ...f, dir: r.dir })));
  all.sort((a, b) => a.faces - b.faces);
  const padF = String(Math.max(...all.map(f => f.faces), 1)).length;
  for (const f of all) {
    console.log(`  ${String(f.faces).padStart(padF)} faces  ${path.basename(f.dir)}/${f.name}`);
  }
  console.log(`\n共 ${all.length} 个模型，已完成重命名。`);
}

main();
