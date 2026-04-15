# Monkey-patch Jekyll 4.4.1 static_file.rb to fix CJK path encoding bug
# https://github.com/jekyll/jekyll/issues/9263
module Jekyll
  class StaticFile
    def destination_rel_dir
      @destination_rel_dir ||= @relative_dir.dup.force_encoding(Encoding::UTF_8)
    end
  end
end
