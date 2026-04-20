---
name: uv-unwrap-esm-modernization
overview: 将 uv-unwrap.html 从 Three.js v0.117.0 全局脚本 + IIFE 模式迁移至现代 ESModule 风格：使用 importmap、升级到 r170+、从 three/addons 导入扩展模块、移除 IIFE、全面现代化代码风格
design:
  architecture:
    framework: html
  styleKeywords:
    - NoUIChange
    - RefactorOnly
  fontSystem:
    fontFamily: Segoe UI
    heading:
      size: 20px
      weight: 600
    subheading:
      size: 14px
      weight: 500
    body:
      size: 14px
      weight: 400
  colorSystem:
    primary:
      - "#7fa7ff"
      - "#86b2ff"
    background:
      - "#070b14"
      - "#0b1220"
    text:
      - "#d8def7"
      - "#eef2ff"
    functional:
      - "#89f0b6"
      - "#ff9d9d"
      - "#ffd38a"
      - "#ffd700"
todos:
  - id: replace-imports
    content: 替换 head 中的三个全局 script 标签为 import map 配置，升级 Three.js 到 r170
    status: completed
  - id: rewrite-module-block
    content: 将 script 标签改为 type=module，添加 import 语句，移除 IIFE，替换所有 THREE.xxx 为具名导入
    status: completed
    dependencies:
      - replace-imports
  - id: modernize-code-style
    content: 清理重复 setStatus 定义，Promise/回调/事件监听全部改箭头函数，统一现代语法风格
    status: completed
    dependencies:
      - rewrite-module-block
  - id: verify-api-compat
    content: 检查并修复 v0.117→r170 跨版本 API 兼容性问题，确保功能正常运行
    status: completed
    dependencies:
      - modernize-code-style
---

## 产品概述

将 `uv-unwrap.html` 从老旧的全局脚本 + Three.js v0.117.0 风格迁移到现代 ESModule + import map 风格，同时升级 Three.js 到最新版本。

## 核心功能

- **Three.js 升级**：从 v0.117.0（2020 年）升级到最新稳定版（当前 r170+）
- **ESModule 化**：将 `<script src="...">` 全局加载改为 `<script type="importmap">` + `import { ... }` 语法
- **API 迁移**：处理 Three.js 版本跨越导致的 API 变更（如 `examples/js/` → `examples/jsm/` 路径变化、构造函数参数变更等）
- **代码现代化**：
- 移除 IIFE 包裹（ESModule 自带作用域隔离）
- `new Promise(function(){})` → Promise 构造器改用箭头函数
- 回调风格事件监听统一使用箭头函数
- 重复的 `setStatus` 函数定义清理
- **保持纯静态**：不引入构建工具链，继续使用 CDN + 单 HTML 文件形式，兼容 GitHub Pages 托管

## 技术栈

- **目标框架**：原生 ESModule（浏览器原生支持）
- **模块系统**：Import Maps（`<script type="importmap">`）实现裸模块名解析
- **Three.js**：从 v0.117.0 升级到 r170+
- **CDN**：继续使用 jsdelivr / cdnjs / unpkg 等 CDN
- **无构建工具**：保持单文件 HTML 形式

## 实现方案

### 核心策略：Import Map + ESModule

由于项目是纯静态 GitHub Pages 站点，无构建工具链，最佳方案是使用浏览器原生的 **Import Maps** 特征（Chrome 89+ / Firefox 108+ / Safari 16.4+ 均已支持）。

### 具体改动点分析

#### 1. 外部依赖加载方式（最关键的变化）

**旧代码（L7-9）：**

```html
<script src="https://cdn.jsdelivr.net/npm/three@v0.117.0"></script>
<script src=".../OrbitControls.js"></script>   <!-- examples/js/ 全局脚本 -->
<script src=".../OBJLoader.js"></script>          <!-- examples/js/ 全局脚本 -->
```

**新代码：**

```html
<script type="importmap">
{
  "imports": {
    "three": "https://cdn.jsdelivr.net/npm/three@0.170.0/build/three.module.js",
    "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.170.0/examples/jsm/"
  }
}
</script>
```

关键路径变化：

| 旧路径 (v0.117) | 新路径 (r170) |
| --- | --- |
| `examples/js/controls/OrbitControls.js` | `examples/jsm/controls/OrbitControls.js` |
| `examples/js/loaders/OBJLoader.js` | `examples/jsm/loaders/OBJLoader.js` |


#### 2. 模块导入语法

**旧代码（L278, L295）：**

```javascript
const objLoader = new THREE.OBJLoader();
const controls = new THREE.OrbitControls(modelCamera, modelCanvas);
```

**新代码：**

```javascript
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { OBJLoader } from 'three/addons/loaders/OBJLoader.js';

const objLoader = new OBJLoader();
const controls = new OrbitControls(modelCamera, modelCanvas);
```

注意：新版 `OBJLoader` 和 `OrbitControls` 是具名导出的类实例，不再是挂载在 `THREE` 命名空间下的全局对象。

#### 3. script 标签改造

**旧代码（L253）：**

```html
<script>
(function() {
  // 所有逻辑...
})();
</script>
```

**新代码：**

```html
<script type="module">
// 直接写逻辑，无需 IIFE 包裹
// ESModule 自动作用域隔离
</script>
```

#### 4. 代码内部现代化（附带优化）

| 位置 | 旧代码问题 | 新代码改进 |
| --- | --- | --- |
| L320, L344 | `setStatus` 函数重复定义了两次 | 删除重复定义 |
| L402, L442 | `new Promise(function(resolve, reject){...})` | 改用箭头函数 `new Promise((resolve, reject) => {...})` |
| L444, L452, L479 等 | 大量 `function() {}` 回调 | 统一使用箭头函数 `() => {}` |
| L254 | `(function() {...})();` IIFE | 删除，ESModule 天然作用域隔离 |
| L1132-1180 | 所有事件监听器的匿名 function | 改为箭头函数 |


#### 5. API 兼容性注意事项（v0.117→r170 跨度大）

需要验证以下可能的 API 变更：

- `THREE.Geometry` 已被移除（r125 废弃），但本代码主要用 `BufferGeometry`，应无影响
- `THREE.Face3` 相关 API 变更 — 本代码未直接使用
- `OrbitControls` 构造函数签名可能变化 — r170 的 OrbitControls 构造参数不变
- `OBJLoader.parse()` 返回值结构 — 保持兼容
- `CanvasTexture` / `MeshStandardMaterial` 接口 — 保持稳定

## 目录结构

```
/Users/lgxgeogo/Desktop/MyDoc/lixiongguo.github.io/
├── uv-unwrap.html                    # [MODIFY] 主目标文件：ESModule 现代化重构
│   ├── <head>                        # [MODIFY] 替换 script src 为 importmap
│   ├── <style>                       # [KEEP] CSS 无需变动
│   └── <script type="module">        # [MODIFY] 整个 JS 逻辑块重写为 ESM 风格
```

仅涉及单个文件的修改，不影响项目其他部分。

本次任务不涉及 UI 创建或视觉设计变更。仅对 uv-unwrap.html 内部的 JavaScript 进行 ESModule 现代化重构和 Three.js 版本升级。页面外观、布局、交互体验完全保持不变。