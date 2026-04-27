import sharp from 'sharp';
import { renameSync, unlinkSync } from 'fs';
import { join, dirname } from 'path';

const imgsDir = 'c:/Users/lixio/OneDrive/Desktop/MyDoc/lixiongguo.github.io/imgs/';

const images = [
  {
    file: 'image-20251107104253558.png',   // 变分法求半径 - Figure 7 文字
  },
  {
    file: 'image-20251107105336742.png',   // 边界条件公式 - Figure 9 文字
  },
];

for (const img of images) {
  const src = imgsDir + img.file;
  try {
    const meta = await sharp(src).metadata();
    console.log(`${img.file}: ${meta.width}x${meta.height}`);

    const cropBottom = Math.round(meta.height * 0.18);
    const newHeight = meta.height - cropBottom;
    const tmpFile = src + '.tmp';

    await sharp(src)
      .extract({ left: 0, top: 0, width: meta.width, height: newHeight })
      .toFile(tmpFile);

    // 用裁剪后的文件替换原文件
    renameSync(tmpFile, src);
    console.log(`  -> OK: 底部裁去 ${cropBottom}px, 新尺寸 ${meta.width}x${newHeight}`);
  } catch (e) {
    console.error(`  错误: ${e.message}`);
  }
}

console.log('\nDone!');
