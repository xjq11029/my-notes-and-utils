#!/usr/bin/env bash
# 初始化脚本示例（Linux / macOS）
set -e
# Python venv
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
echo "虚拟环境已创建并激活 (.venv)"

# Node (可选)
# npm install

echo "完成。请根据需要安装依赖。"
