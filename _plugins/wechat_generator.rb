# frozen_string_literal: true

# WechatGenerator - Jekyll 插件
# 在构建时自动生成微信公众号兼容的 HTML 版本
# 功能：
#   1. 将本地图片路径替换为阿里云 OSS URL
#   2. 将 MathJax 公式转换为图片 (CodeCogs API)
#   3. 生成内联样式的微信兼容 HTML
#
# 使用方法：
#   1. 在 _config.yml 中配置 wechat 段
#   2. 执行 jekyll build 或 jekyll serve
#   3. 微信版本输出到 _site/wechat/ 目录

require 'uri'
require 'cgi'

# 可选依赖：nokogiri（用于更精确的 HTML 处理）
begin
  require 'nokogiri'
  NOKOGIRI_AVAILABLE = true
rescue LoadError
  NOKOGIRI_AVAILABLE = false
end

module Jekyll
  class WechatGenerator < Generator
    safe true
    priority :low

    # 代码块占位符计数器
    @@code_placeholder_counter = 0

    def generate(site)
      config = site.config['wechat']
      return unless config && config['enabled']

      @oss_base_url = config.dig('oss', 'base_url') || ''
      @output_dir = config['output_dir'] || 'wechat'
      @mathjax_enabled = config.dig('mathjax', 'enabled') != false
      @style_config = config['style'] || {}
      @formula_cache = {}

      if NOKOGIRI_AVAILABLE
        Jekyll.logger.info 'WechatGenerator:', '使用 Nokogiri 进行 HTML 处理'
      else
        Jekyll.logger.warn 'WechatGenerator:', 'Nokogiri 未安装，使用正则模式（建议: gem install nokogiri）'
      end

      Jekyll.logger.info 'WechatGenerator:', '开始生成微信公众号版本...'

      site.posts.docs.each_with_index do |post, index|
        begin
          generate_wechat_version(site, post)
          Jekyll.logger.info "  [#{index + 1}/#{site.posts.docs.size}]", post.data['slug'] || post.slug
        rescue StandardError => e
          Jekyll.logger.warn "WechatGenerator:", "处理文章 #{post.data['title']} 失败: #{e.message}"
        end
      end

      Jekyll.logger.info 'WechatGenerator:', "微信公众号版本生成完成！输出目录: #{@output_dir}/"
    end

    private

    # ============================================
    # 主处理流程
    # ============================================

    def generate_wechat_version(site, post)
      content = post.content.dup

      # 步骤0: 保护代码块，防止其中的 $ 被误转为公式
      content, code_blocks = protect_code_blocks(content)

      # 步骤1: 替换图片路径
      content = replace_image_paths(content)

      # 步骤2: 转换 MathJax 公式（此时代码块已被保护）
      content = convert_mathjax(content) if @mathjax_enabled

      # 步骤3: 恢复代码块
      content = restore_code_blocks(content, code_blocks)

      # 步骤4: 使用 kramdown 渲染为 HTML
      html = render_to_html(content, site)

      # 步骤5: 后处理 HTML - 内联样式、清理标签
      html = post_process_html(html)

      # 步骤6: 包装完整页面
      full_html = wrap_with_template(post, html)

      # 步骤7: 写入文件
      write_output_file(site, post, full_html)
    end

    # ============================================
    # 代码块保护模块（防止 $ 被误转公式）
    # ============================================

    def protect_code_blocks(content)
      code_blocks = {}
      placeholder_prefix = "\x00CODE_BLOCK_"

      # 保护围栏代码块 ``` ... ```
      content = content.gsub(/```[\w]*\n.*?```/m) do |match|
        key = "#{placeholder_prefix}#{@@code_placeholder_counter}\x00"
        code_blocks[key] = match
        @@code_placeholder_counter += 1
        key
      end

      # 保护行内代码 `...`
      content = content.gsub(/`[^`\n]+`/) do |match|
        key = "#{placeholder_prefix}#{@@code_placeholder_counter}\x00"
        code_blocks[key] = match
        @@code_placeholder_counter += 1
        key
      end

      [content, code_blocks]
    end

    def restore_code_blocks(content, code_blocks)
      code_blocks.each { |placeholder, original| content = content.gsub(placeholder, original) }
      content
    end

    # ============================================
    # 图片路径替换模块
    # ============================================

    def replace_image_paths(content)
      # 匹配所有 Markdown 图片语法，包括缺少 alt 文本的情况
      content.gsub(/!\[([^\]]*)\]\(([^)]+)\)/) do |_match|
        alt_text = Regexp.last_match[1]
        path = Regexp.last_match[2]
        new_path = process_image_path(path)
        "![#{alt_text}](#{new_path})"
      end
    end

    def process_image_path(path)
      return path if path.start_with?('http://', 'https://')

      filename = File.basename(path).gsub('\\', '/') # 统一路径分隔符
      return path if filename.empty?

      ext = File.extname(filename).downcase
      valid_extensions = %w[.jpg .jpeg .png .gif .svg .webp .bmp]
      return path unless valid_extensions.include?(ext)

      # URL 编码中文等特殊字符
      safe_filename = CGI.escape(filename).gsub('+', '%20')

      "#{@oss_base_url}/#{safe_filename}"
    end

    # ============================================
    # MathJax 公式转换模块
    # ============================================

    def convert_mathjax(content)
      # 先处理块级公式 $$...$$（必须在行内之前）
      content = convert_block_math(content)
      # 再处理行内公式 $...$
      convert_inline_math(content)
    end

    def convert_block_math(content)
      content.gsub(/\$\$(.*?)\$\$/m) do |_match|
        formula = Regexp.last_match[1].strip
        next Regexp.last_match[0] if formula.empty?

        img_url = get_formula_image_url(formula, false)
        "\n\n![formula](#{img_url})\n\n"
      end
    end

    def convert_inline_math(content)
      result = ''
      pos = 0

      while pos < content.length
        dollar_pos = content.index('$', pos)
        unless dollar_pos
          result += content[pos..]
          break
        end

        # 块级公式 $$ 开头 — 跳过整个块级公式
        if dollar_pos + 1 < content.length && content[dollar_pos + 1] == '$'
          end_pos = content.index('$$', dollar_pos + 2)
          if end_pos
            result += content[dollar_pos..end_pos + 1]
            pos = end_pos + 2
          else
            result += content[dollar_pos..]
            break
          end
          next
        end

        # 行内公式：查找配对的结束 $
        end_dollar_pos = find_matching_dollar(content, dollar_pos + 1)

        if end_dollar_pos
          formula = content[(dollar_pos + 1)...end_dollar_pos].strip
          if formula.empty?
            result += '$'
            pos = dollar_pos + 1
          else
            img_url = get_formula_image_url(formula, true)
            # 行内公式使用 <img> 标签，设置 display:inline 使其与文字同行
            result += "<img src=\"#{img_url}\" alt=\"formula\" style=\"display:inline;vertical-align:middle;margin:0 2px;height:1.2em;\" />"
            pos = end_dollar_pos + 1
          end
        else
          result += content[dollar_pos]
          pos = dollar_pos + 1
        end
      end

      result
    end

    def find_matching_dollar(content, start_pos)
      search_pos = start_pos
      while search_pos < content.length
        idx = content.index('$', search_pos)
        return nil unless idx

        # 排除 $$ 的情况
        next_idx = idx + 1
        if next_idx < content.length && content[next_idx] == '$'
          search_pos = next_idx + 2
          next
        else
          return idx
        end
      end
      nil
    end

    def get_formula_image_url(formula, inline)
      cache_key = "#{inline ? 'inline' : 'block'}:#{formula}"
      return @formula_cache[cache_key] if @formula_cache.key?(cache_key)

      encoded = CGI.escapeURIComponent(formula)
      size_prefix = inline ? '\\small%20' : ''
      url = "https://latex.codecogs.com/svg.image?#{size_prefix}#{encoded}"

      @formula_cache[cache_key] = url
      url
    end

    # ============================================
    # HTML 渲染模块
    # ============================================

    def render_to_html(markdown_content, site)
      return '' if markdown_content.nil? || markdown_content.empty?

      converter = site.converters.find { |c| c.instance_of?(Jekyll::Converters::Markdown) }
      if converter
        converter.convert(markdown_content)
      else
        require 'kramdown'
        Kramdown::Document.new(markdown_content).to_html
      end
    rescue StandardError => e
      Jekyll.logger.warn 'WechatRenderer:', "HTML 渲染失败: #{e.message}"
      "<p>渲染错误: #{e.message}</p>"
    end

    # ============================================
    # HTML 后处理模块
    # ============================================

    def post_process_html(html)
      if NOKOGIRI_AVAILABLE
        post_process_with_nokogiri(html)
      else
        post_process_with_regex(html)
      end
    end

    # --- Nokogiri 模式 ---

    def post_process_with_nokogiri(html)
      doc = Nokogiri::HTML::DocumentFragment.parse(html)
      apply_nokogiri_styles(doc)
      remove_unsupported_tags(doc)
      doc.to_html(save_with: Nokogiri::XML::Node::SaveOptions::NO_DECLARATION)
    end

    def apply_nokogiri_styles(doc)
      ff = style_value('font_family')
      fs = style_value('font_size')
      lh = style_value('line_height')
      tc = style_value('text_color')

      styles_map = {
        'body' => "font-family: #{ff}; font-size: #{fs}; line-height: #{lh}; color: #{tc}; padding: 10px; margin: 0;",
        'p' => 'margin: 16px 0; text-align: justify;',
        'h1' => 'font-size: 22px; font-weight: bold; margin: 24px 0 16px; color: #222; border-bottom: 2px solid #eee; padding-bottom: 8px;',
        'h2' => 'font-size: 20px; font-weight: bold; margin: 20px 0 14px; color: #333;',
        'h3' => 'font-size: 18px; font-weight: bold; margin: 18px 0 12px; color: #444;',
        'h4' => 'font-size: 16px; font-weight: bold; margin: 16px 0 10px; color: #555;',
        'ul' => 'margin: 12px 0; padding-left: 24px; list-style-type: disc;',
        'ol' => 'margin: 12px 0; padding-left: 24px; list-style-type: decimal;',
        'li' => "margin: 6px 0; line-height: #{lh};",
        'blockquote' => 'border-left: 4px solid #ddd; margin: 16px 0; padding: 8px 16px; background-color: #f9f9f9; color: #666;',
        'pre' => 'background-color: #f6f8fa; padding: 16px; overflow-x: auto; border-radius: 6px; margin: 16px 0; font-size: 14px; line-height: 1.6;',
        'code' => "font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace; background-color: #f0f0f0; padding: 2px 6px; border-radius: 3px; font-size: 14px;",
        'a' => 'color: #007acc; text-decoration: none;',
        'table' => 'width: 100%; border-collapse: collapse; margin: 16px 0; font-size: 14px;',
        'th' => 'background-color: #f2f2f2; padding: 10px; border: 1px solid #ddd; text-align: left;',
        'td' => 'padding: 10px; border: 1px solid #ddd;',
        'hr' => 'border: none; border-top: 1px solid #eee; margin: 24px 0;',
        'strong' => 'font-weight: bold;',
        'em' => 'font-style: italic;'
      }

      styles_map.each { |tag, styles| style_element(doc, tag, styles) }

      # 图片样式（区分公式图片和普通图片）
      doc.css('img').each do |el|
        alt = el['alt'] || ''
        if alt == 'formula'
          el['style'] = 'display:inline; vertical-align:middle; margin:0 2px; max-width:none; height:1.2em;'
        else
          existing = el['style'] || ''
          el['style'] = "#{existing.empty? ? '' : existing;}max-width:100%;height:auto;display:block;margin:16px auto;border-radius:4px;"
        end
      end

      # 代码块内的 code 不加背景
      doc.css('pre code').each { |el| el['style'] = 'background-color: transparent; padding: 0; font-size: inherit;' }
    end

    def style_element(doc, tag, styles)
      doc.css(tag).each do |element|
        existing = element['style'] || ''
        element['style'] = existing.empty? ? styles : "#{existing}; #{styles}"
      end
    end

    def remove_unsupported_tags(doc)
      doc.css('script, link, meta').each(&:remove)
    end

    # --- 正则模式（无 Nokogiri 时使用）---

    def post_process_with_regex(html)
      html = html.gsub(/<script[^>]*>.*?<\/script>/mi, '')
                  .gsub(/<link[^>]*>/i, '')
                  .gsub(/<meta[^>]*>/i, '')

      ff = style_value('font_family')
      fs = style_value('font_size')
      lh = style_value('line_height')
      tc = style_value('text_color')
      base_style = "font-family:#{ff};font-size:#{fs};line-height:#{lh};color:#{tc};"

      html = "<div style=\"#{base_style}\">#{html}</div>" unless html.include?('<body')

      html
    end

    def style_value(key)
      @style_config[key] || {
        'font_family' => "-apple-system, BlinkMacSystemFont, 'PingFang SC', 'Microsoft YaHei', sans-serif",
        'font_size' => '16px',
        'line_height' => '1.8',
        'text_color' => '#333333'
      }[key]
    end

    # ============================================
    # 页面模板包装
    # ============================================

    def wrap_with_template(post, body_html)
      title = post.data['title'] || '无标题'
      date = post.date.strftime('%Y年%m月%d日')
      categories = post.data['categories'] || []
      cat_tags = categories.map { |c| "##{c}" }.join(' ')

      <<~HTML
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
          <meta charset="UTF-8">
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
          <title>#{CGI.escapeHTML(title)}</title>
        </head>
        <body>
          <header style="text-align:center;margin-bottom:30px;padding-bottom:20px;border-bottom:1px solid #eee;">
            <h1 style="margin:0;font-size:24px;color:#333;">#{CGI.escapeHTML(title)}</h1>
            <p style="margin:10px 0 0;color:#888;font-size:14px;">#{date} #{cat_tags}</p>
          </header>
          <article>#{body_html}</article>
          <footer style="margin-top:40px;padding-top:20px;border-top:1px solid #eee;text-align:center;color:#999;font-size:12px;">
            <p>本文由 Jekyll WechatGenerator 自动生成</p>
            <p>请复制上方内容到微信公众号编辑器发布</p>
          </footer>
        </body>
        </html>
      HTML
    end

    # ============================================
    # 文件输出模块
    # ============================================

    def write_output_file(_site, post, content)
      slug = post.data['slug'] || post.slug
      output_path = File.join(@output_dir, "#{slug}.html")

      dir = File.dirname(output_path)
      FileUtils.mkdir_p(dir) unless Dir.exist?(dir)

      File.write(output_path, content)
    end
  end
end
