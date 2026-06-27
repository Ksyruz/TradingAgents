"""
TradingAgents Configuration Override for LiteLLM + Ollama + Claude Setup

This module provides a pre-configured setup for:
  - Deep thinking (high-leverage): Claude via Anthropic API
  - Quick thinking (high-volume): Local model via Ollama + LiteLLM proxy
  
Both tiers are routed through a single LiteLLM endpoint at http://localhost:8000/v1

Usage:
    from tradingagents_config import get_tiered_config
    config = get_tiered_config()
    graph = TradingAgentsGraph(config=config, debug=True)
    result = graph.propagate(ticker="AAPL", analysis_date="2026-06-10")
"""

import os
from tradingagents.default_config import DEFAULT_CONFIG


def get_tiered_config():
    """Return a config dict with deep/quick tier routing via LiteLLM.
    
    Expects these env-vars to be set:
      - TRADINGAGENTS_LLM_BACKEND_URL: LiteLLM proxy endpoint (default: http://localhost:8000/v1)
      - TRADINGAGENTS_DEEP_THINK_LLM: Claude model name (default: claude-opus-4-1)
      - TRADINGAGENTS_QUICK_THINK_LLM: Local model name (default: mistral-large)
      - TRADINGAGENTS_MAX_DEBATE_ROUNDS: Debate rounds (default: 2)
      - TRADINGAGENTS_MAX_RISK_ROUNDS: Risk discussion rounds (default: 1)
      - TRADINGAGENTS_TEMPERATURE: Temperature for LLM (default: 0.0)
    
    If not set, defaults are used.
    
    Returns:
        dict: Configuration dict ready for TradingAgentsGraph
    """
    config = DEFAULT_CONFIG.copy()
    
    # Override via DEFAULT_CONFIG's built-in env-var coercion
    # (uses TRADINGAGENTS_* env-vars if present)
    # This happens automatically during DEFAULT_CONFIG construction,
    # so we just return it.
    
    # Explicitly log what we're using (helpful for debugging):
    print("=" * 70)
    print("TradingAgents Configuration (LiteLLM Tiered Setup)")
    print("=" * 70)
    print(f"LLM Provider: {config['llm_provider']}")
    print(f"Backend URL: {config['backend_url']}")
    print(f"Deep Think Model (Claude): {config['deep_think_llm']}")
    print(f"Quick Think Model (Local): {config['quick_think_llm']}")
    print(f"Max Debate Rounds: {config['max_debate_rounds']}")
    print(f"Max Risk Rounds: {config['max_risk_discuss_rounds']}")
    print(f"Temperature: {config['temperature']}")
    print("=" * 70)
    
    return config


if __name__ == "__main__":
    # Quick test: print the config
    cfg = get_tiered_config()
    print("\nFull config dict:")
    import json
    print(json.dumps(cfg, indent=2, default=str))
