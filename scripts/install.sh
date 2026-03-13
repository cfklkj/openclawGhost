#!/bin/bash
# openclawGhost 安装脚本

echo "安装 openclawGhost..."

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "错误：需要安装 Python 3.8+"
    exit 1
fi

# 安装依赖
pip3 install -r requirements.txt

# 安装包
pip3 install -e .

echo "✓ 安装完成"
echo "运行 'openclawGhost --help' 开始使用"
