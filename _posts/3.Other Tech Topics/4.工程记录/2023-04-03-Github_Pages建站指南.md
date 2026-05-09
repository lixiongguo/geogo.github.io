---
layout: post
title: "Github Pages 建个人网站全程攻略"
categories: [Others, Engineering]
---
## Github Pages 建个人网站全程攻略

#### GitHub Pages

1.建立github.io仓(命名要注意!! 注意是**个人站点还是项目站点**!!，很坑，详见后面解释)

2.settings pages下进行设置

![image-20240911150939286](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20240911150939286.png)

修改后还要注意到需要build

![image-20240911151316835](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20240911151316835.png)

### Jekyll

------

**Jekyll** 是一个静态网站生成器，用于创建个人博客、项目网站或公司主页。它通过将 Markdown 或 HTML 文件转换为静态网页，生成一个完整的网站。

jekyll安装教程 https://blog.csdn.net/qq_33919450/article/details/127859193

先安装ruby https://www.ruby-lang.org/zh_cn/

安装了 Ruby 之后，可以通过 Gem 包管理器安装 Jekyll
gem install jekyll bundler

创建一个新的 Jekyll 站点非常简单：

![image-20240911143228623](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20240911143228623.png)

**jekyll new myblog**之后生成的目录结构

![image-20250306200049709](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20250306200049709.png)

重要的配置文件:_**config.yml** 其中destination:存放用来生成网页的根目录，exerpt_separator摘要分隔符

很重要的，还有用来**解析公式的math_engine** 

![image-20250306200749263](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20250306200749263.png)

**编写内容**： Markdown文件放到**_posts** 目录下。格式要求 `YYYY-MM-DD-文章标题.md`（例如 `2023-10-05-我的博客.md`）。

一般先用**jekyll server** 本地看下，然后再上传部署到git上。

注意文章还要加上 **Matter Front**（**文章抬头**)

![image-20250306203729007](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20250306203729007.png)

**index.md** 首页

**_layouts** 存放布局 。**___include** 存放可重用的HTML片段 他们一般直接用主题提供的就可以了

![image-20250306201002065](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20250306201002065.png)

![image-20250306201312027](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20250306201312027.png)

**_data**存放结构化数据![image-20250306201709498](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20250306201709498.png)

**Gemfile** 定义Ruby依赖，比较重要

![image-20250306201521016](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20250306201521016.png)

**public**放css等(一般用主题自带的)

![image-20250306201830950](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20250306201830950.png)

#### **部署站点**

------

直接提交到 Git 库就可以，部署是自动的，就是这么简单！！

一般不会马上就更新，需要3-5分钟部署。GitHub的**Actions**标签下查看部署进度

![image-20250306202145353](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20250306202145353.png)

## 图床设置

图床用来存放图片等资源的，需要把图片放到云端这样网站页面才能索引到。

用**Aliyun对象存储**就可以


申请Aliyun对象存储的 AccesssKey和ID，如果是新的端需要新创建



Bucket

![image-20240911202551996](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20240911202551996.png)



下载**PicGo** https://picgo.github.io/PicGo-Doc/zh/

PicGO设置

![image-20240911202628238](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20240911202628238.png)

最后**在Typora设置**

![image-20240911203150784](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20240911203150784.png)

Typora上传图片很简单，直接右键选择上传图片就可以。

### 主题

------

实际上主题就是一个基本搞好的静态网站项目，可以在别人基础上做出好看的网页效果。

使用的话就是简单的把文件拷到目录下就可以了。静态网站所以就是这么简单

网上很多主题资源，有jekyll官方的网站，github也有很多免费的，找一个适合自己的

![image-20250306202405122](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20250306202405122.png)

**FAQ**

Q:为什么会有无法自动路由到文件的情况？(后面会自动加上库的名称导致文件无法路由到)

A:因为github pages站点的两种配置类型：1.站点类型 https://lixiongguo.github.io/  2. 项目站点 https://lixiongguo.github.io/ geogo.github.io/

![image-20250306195030026](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20250306195030026.png)

解决方法很简单直接改名字就可以了

![image-20250306195416757](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20250306195416757.png)

---

## 图床配置记录（2025-05-09 更新）

### PicGo-Core 命令行安装

macOS 环境下，Typora 下拉菜单找不到 `PicGo.app` 选项时，可以改用 **PicGo-Core（命令行版）**：

```bash
# 1. 安装 PicGo-Core
npm install -g picgo

# 2. 安装阿里云 OSS 插件
picgo install picgo-plugin-oss

# 3. 配置文件路径
~/.picgo/config.json
```

### 配置文件内容

```json
{
  "picBed": {
    "uploader": "oss",
    "current": "oss",
    "oss": {
      "accessKeyId": "<你的 AccessKey ID>",
      "accessKeySecret": "<你的 Secret>",
      "bucket": "lgximgs",
      "area": "oss-cn-beijing",
      "path": "images/",
      "customUrl": "https://lgximgs.oss-cn-beijing.aliyuncs.com"
    }
  },
  "picgoPlugins": {
    "picgo-plugin-oss": true
  }
}
```

### 遇到的问题

#### 1. AccessKey 签名不匹配

```
The request signature we calculated does not match the signature you provided.
```

**原因**：`AccessKeySecret` 已过期/被重置。

**解决**：登录 [阿里云 RAM 控制台](https://ram.console.aliyun.com/manage/ak) 找到对应 AccessKey，点击「重置 Secret」，获取新密钥后更新配置。

> ⚠️ **安全提醒**：AccessKeySecret 不要明文写在博客或代码中！之前本文第 89-91 行曾明文记录，已打码处理。

#### 2. PicGo-Core 与 Node.js v24 兼容性

Node.js v24 环境下，`picgo` CLI 的交互式命令（如 `picgo set uploader`）会崩溃：

```
Error [ERR_USE_AFTER_CLOSE]: readline was closed
```

**解决**：直接编辑 `~/.picgo/config.json` 配置文件，避免使用交互式命令。

#### 3. PicGo-Core 配置不生效

即使配置文件写了 `"current": "oss"`，上传时仍提示 `Can't find uploader - smms`。

**原因**：PicGo v1.x 在 Node.js v24 下存在配置加载 bug。

**替代方案**：直接用阿里云 `ali-oss` SDK 写上传脚本：

```bash
npm install -g ali-oss
```

创建 `~/.picgo/oss-upload.js`：

```javascript
const OSS = require('ali-oss');
const path = require('path');

const client = new OSS({
  region: 'oss-cn-beijing',
  accessKeyId: '<你的 AccessKey ID>',
  accessKeySecret: '<你的 Secret>',
  bucket: 'lgximgs',
  secure: true,
  endpoint: 'oss-cn-beijing.aliyuncs.com'
});

async function upload(filePath) {
  const fileName = path.basename(filePath);
  const objectName = 'images/' + fileName;
  await client.put(objectName, filePath);
  console.log('https://lgximgs.oss-cn-beijing.aliyuncs.com/' + objectName);
}

upload(process.argv[2]);
```

使用：

```bash
node ~/.picgo/oss-upload.js "/path/to/image.png"
```

### Typora 配置 PicGo-Core

> Typora → 偏好设置 → 图像 → 上传服务

下拉选择 **`PicGo-Core (Command line)`**，路径填入：

```
/usr/local/bin/picgo
```

（如果 `which picgo` 输出不同路径，按实际填写）

点击「验证图片上传选项」，成功即可使用。右键图片 → 上传图片，自动上传到 OSS。

