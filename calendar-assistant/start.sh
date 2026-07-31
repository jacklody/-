#!/bin/bash

# 日历助手 - 启动脚本
echo "🚀 启动日历助手..."
echo ""

# 进入项目目录
cd "$(dirname "$0")"

# 检查Python是否可用
if command -v python3 &> /dev/null; then
    echo "✅ 使用 Python 3 启动服务器"
    echo "📍 服务地址: http://localhost:8080"
    echo ""
    echo "💡 按 Ctrl+C 停止服务器"
    echo ""
    python3 -m http.server 8080
elif command -v python &> /dev/null; then
    echo "✅ 使用 Python 启动服务器"
    echo "📍 服务地址: http://localhost:8080"
    echo ""
    echo "💡 按 Ctrl+C 停止服务器"
    echo ""
    python -m http.server 8080
else
    echo "❌ 错误: 未找到 Python，无法启动服务器"
    echo ""
    echo "请使用其他方式启动HTTP服务器，例如:"
    echo "  - Node.js: npx serve ."
    echo "  - PHP: php -S localhost:8080"
    echo "  - 或者直接用浏览器打开 index.html 文件"
    echo ""
    exit 1
fi