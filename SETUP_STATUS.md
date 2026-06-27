# TradingAgents Local+API Setup — Status Report

**Date:** 2026-06-25  
**Machine:** Mac (running tests & proxy)  
**Linux Machine:** Pop!_OS at 10.10.0.192 (running Ollama)  

---

## ✅ **COMPLETED**

### Environment & Dependencies
- [x] Python 3.13 venv created at `./venv`
- [x] TradingAgents package installed via `pip install -e .`
- [x] LiteLLM installed (`pip install litellm`)
- [x] All required Python dependencies ready

### Configuration Files
- [x] `.env` populated with:
  - `ANTHROPIC_API_KEY` ✓ (for Claude deep_think_llm)
  - `OPENAI_API_KEY` ✓ (bonus)
  - `GROQ_API_KEY` ✓ (bonus)
  - `OLLAMA_BASE_URL=http://10.10.0.192:11434/v1` ✓ (points to Linux machine)
  - `LITELLM_MASTER_KEY` ✓ (generated)
  - `TRADINGAGENTS_*` env-vars for all framework config ✓

- [x] `litellm-config.yaml` created with:
  - Deep route: `claude-opus-4-1` → Anthropic API
  - Quick route: `mistral-large` / `neural-chat` → Ollama
  - Single endpoint: `http://localhost:8000/v1`

- [x] `.gitignore` verified (`.env` excluded, safe from accidental commits)

### Execution Scripts
- [x] `start-litellm-proxy.sh` — starts the routing proxy
- [x] `pull-ollama-model.sh` — helper to pull model to Linux machine
- [x] `test-tradingagents-e2e.py` — full e2e test harness
- [x] `tradingagents_config.py` — config loader with env-var override

### Documentation
- [x] `SETUP_CHECKLIST.md` — detailed configuration reference
- [x] Session memory logged at `/memories/session/tradingagents-setup.md`

---

## ⏳ **BLOCKED: AWAITING OLLAMA MODEL**

### Current Issue
No models are yet pulled to Ollama on 10.10.0.192.

### Required Action (User)
Pull a strong model to Ollama on your Linux machine. Choose one:

```bash
# SSH into your Linux machine:
ssh user@10.10.0.192

# Pull the recommended model (takes ~10-15 minutes):
ollama pull mistral-large

# Verify it worked:
curl http://localhost:11434/api/tags | jq '.models[].name'
# Should output: "mistral-large"
```

**Model Recommendation:** `mistral-large`
- 46B parameters
- ~26GB VRAM at Q4 (fits comfortably in 48GB)
- Strong reasoning capability for analyst work
- Good balance of speed vs. quality

**Alternatives:**
- `neural-chat` (38B, ~21GB, faster)
- `dolphin-mixtral` (46B, ~27GB, creative)

---

## 📋 **NEXT STEPS (After Model is Pulled)**

Once you confirm the model is available on Ollama:

### Step 1: Verify Ollama Connectivity (Mac)
```bash
curl http://10.10.0.192:11434/api/tags | jq '.models[].name'
# Should list: ["mistral-large"] (or whatever you pulled)
```

### Step 2: Start LiteLLM Proxy (Mac, this folder)
```bash
source venv/bin/activate
./start-litellm-proxy.sh
# Should output: "Uvicorn running on http://0.0.0.0:8000"
```
This runs in foreground. Keep it running or run in a separate terminal.

### Step 3: Run E2E Test (Mac, in another terminal)
```bash
source venv/bin/activate
python test-tradingagents-e2e.py
```

This will:
1. ✓ Test Ollama connectivity (10.10.0.192:11434)
2. ✓ Test LiteLLM proxy (localhost:8000)
3. ✓ Run analysis on AAPL for 2 weeks ago
4. ✓ Verify memory log was written
5. ✓ Print decision and metrics

### Step 4: Capture Token/Cost Metrics
After test completes, look for:
- **LiteLLM logs** (stdout): Claude token usage & cost
- **Memory log**: `~/.tradingagents/memory/trading_memory.md`
- **Local metrics**: Ollama inference time

---

## 🏗️ **Architecture Summary**

```
┌─────────────────────────────────────────────────────────────┐
│                     TradingAgents                           │
│                  (on this Mac)                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  quick_think_llm (Analysts)                                 │
│         │                                                   │
│         └──→ [LiteLLM Proxy @ localhost:8000/v1]            │
│              │                                              │
│         ┌────┴────────────────────────────────────────────┐ │
│         │                                                 │ │
│    deep_think_llm                        quick route      │ │
│   (Researchers,                                           │ │
│    Traders,                          "mistral-large"      │ │
│    Portfolio)                              │              │ │
│         │                                  └─────┐        │ │
│         │                                        │        │ │
│         └────────────────────────────────────┐   │        │ │
│                                              │   │        │ │
│           "claude-opus-4-1" (Anthropic)     │   │        │ │
│                                              │   │        │ │
│         ┌────────────────────────────────────┘   │        │ │
│         │                                        │        │ │
│         ▼                                        ▼        │ │
│     [Claude API]                        [Ollama @ .192] │ │
│     (High-leverage)                     (High-volume)   │ │
│     $$ cost, high quality               $0 cost, local  │ │
│                                         GPU time        │ │
│                                                         │ │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 **Expected Token/Cost Breakdown**

Once we run the full test, you'll see (estimated):

| Tier | Model | Tokens | Cost | Use Case |
|------|-------|--------|------|----------|
| **Deep** | Claude Opus | 2,000-5,000 | $0.05-0.15 | Researcher debate, portfolio decision |
| **Quick** | Mistral 46B | 10,000-20,000 | $0 | Analyst reports (fundamental, sentiment, news) |

Total per run: ~$0.10-0.20 (Claude only; Ollama is free local)

---

## 🆘 **Troubleshooting**

### "Ollama not reachable"
- Confirm Ollama is running on Linux machine: `ollama serve` or Docker container
- Confirm model is pulled: `ollama list`
- Confirm firewall allows `10.10.0.192:11434` from Mac

### "LiteLLM proxy not reachable"
- Ensure it's running: `./start-litellm-proxy.sh`
- Check port 8000 is free: `lsof -i :8000`
- Verify .env is loaded: Check console output for API keys

### "Analysis hangs"
- Check LiteLLM logs for routing errors
- Verify Anthropic key is valid (test with `curl` to Claude via LiteLLM)
- Verify Ollama model name matches config

---

## 🎯 **Summary: What Happens Next**

1. You pull `mistral-large` to 10.10.0.192:11434 ← **YOUR ACTION**
2. I start the LiteLLM proxy (localhost:8000) ← **MY ACTION**
3. I run the e2e test ← **MY ACTION**
4. I generate token/cost report ← **MY ACTION**
5. System is ready for backtesting & live runs ← **DONE**

---

**Next:** SSH to your Linux machine and pull the model, then let me know when it's done!
