#!/bin/bash
# pull-ollama-model.sh
# Run this on your Pop!_OS Linux machine to pull a model for TradingAgents
# 
# Usage:
#   ssh user@10.10.0.192 'bash -s' < pull-ollama-model.sh
#   OR manually SSH and run the commands below

set -e

echo "=========================================="
echo "Pulling Ollama Model for TradingAgents"
echo "=========================================="
echo ""

# Ensure Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
  echo "ERROR: Ollama is not running at http://localhost:11434"
  echo "Start Ollama with: docker compose up -d ollama (or: ollama serve)"
  exit 1
fi

# Pull a strong 32B reasoning model
# Options (all ~22-26GB at Q4; all fit well in 48GB VRAM):
#   - mistral-large       (46B, best reasoning, ~26GB Q4)
#   - neural-chat         (38B, fast, ~21GB Q4)
#   - dolphin-mixtral     (46B, creative, ~27GB Q4)
#   - qwen2:32b           (32B, balanced, ~19GB Q4)
#   - llama2:70b          (70B, reasoning-heavy, ~39GB Q4)

MODEL="${1:-mistral-large}"

echo "Pulling model: $MODEL"
echo "(This may take 5-15 minutes depending on speed and model size)"
echo ""

ollama pull "$MODEL"

echo ""
echo "=========================================="
echo "✓ Model '$MODEL' pulled successfully!"
echo "=========================================="
echo ""
echo "Verify it's available:"
echo "  curl http://localhost:11434/api/tags | jq '.models[].name'"
echo ""
echo "Update TradingAgents .env:"
echo "  TRADINGAGENTS_QUICK_THINK_LLM=$MODEL"
