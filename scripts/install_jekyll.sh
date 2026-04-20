#!/bin/bash
# Jekyll 安装脚本 - 适配 Ruby 2.6

cd /Users/lgxgeogo/Desktop/MyDoc/lixiongguo.github.io

# 清除有问题的环境变量
unset RUBYOPT

# 添加本地 gem 到 PATH
export PATH="$HOME/.gem/ruby/2.6.0/bin:$PATH"

echo "Installing compatible gems for Ruby 2.6..."

# 安装兼容版本的 gem
gem install --user-install ffi -v 1.15.5
gem install --user-install sassc -v 2.4.0
gem install --user-install jekyll -v 4.2.2

echo "Installing bundler..."
gem install --user-install bundler -v 2.4.22

echo "Installing project dependencies..."
bundle install

echo "Done! You can now run: bundle exec jekyll serve"
