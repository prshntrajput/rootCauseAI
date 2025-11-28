#!/bin/bash

echo "🚀 rootCauseAI CLI Demo"
echo "======================================"
echo ""

echo "📦 1. Check installation"
fix-error version
echo ""

echo "📊 2. Show statistics"
fix-error stats
echo ""

echo "📜 3. Show history"
fix-error history --count 5
echo ""

echo "❓ 4. Show help"
fix-error --help
echo ""

echo "✅ Demo complete!"
echo ""
echo "Try these commands:"
echo "  fix-error run 'python script.py'"
echo "  fix-error fix 'TypeError: ...'"
echo "  fix-error config"
