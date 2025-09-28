import os
import shutil

# 定义源目录和目标目录
source_dir = r"d:\MyDocs\geogo.github.io\_posts"
target_dir = r"d:\MyDocs\geogo.github.io\_drafts"

# 确保目标目录存在
os.makedirs(target_dir, exist_ok=True)

# 递归查找所有.txt文件并移动到_drafts目录
txt_files = []
for root, dirs, files in os.walk(source_dir):
    for file in files:
        if file.endswith(".txt"):
            source_path = os.path.join(root, file)
            txt_files.append(source_path)

# 移动.txt文件到_drafts目录
for txt_file in txt_files:
    # 获取相对路径
    relative_path = os.path.relpath(txt_file, source_dir)
    target_path = os.path.join(target_dir, relative_path)
    
    # 确保目标目录存在
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    
    # 移动文件
    shutil.move(txt_file, target_path)
    print(f"Moved: {txt_file} -> {target_path}")

# 重命名_drafts目录下的所有.txt文件为.md文件
for root, dirs, files in os.walk(target_dir):
    for file in files:
        if file.endswith(".txt"):
            txt_path = os.path.join(root, file)
            base_name = os.path.splitext(txt_path)[0]
            md_path = base_name + ".md"
            
            # 重命名文件
            os.rename(txt_path, md_path)
            print(f"Renamed: {txt_path} -> {md_path}")

print("All operations completed!")