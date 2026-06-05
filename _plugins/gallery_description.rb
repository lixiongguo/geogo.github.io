module Jekyll
  module GalleryDescription
    def gallery_description(title)
      file_path = File.join(@context.registers[:site].source, 'gallery', 'ThumbNails', "#{title}.md")
      if File.exist?(file_path)
        File.read(file_path, encoding: 'UTF-8').strip
      else
        ''
      end
    end
  end
end

Liquid::Template.register_filter(Jekyll::GalleryDescription)
