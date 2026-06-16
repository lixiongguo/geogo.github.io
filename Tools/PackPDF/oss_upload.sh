#!/bin/bash
# 一键上传本地图片到阿里云 OSS 并替换 _posts/ 中的路径
# 用法:
#   ./oss_upload.sh          # 上传 + 替换
#   ./oss_upload.sh --dry    # 仅预览，不实际修改

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CSV_FILE="$SCRIPT_DIR/docs/AccessKey.csv"
UPLOAD_PY="$SCRIPT_DIR/upload_and_replace.py"

# 从 CSV 读取密钥（第二行，逗号分隔）
if [[ ! -f "$CSV_FILE" ]]; then
    echo "ERROR: 未找到 AccessKey.csv ($CSV_FILE)"
    exit 1
fi

AK=$(sed -n '2p' "$CSV_FILE" | cut -d',' -f1 | tr -d '\r\n')
SK=$(sed -n '2p' "$CSV_FILE" | cut -d',' -f2 | tr -d '\r\n')

if [[ -z "$AK" || -z "$SK" ]]; then
    echo "ERROR: 无法从 AccessKey.csv 读取密钥"
    exit 1
fi

export OSS_ACCESS_KEY_ID="$AK"
export OSS_ACCESS_KEY_SECRET="$SK"

cd "$SCRIPT_DIR/../.."  # 回到项目根目录

if [[ "${1:-}" == "--dry" ]]; then
    python3 "$UPLOAD_PY" --dry
else
    python3 "$UPLOAD_PY"
fi
