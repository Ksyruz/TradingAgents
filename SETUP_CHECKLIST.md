# TradingAgents Local+API Tiered Setup — Configuration Checklist

## ✅ Completed Setup Steps

### Environment
- [x] Python 3.13 venv created at `/Users/ahmed/src/TradingAgents/venv`
- [x] TradingAgents installed via `pip install -e .`

### Configuration Files
- [x] `.env` created with placeholders for:
  - `ANTHROPIC_API_KEY` (required for deep_think_llm / Claude)
  - `OLLAMA_BASE_URL` (for routing to local Ollama)
  - `TRADINGAGENTS_*` env-vars for framework override
  
- [x] `.gitignore` verified to exclude `.env` (no secrets in Git)

- [x] `litellm-config.yaml` created with:
  - Deep routing: `claude-opus-4-1` → Anthropic API
  - Quick routing: `mistral-large` / `neural-chat` → Ollama (OpenAI-compatible)
  - Single endpoint: `http://localhost:8000/v1`

- [x] `tradingagents_config.py` created to load config with env-var overrides

- [x] `start-litellm-proxy.sh` created to start the proxy daemon

---

## 🔴 ACTION REQUIRED: Complete These Steps

### 1. **Provide Ollama Details**
   - **Hostname/IP of your Linux machine** (where Ollama is running)
     - Example: `192.168.1.100` or `linux-machine.local`
   - Update `.env` `OLLAMA_BASE_URL` to point to it:
     ```bash
     OLLAMA_BASE_URL=http://<YOUR_LINUX_IP_OR_HOSTNAME>:11434/v1
     ```

### 2. **Add Anthropic API Key**
   - Get your **Claude API key** from https://console.anthropic.com/
   - Add to `.env`:
     ```bash
     ANTHROPIC_API_KEY=sk-ant-...
     ```

### 3. **Install & Test LiteLLM**
   In the venv:
   ```bash
   source venv/bin/activate
   pip install litellm
   ```

### 4. **Verify Ollama Models**
   Once you provide the Linux IP, test Ollama connectivity:
   ```bash
   curl http://<YOUR_LINUX_IP>:11434/api/tags | jq '.models[].name'
   ```
   
   Confirm one of these is available:
   - `mistral-large` (recommended: 46B, ~26GB Q4)
   - `neural-chat` (38B, ~21GB Q4)
   - `dolphin-mixtral` (46B, ~27GB Q4)
   
   If none exist, pull one:
   ```bash
   # SSH into Linux machine and run:
   ollama pull mistral-large
   ```

### 5. **Generate LiteLLM Master Key** (optional but recommended)
   ```bash
   openssl rand -hex 16
   ```
   Add to `.env`:
   ```bash
   LITELLM_MASTER_KEY=<generated-key>
   ```

### 6. **Add Optional API Keys** (if using these data sources)
   - **Alpha Vantage** (stock fundamentals): https://www.alphavantage.co/api/
   - **FRED** (macro data): https://fred.stlouisfed.org/docs/api/
   
   Add to `.env`:
   ```bash
   ALPHA_VANTAGE_API_KEY=...
   FRED_API_KEY=...
   ```

---

## 🧪 Testing Sequence (Once Requirements Above Met)

### A. Start LiteLLM Proxy
```bash
cd /Users/ahmed/src/TradingAgents
source venv/bin/activate
./start-litellm-proxy.sh
```
Should log: `Uvicorn running on http://0.0.0.0:8000`

### B. Test LiteLLM Routes (in another terminal)
```bash
# Test Claude (deep_think)
curl http://localhost:8000/v1/models | jq '.data[] | select(.id == "claude-opus-4-1")'

# Test Ollama/Mistral (quick_think)
curl http://localhost:8000/v1/models | jq '.data[] | select(.id == "mistral-large")'
```

### C. Run End-to-End Test
Create and run `test-tradingagents.py`:
```python
#!/usr/bin/env python3
import os
from datetime import datetime, timedelta
from tradingagents_config import get_tiered_config
from tradingagents import TradingAgentsGraph

# Load config from .env
config = get_tiered_config()

# Initialize graph
print("\n[1/3] Initializing TradingAgents graph...")
graph = TradingAgentsGraph(debug=True, config=config)

# Run for AAPL, 2 weeks ago
test_ticker = "AAPL"
test_date = (datetime.now() - timedelta(days=14)).strftime("%Y-%m-%d")

print(f"\n[2/3] Running analysis for {test_ticker} on {test_date}...")
result = graph.propagate(ticker=test_ticker, analysis_date=test_date)

print(f"\n[3/3] Checking memory log...")
memory_log_path = config["memory_log_path"]
if os.path.exists(memory_log_path):
    print(f"✓ Memory log written to: {memory_log_path}")
    with open(memory_log_path, "r") as f:
        lines = f.readlines()
    print(f"  ({len(lines)} lines, last 20 lines:)\n")
    print("".join(lines[-20:]))
else:
    print(f"✗ Memory log not found at {memory_log_path}")

print("\n✓ End-to-end test complete!")
```

### D. Capture Token/Cost Summary
After test completes, extract:
- LiteLLM logs for Claude token usage (API spend)
- Local Ollama inference time & token counts (GPU utilization)

---

## 📋 Next Steps (After I Hear From You)

Once you provide:
1. Linux machine IP/hostname
2. Anthropic API key
3. Confirm available Ollama models

I will:
1. Update `.env` with your details
2. Install LiteLLM
3. Start the proxy
4. Run the full e2e test
5. Generate the token/cost report

**Ready to provide the details?**
