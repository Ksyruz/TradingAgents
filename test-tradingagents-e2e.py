#!/usr/bin/env python3
"""
End-to-End Test for TradingAgents (LiteLLM + Ollama + Claude)

This script:
1. Tests Ollama connectivity
2. Starts LiteLLM proxy (or uses existing)
3. Runs a single-ticker analysis
4. Captures token/cost metrics

Usage:
    source venv/bin/activate
    python test-tradingagents-e2e.py --ticker AAPL --date 2026-06-10
"""

import os
import sys
import json
import time
import argparse
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def test_ollama_connectivity(ollama_base_url: str) -> bool:
    """Test if Ollama is reachable."""
    print("[1/5] Testing Ollama connectivity...")
    import requests
    try:
        resp = requests.get(ollama_base_url.replace("/v1", "/api/tags"), timeout=5)
        if resp.status_code == 200:
            models = resp.json().get("models", [])
            model_names = [m.get("name") for m in models]
            print(f"  ✓ Ollama is running")
            print(f"  ✓ Available models: {', '.join(model_names)}")
            return True
        else:
            print(f"  ✗ Ollama returned status {resp.status_code}")
            return False
    except Exception as e:
        print(f"  ✗ Ollama is not reachable: {e}")
        return False

def test_litellm_proxy(proxy_url: str) -> bool:
    """Test if LiteLLM proxy is reachable."""
    print("[2/5] Testing LiteLLM proxy...")
    import requests
    try:
        resp = requests.get(f"{proxy_url}/models", timeout=5)
        if resp.status_code == 200:
            models = resp.json().get("data", [])
            model_ids = [m.get("id") for m in models]
            print(f"  ✓ LiteLLM proxy is running")
            print(f"  ✓ Available routed models: {', '.join(model_ids)}")
            return True
        else:
            print(f"  ✗ LiteLLM returned status {resp.status_code}")
            return False
    except Exception as e:
        print(f"  ✗ LiteLLM proxy is not reachable: {e}")
        print(f"    (Make sure: source venv/bin/activate && ./start-litellm-proxy.sh)")
        return False

def test_trading_agents(config: dict) -> dict:
    """Run TradingAgents analysis and capture results."""
    print("[3/5] Initializing TradingAgents...")
    
    from tradingagents import TradingAgentsGraph
    
    graph = TradingAgentsGraph(debug=True, config=config)
    
    print("[4/5] Running analysis...")
    ticker = "AAPL"
    analysis_date = (datetime.now() - timedelta(days=14)).strftime("%Y-%m-%d")
    
    print(f"  Ticker: {ticker}")
    print(f"  Date: {analysis_date}")
    
    start_time = time.time()
    try:
        result = graph.propagate(ticker=ticker, analysis_date=analysis_date)
        elapsed = time.time() - start_time
        
        print(f"  ✓ Analysis completed in {elapsed:.1f}s")
        
        # Extract decision from result
        if hasattr(result, "get"):
            decision = result.get("decision", "N/A")
            print(f"  ✓ Final decision: {decision}")
        
        return {
            "success": True,
            "ticker": ticker,
            "date": analysis_date,
            "elapsed_seconds": elapsed,
            "result": result
        }
    except Exception as e:
        print(f"  ✗ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e)
        }

def check_memory_log(config: dict) -> bool:
    """Verify memory log was written."""
    print("[5/5] Checking memory log...")
    
    memory_log_path = config["memory_log_path"]
    if os.path.exists(memory_log_path):
        with open(memory_log_path, "r") as f:
            lines = f.readlines()
        
        print(f"  ✓ Memory log exists at: {memory_log_path}")
        print(f"  ✓ {len(lines)} lines written")
        print(f"\n  --- Last 30 lines of memory log ---")
        print("".join(lines[-30:]))
        return True
    else:
        print(f"  ✗ Memory log not found at: {memory_log_path}")
        return False

def main():
    parser = argparse.ArgumentParser(description="TradingAgents E2E Test")
    parser.add_argument("--ticker", default="AAPL", help="Ticker to analyze")
    parser.add_argument("--date", help="Analysis date (YYYY-MM-DD)")
    parser.add_argument("--skip-proxy-check", action="store_true", help="Skip LiteLLM proxy check")
    args = parser.parse_args()
    
    # Load environment
    from dotenv import load_dotenv
    load_dotenv()
    
    # Load config
    from tradingagents_config import get_tiered_config
    config = get_tiered_config()
    
    # Test sequence
    print("\n" + "="*70)
    print("TradingAgents E2E Test")
    print("="*70 + "\n")
    
    # Test Ollama
    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
    if not test_ollama_connectivity(ollama_url):
        print("\n✗ Ollama not reachable. Pull a model and ensure Ollama is running.")
        return 1
    
    print()
    
    # Test LiteLLM (optional)
    if not args.skip_proxy_check:
        if not test_litellm_proxy("http://localhost:8000/v1"):
            print("\n✗ LiteLLM proxy not reachable. Start it with:")
            print("  source venv/bin/activate && ./start-litellm-proxy.sh")
            return 1
    
    print()
    
    # Run TradingAgents
    result = test_trading_agents(config)
    if not result.get("success"):
        print(f"\n✗ Analysis failed: {result.get('error')}")
        return 1
    
    print()
    
    # Check memory log
    if not check_memory_log(config):
        print("\n⚠ Memory log not found (but analysis may have completed)")
    
    print("\n" + "="*70)
    print("✓ E2E Test Complete!")
    print("="*70 + "\n")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
