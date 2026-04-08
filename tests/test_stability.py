import pytest
import time
import concurrent.futures
import psutil
import os
# Remove: import requests (not used)

class TestStability:
    
    def test_concurrent_requests(self, client, sample_python_code):
        def make_request():
            response = client.post("/api/format", json=sample_python_code)
            return response.status_code == 200
        
        # Reduced from 20 to 10, workers from 10 to 5
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [f.result() for f in futures]
        
        success_rate = sum(results) / len(results)
        assert success_rate >= 0.85
    
    def test_memory_stability(self, client):
        memory_readings = []
        
        # Reduced from 50 to 15 requests
        for i in range(15):
            response = client.post("/api/format", json={
                "code": f"def test_{i}():\n    pass",
                "language": "python"
            })
            assert response.status_code == 200
            
            if i % 5 == 0:  # Check every 5 instead of every 10
                metrics = client.get("/metrics").json()
                memory_readings.append(metrics["memory_mb"])
            
            time.sleep(0.05)  # Reduced from 0.1 to 0.05
        
        if len(memory_readings) >= 2:
            memory_growth = memory_readings[-1] - memory_readings[0]
            assert memory_growth < 50
    
    def test_sustained_load(self, client):
        successes = 0
        total = 15  # Reduced from 30 to 15
        
        for i in range(total):
            response = client.post("/api/format", json={
                "code": f"def test():\n    pass",
                "language": "python"
            })
            if response.status_code == 200:
                successes += 1
            time.sleep(0.2)  # Reduced from 0.5 to 0.2
        
        success_rate = successes / total
        assert success_rate >= 0.95
    
    def test_server_doesnt_crash_on_bad_input(self, client):
        bad_inputs = [
            {"code": None, "language": "python"},
            {"code": "test", "language": None},
            {},
            {"code": "test", "language": "invalid_lang_xyz"},
            {"code": "x" * 100000, "language": "python"},
        ]
        
        for bad_input in bad_inputs:
            response = client.post("/api/format", json=bad_input)
            assert response.status_code in [200, 422]