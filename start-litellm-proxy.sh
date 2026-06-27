#!/bin/bash
# start-litellm-proxy.sh
# Starts the LiteLLM proxy listening on http://localhost:8000/v1
# Routes deep_think_llm to Claude (Anthropic API)
# Routes quick_think_llm to Ollama (local)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="${SCRIPT_DIR}/litellm-config.yaml"

# Ensure .env is loaded
if [ -f "${SCRIPT_DIR}/.env" ]; then
  set -a
  source "${SCRIPT_DIR}/.env"
  set +a
else
  echo "ERROR: .env file not found at ${SCRIPT_DIR}/.env"
  exit 1
fi

# Validate required env vars
if [ -z "$ANTHROPIC_API_KEY" ]; then
  echo "ERROR: ANTHROPIC_API_KEY not set in .env"
  exit 1
fi

if [ -z "$OLLAMA_BASE_URL" ]; then
  echo "ERROR: OLLAMA_BASE_URL not set in .env"
  exit 1
fi

if [ -z "$LITELLM_MASTER_KEY" ]; then
  echo "WARNING: LITELLM_MASTER_KEY not set; generating one..."
  export LITELLM_MASTER_KEY=$(openssl rand -hex 16)
  echo "Generated LITELLM_MASTER_KEY: $LITELLM_MASTER_KEY"
fi

echo "Starting LiteLLM Proxy..."
echo "  Config: ${CONFIG_FILE}"
echo "  Anthropic API Key: ${ANTHROPIC_API_KEY:0:10}..."
echo "  Ollama Base URL: ${OLLAMA_BASE_URL}"
echo "  LiteLLM Proxy will listen on: http://localhost:8000/v1"
echo ""

# Run litellm proxy
litellm --config "${CONFIG_FILE}" \
  --port 8000 \
  --num_workers 2 \
  --debug
