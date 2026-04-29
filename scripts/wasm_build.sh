#!/bin/bash
# wasm_build.sh - 使用 emsdk 编译 conformal-parameterization 为 WebAssembly
# 使用方法: bash scripts/wasm_build.sh

# 不设置 set -e，手动处理错误

echo "==================================="
echo "Conformal Parameterization WASM Build"
echo "==================================="

# 获取脚本所在目录的绝对路径
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# 设置路径
EMSDK_PATH="$PROJECT_ROOT/cpp/emsdk"
SRC_DIR="$PROJECT_ROOT/cpp/conformal-parameterization"
OUT_DIR="$PROJECT_ROOT/assets/wasm"
EMSDK_SCRIPT="$EMSDK_PATH/emsdk"

echo "项目根目录: $PROJECT_ROOT"
echo "EMSdk 路径: $EMSDK_PATH"
echo "源码目录: $SRC_DIR"
echo "输出目录: $OUT_DIR"
echo ""

# 检查 emsdk 是否存在
if [ ! -d "$EMSDK_PATH" ]; then
    echo "[错误] 未找到 emsdk 目录: $EMSDK_PATH"
    exit 1
fi

# 确保 emsdk 脚本可执行
chmod +x "$EMSDK_SCRIPT" 2>/dev/null || true
chmod +x "$EMSDK_PATH/emsdk_env.sh" 2>/dev/null || true

# 检查 emsdk 是否可以运行
echo "检查 emsdk 工具..."
cd "$EMSDK_PATH"
if ! python3 "$EMSDK_SCRIPT" --version &>/dev/null && ! python "$EMSDK_SCRIPT" --version &>/dev/null; then
    echo "[警告] emsdk 脚本可能无法正常运行"
    echo "尝试直接运行: python3 $EMSDK_SCRIPT list"
    echo ""
fi

# 安装并激活 emsdk（如果 emcc 不可用）
if ! command -v emcc &> /dev/null; then
    echo "[警告] 未找到 emcc，尝试安装 Emscripten SDK..."
    echo ""
    
    # 更新 emsdk
    echo "[步骤 1/4] 更新 emsdk..."
    git pull 2>/dev/null || echo "  (git pull 失败，继续...)"
    
    # 安装最新版本
    echo ""
    echo "[步骤 2/4] 安装最新版 Emscripten（这可能需要几分钟）..."
    echo "  执行: $EMSDK_SCRIPT install latest"
    
    if [ -f "$EMSDK_SCRIPT" ]; then
        python3 "$EMSDK_SCRIPT" install latest 2>&1 || python "$EMSDK_SCRIPT" install latest 2>&1
        INSTALL_RESULT=$?
        
        if [ $INSTALL_RESULT -ne 0 ]; then
            echo ""
            echo "[错误] emsdk install 失败 (退出码: $INSTALL_RESULT)"
            echo ""
            echo "请尝试手动安装:"
            echo "  cd $EMSDK_PATH"
            echo "  ./emsdk install latest"
            echo ""
            exit 1
        fi
    else
        echo "[错误] 未找到 emsdk 脚本: $EMSDK_SCRIPT"
        exit 1
    fi
    
    # 激活最新版本
    echo ""
    echo "[步骤 3/4] 激活 Emscripten..."
    python3 "$EMSDK_SCRIPT" activate latest 2>&1 || python "$EMSDK_SCRIPT" activate latest 2>&1
    
    cd "$PROJECT_ROOT"
    echo ""
fi

# 激活 Emscripten 环境
echo "[步骤 4/4] 激活 Emscripten 环境..."
source "$EMSDK_PATH/emsdk_env.sh"

# 验证 emcc 是否可用
if ! command -v emcc &> /dev/null; then
    echo "[错误] 未找到 emcc 编译器"
    echo ""
    echo "请手动执行以下步骤:"
    echo "  cd $EMSDK_PATH"
    echo "  ./emsdk install latest"
    echo "  ./emsdk activate latest"
    echo "  source ./emsdk_env.sh"
    echo "  emcc --version"
    echo ""
    echo "然后重新运行此脚本: bash $0"
    exit 1
fi

EMCC_VERSION=$(emcc --version | head -n 1)
echo "[OK] 找到 emcc: $EMCC_VERSION"
echo ""

# 创建输出目录
echo "[2/3] 创建输出目录..."
mkdir -p "$OUT_DIR"
echo "  输出目录: $OUT_DIR"
echo ""

# 切换到源码目录
cd "$SRC_DIR"

echo "[3/3] 编译 WASM 模块..."
echo "  使用 C++17 标准，优化级别 O2"
echo ""

# 编译选项 (匹配 uv-unwrap.html 的需求)
EMCC_FLAGS=(
    # C++ 标准与优化
    -std=c++17
    -O2
    -Wall

    # Include 路径
    -I./deps
    -I.

    # Emscripten 标志 (MODULARIZE + EXPORT_NAME 匹配 HTML)
    -s WASM=1
    -s MODULARIZE=1
    -s EXPORT_NAME="LSCMSolver"
    # -s "EXPORTED_RUNTIME_METHODS=['ccall','cwrap','getValue','setValue','UTF8ToString','stringToUTF8','lengthBytesUTF8','_malloc','_free']"
    -s "EXPORTED_RUNTIME_METHODS=['ccall','cwrap','getValue','setValue','UTF8ToString','stringToUTF8','lengthBytesUTF8']"
    -s "EXPORTED_FUNCTIONS=['_malloc','_free']"
    -s ALLOW_MEMORY_GROWTH=1
    -s FORCE_FILESYSTEM=1
    -s DISABLE_EXCEPTION_CATCHING=1

    # 注意：不使用 --bind，因为 wasm_main.cpp 使用 EMSCRIPTEN_KEEPALIVE (C 接口)

    # 禁用异常 (与 DISABLE_EXCEPTION_CATCHING 配合)
    -fno-exceptions
)

# 源文件 (使用 wasm_main.cpp，提供 C 接口)
SRCS=(
    wasm_main.cpp
    Mesh.cpp
    MeshIO.cpp
    Lscm.cpp
    Parameterization.cpp
    QcError.cpp
    Solver.cpp
    Vertex.cpp
    Edge.cpp
    Face.cpp
    HalfEdge.cpp
)

# 输出文件 (匹配 uv-unwrap.html 中的引用)
OUTPUT_JS="$OUT_DIR/lscm_solver.js"
OUTPUT_WASM="$OUT_DIR/lscm_solver.wasm"

echo "执行编译命令..."
emcc "${EMCC_FLAGS[@]}" "${SRCS[@]}" -o "$OUTPUT_JS"

if [ $? -ne 0 ]; then
    echo "[失败] 编译出错"
    exit 1
fi

echo ""
echo "==================================="
echo "编译完成！"
echo "==================================="
echo ""
echo "生成的文件:"
if [ -f "$OUTPUT_JS" ]; then
    echo "  [OK] $OUTPUT_JS"
else
    echo "  [警告] 未找到 $(basename "$OUTPUT_JS")"
fi

if [ -f "$OUTPUT_WASM" ]; then
    echo "  [OK] $OUTPUT_WASM"
else
    echo "  [警告] 未找到 $(basename "$OUTPUT_WASM")"
fi

# 检查是否生成了 worker 文件
if [ -f "$OUT_DIR/lscm_solver.worker.js" ]; then
    echo "  [OK] $OUT_DIR/lscm_solver.worker.js"
fi

echo ""
echo "在 JavaScript 中使用 (参见 uv-unwrap.html):"
echo "  <!-- 在 HTML 中引用 -->"
echo "  <script src=\"assets/wasm/lscm_solver.js\"></script>"
echo ""
echo "  // 在 JS 中调用"
echo "  const module = await LSCMSolver();"
echo "  const posPtr = module._malloc(...);"
echo "  const facePtr = module._malloc(...);"
echo "  module.ccall('solve_lscm', 'number', [...], [...]);"
echo "  const uvSize = module.ccall('get_uv_result_size', 'number', [], []);"
echo "  const uvPtr = module.ccall('get_uv_result', 'number', [], []);"
echo "  // ... 读取 UV 数据 ..."
echo "  module.ccall('dispose', 'void', [], []);"
echo "  module._free(posPtr);"
echo ""

cd "$PROJECT_ROOT"

echo "==================================="
echo "下次编译时，只需运行:"
echo "  bash scripts/wasm_build.sh"
echo "==================================="
