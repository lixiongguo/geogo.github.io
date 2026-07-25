# frozen_string_literal: true

# 公网构建 (JEKYLL_ENV=production) 时，将 `_posts/2.Machine Learning` 下文章正文
# 替换为「尚未完整」，避免未完成内容对外公开。本地 jekyll serve 默认 development，不受影响。
# 开放时在 _config.yml 设 ml_posts.public: true 即可。
#
# 在 :site, :post_read 阶段替换，确保页面、feed、微信导出等后续步骤都只看到占位正文。

module Jekyll
  module MlPostsGate
    module_function

    def production?
      ENV.fetch('JEKYLL_ENV', 'development') == 'production'
    end

    def public?(site)
      site.config.dig('ml_posts', 'public') == true
    end

    def ml_post?(post)
      path = post.relative_path.to_s
      # `_posts/1.Parameterization` 始终对外全文开放，绝不拦截
      return false if path.include?('1.Parameterization')

      path.include?('2.Machine Learning')
    end

    def apply!(site)
      return if public?(site)
      return unless production?

      gated = 0
      site.posts.docs.each do |post|
        next unless ml_post?(post)

        post.content = "尚未完整\n"
        post.data['excerpt'] = '尚未完整'
        gated += 1
        Jekyll.logger.info 'MlPostsGate:', "Gated: #{post.relative_path}"
      end
      Jekyll.logger.info 'MlPostsGate:', "Gated #{gated} ML post(s)" if gated.positive?
    end
  end
end

Jekyll::Hooks.register :site, :post_read do |site|
  Jekyll::MlPostsGate.apply!(site)
end
