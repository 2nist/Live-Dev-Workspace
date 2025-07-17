#!/usr/bin/env python3
"""
LATE Harness API Test Script

Automates API calls to Ableton Live and logs results for integration testing.
"""
import requests
import time
import json
import os

API_URL = "http://localhost:9877/api"  # Example MCP server endpoint
RESULTS_LOG = "results.log"

TEST_CASES = [
    {"endpoint": "/get_session_info", "method": "GET"},
    {"endpoint": "/create_midi_track", "method": "POST", "data": {"index": -1}},
    {"endpoint": "/set_tempo", "method": "POST", "data": {"tempo": 120}},
]

def log_result(entry):
    with open(RESULTS_LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")


def run_tests():
    for test in TEST_CASES:
        url = API_URL + test["endpoint"]
        method = test["method"]
        data = test.get("data")
        print(f"Testing {method} {url} ...")
        try:
            if method == "GET":
                resp = requests.get(url)
            else:
                resp = requests.post(url, json=data)
            result = {
                "endpoint": test["endpoint"],
                "status": resp.status_code,
                "response": resp.json() if resp.content else None,
                "timestamp": time.time()
            }
            print(f"Result: {result['status']}")
            log_result(result)
        except Exception as e:
            print(f"Error: {e}")
            log_result({"endpoint": test["endpoint"], "error": str(e), "timestamp": time.time()})

if __name__ == "__main__":
    run_tests()
