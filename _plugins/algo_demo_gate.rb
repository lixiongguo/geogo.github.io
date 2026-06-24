# frozen_string_literal: true

# 公网构建 (JEKYLL_ENV=production) 时，移除 ready: false 的算法 Demo 页面，
# 使直接访问 URL 返回 404。本地 jekyll serve 默认 development，不受影响。

module Jekyll
  module AlgoDemoGate
    module_function

    def production?
      ENV.fetch('JEKYLL_ENV', 'development') == 'production'
    end

    def gate!(site)
      return unless production?

      demos = site.data['algo_demos']
      return unless demos.is_a?(Array)

      removed = 0
      demos.each do |demo|
        next if demo['ready']

        rel = demo['url'].to_s.sub(%r{\A/}, '')
        next if rel.empty?

        path = File.join(site.dest, rel)
        next unless File.file?(path)

        File.delete(path)
        removed += 1
        Jekyll.logger.info 'AlgoDemoGate:', "Removed (not ready): #{rel}"
      end

      Jekyll.logger.info 'AlgoDemoGate:', "Gated #{removed} demo page(s)" if removed.positive?
    end
  end
end

Jekyll::Hooks.register :site, :post_write do |site|
  Jekyll::AlgoDemoGate.gate!(site)
end
