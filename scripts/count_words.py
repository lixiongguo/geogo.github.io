import os
import re
import glob

def count_words_in_markdown(file_path):
    """统计Markdown文件中的字数"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 移除YAML front matter（---之间的内容）
        content = re.sub(r'^---\n.*?\n---\n', '', content, flags=re.DOTALL)
        
        # 移除代码块（```之间的内容）
        content = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
        
        # 移除行内代码
        content = re.sub(r'`[^`]*`', '', content)
        
        # 移除图片链接
        content = re.sub(r'!\[.*?\]\(.*?\)', '', content)
        
        # 移除普通链接
        content = re.sub(r'\[.*?\]\(.*?\)', '', content)
        
        # 移除HTML标签
        content = re.sub(r'<.*?>', '', content)
        
        # 移除特殊字符和标点，只保留中英文字符和空格
        content = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\s]', '', content)
        
        # 统计中文字符数（每个中文字符算1个字）
        chinese_chars = len(re.findall(r'[\u4e00-\u9fa5]', content))
        
        # 统计英文单词数（按空格分割）
        english_words = len(re.findall(r'[a-zA-Z]+', content))
        
        # 总字数 = 中文字符数 + 英文单词数
        total_words = chinese_chars + english_words
        
        return total_words, chinese_chars, english_words
        
    except Exception as e:
        print(f"读取文件 {file_path} 时出错: {e}")
        return 0, 0, 0

def main():
    base_dir = r'd:\MyDocs\geogo.github.io'
    posts_dir = os.path.join(base_dir, '_posts')
    
    if not os.path.exists(posts_dir):
        print(f"文章目录不存在: {posts_dir}")
        return
    
    # 查找所有markdown文件
    md_files = []
    for root, dirs, files in os.walk(posts_dir):
        for file in files:
            if file.endswith('.md'):
                md_files.append(os.path.join(root, file))
    
    print(f"找到 {len(md_files)} 个Markdown文件")
    
    total_words = 0
    total_chinese = 0
    total_english = 0
    file_stats = []
    
    for file_path in md_files:
        words, chinese, english = count_words_in_markdown(file_path)
        total_words += words
        total_chinese += chinese
        total_english += english
        
        file_stats.append({
            'file': os.path.relpath(file_path, base_dir),
            'words': words,
            'chinese': chinese,
            'english': english
        })
    
    # 按字数排序
    file_stats.sort(key=lambda x: x['words'], reverse=True)
    
    print(f"\n=== 统计结果 ===")
    print(f"总文章数: {len(md_files)}")
    print(f"总字数: {total_words:,}")
    print(f"中文字符数: {total_chinese:,}")
    print(f"英文单词数: {total_english:,}")
    
    print(f"\n=== 文章字数排行（前10）===")
    for i, stat in enumerate(file_stats[:10], 1):
        print(f"{i:2d}. {stat['file']} - {stat['words']:,}字")
    
    print(f"\n=== 分类统计 ===")
    # 按目录分类统计
    category_stats = {}
    for stat in file_stats:
        category = os.path.dirname(stat['file']).replace('_posts\\', '')
        if category not in category_stats:
            category_stats[category] = {'count': 0, 'words': 0}
        category_stats[category]['count'] += 1
        category_stats[category]['words'] += stat['words']
    
    for category, stats in sorted(category_stats.items(), key=lambda x: x[1]['words'], reverse=True):
        print(f"{category}: {stats['count']}篇文章, {stats['words']:,}字")

if __name__ == "__main__":
    main()