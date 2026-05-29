# 阿里云OSS配置信息

## OSS基本信息
- **存储空间(Bucket)名称**: lgximgs
- **地域节点**: oss-cn-beijing (阿里云北京区域)
- **访问域名**: https://lgximgs.oss-cn-beijing.aliyuncs.com

## 使用说明
- 该OSS主要用于存储博客网站中的图片资源
- 访问方式为HTTPS，保证数据传输安全
- 图片资源路径格式：https://lgximgs.oss-cn-beijing.aliyuncs.com/images/[filename]

## 当前使用情况
- 多个Markdown文档中引用了该OSS的图片资源
- 主要用于存放数学理论、参数化等相关文章的插图
- 路径结构为：images/ 下的各种图片文件

## 注意事项
- 请妥善保管OSS的访问密钥，避免泄露
- 定期检查OSS中的文件，确保资源可用性
- 如需迁移或更改OSS配置，需要同步更新所有引用该OSS的文档
