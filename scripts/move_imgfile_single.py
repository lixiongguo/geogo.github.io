import os
import re
import shutil
import sys
import argparse
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

def download_image(url, save_path):
    """下载图片到指定路径"""
    try:
        # 添加请求头以避免被某些网站拒绝
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            with open(save_path, 'wb') as f:
                f.write(response.read())
        return True
    except Exception as e:
        print(f"    下载失败: {url} - {e}")
        return False

def get_filename_from_url(url):
    """从URL中提取文件名"""
    parsed_url = urlparse(url)
    filename = os.path.basename(parsed_url.path)
    
    # 如果没有扩展名，尝试从查询参数中获取
    if not os.path.splitext(filename)[1]:
        # 移除查询参数
        filename = filename.split('?')[0]
        # 根据Content-Type确定扩展名（这里简化处理）
        if 'jpg' in url or 'jpeg' in url:
            filename += '.jpg'
        elif 'png' in url:
            filename += '.png'
        elif 'gif' in url:
            filename += '.gif'
        else:
            filename += '.jpg'  # 默认jpg
    
    return filename

def migrate_images(file_path=None):
    # 定义目录路径
    posts_dir = Path('_posts')
    imgs_dir = Path('imgs')
    
    # 确保imgs目录存在
    imgs_dir.mkdir(exist_ok=True)
    
    # 定义要特殊处理的域名（可选）
    special_domains = [
        'lgximgs.oss-cn-beijing.aliyuncs.com'
    ]
    
    # 收集所有需要处理的Markdown文件
    if file_path:
        # 如果指定了文件，只处理该文件
        target_file = Path(file_path)
        if not target_file.exists():
            print(f"错误: 文件不存在 {file_path}")
            return
        md_files = [target_file]
        print(f"处理指定文件: {file_path}\n")
    else:
        # 否则处理所有markdown文件
        md_files = list(posts_dir.rglob('*.md'))
        print(f"处理所有Markdown文件...\n")
    
    # 统计信息
    total_images_found = 0
    total_local_migrated = 0
    total_web_downloaded = 0
    total_special_ignored = 0
    
    # 处理每个Markdown文件
    for md_file in md_files:
        print(f"处理文件: {md_file}")
        
        # 读取文件内容
        content = md_file.read_text(encoding='utf-8')
        original_content = content
        
        # 查找图片引用 pattern: ![alt](path)
        image_pattern = r'!\[([^\]]*)\]\(([^)]*\.(?:png|jpg|jpeg|gif|bmp|svg))[^\)]*\)'
        matches = re.findall(image_pattern, content)
        
        if matches:
            print(f"  找到 {len(matches)} 个图片引用")
            
            for alt_text, img_path in matches:
                total_images_found += 1
                img_path = img_path.strip()
                
                # 检查是否是网络图片
                if img_path.startswith('http'):
                    # 检查是否是指定的特殊域名
                    is_special = False
                    for domain in special_domains:
                        if domain in img_path:
                            is_special = True
                            total_special_ignored += 1
                            print(f"    忽略特殊域名链接: {img_path}")
                            break
                    
                    # 如果是特殊域名，则跳过处理
                    if is_special:
                        continue
                    
                    # 下载网络图片
                    filename = get_filename_from_url(img_path)
                    # 确保文件名唯一
                    new_img_path = imgs_dir / filename
                    counter = 1
                    while new_img_path.exists():
                        name, ext = os.path.splitext(filename)
                        new_img_path = imgs_dir / f"{name}_{counter}{ext}"
                        counter += 1
                    
                    if download_image(img_path, new_img_path):
                        total_web_downloaded += 1
                        print(f"    已下载: {img_path} -> {new_img_path}")
                        
                        # 更新Markdown文件中的引用路径
                        relative_path = os.path.relpath(new_img_path, md_file.parent)
                        new_ref = f'![{alt_text}]({relative_path})'
                        old_ref = f'![{alt_text}]({img_path})'
                        content = content.replace(old_ref, new_ref)
                        print(f"    已更新引用: {old_ref} -> {new_ref}")
                    else:
                        print(f"    下载失败: {img_path}")
                else:
                    # 处理本地图片文件
                    # 处理相对路径引用
                    if img_path.startswith('../'):
                        # 处理相对于_posts目录的相对路径
                        actual_img_path = (md_file.parent / img_path).resolve()
                    elif img_path.startswith('/'):
                        # 处理绝对路径引用
                        actual_img_path = Path(img_path.lstrip('/'))
                    else:
                        # 处理相对路径引用（相对于当前文件）
                        actual_img_path = (md_file.parent / img_path).resolve()
                    
                    # 检查图片文件是否存在
                    if actual_img_path.exists() and actual_img_path.is_file():
                        # 生成新的图片文件名（保持原文件名）
                        new_img_name = actual_img_path.name
                        new_img_path = imgs_dir / new_img_name
                        
                        # 复制图片到imgs目录
                        try:
                            shutil.copy2(actual_img_path, new_img_path)
                            total_local_migrated += 1
                            print(f"    已复制: {actual_img_path} -> {new_img_path}")
                            
                            # 更新Markdown文件中的引用路径
                            # 新的相对路径应该是相对于_posts目录的imgs目录
                            relative_path = os.path.relpath(new_img_path, md_file.parent)
                            new_ref = f'![{alt_text}]({relative_path})'
                            old_ref = f'![{alt_text}]({img_path})'
                            content = content.replace(old_ref, new_ref)
                            print(f"    已更新引用: {old_ref} -> {new_ref}")
                        except Exception as e:
                            print(f"    复制失败: {actual_img_path} - {e}")
                    else:
                        print(f"    图片文件不存在: {actual_img_path}")
        
        # 如果内容有变化，则写回文件
        if content != original_content:
            try:
                md_file.write_text(content, encoding='utf-8')
                print(f"  已更新文件: {md_file}")
            except Exception as e:
                print(f"  写入文件失败: {md_file} - {e}")
    
    print(f"\n处理完成!")
    print(f"总共找到图片引用: {total_images_found}")
    print(f"成功迁移本地图片: {total_local_migrated}")
    print(f"成功下载网络图片: {total_web_downloaded}")
    print(f"忽略特殊域名链接: {total_special_ignored}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='迁移Markdown文件中的图片到本地imgs目录')
    parser.add_argument('file', nargs='?', default=None, help='指定要处理的Markdown文件路径（可选）')
    
    args = parser.parse_args()
    
    migrate_images(args.file)