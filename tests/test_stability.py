import pytest
import time
import concurrent.futures
import requests
import psutil
import os

class TestStability:
    
    def test_concurrent_requests(self, client, sample_python_code):
        """Test handling multiple concurrent requests"""
        
        def make_request():
            response = client.post("/api/format", json=sample_python_code)
            return response.status_code == 200
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(20)]
            results = [f.result() for f in futures]
        
        success_rate = sum(results) / len(results)
        assert success_rate >= 0.85  # At least 85% success rate
    
    def test_memory_stability(self, client):
        """Test memory doesn't leak over multiple requests"""
        import subprocess
        
        memory_readings = []
        
        # Make 50 requests
        for i in range(50):
            response = client.post("/api/format", json={
                "code": f"def test_{i}():\n    pass",
                "language": "python"
            })
            assert response.status_code == 200
            
            # Get memory usage every 10 requests
            if i % 10 == 0:
                metrics = client.get("/metrics").json()
                memory_readings.append(metrics["memory_mb"])
            
            time.sleep(0.1)
        
        # Check memory growth (shouldn't grow more than 50MB)
        if len(memory_readings) >= 2:
            memory_growth = memory_readings[-1] - memory_readings[0]
            assert memory_growth < 50, f"Memory grew by {memory_growth}MB"
    
    def test_sustained_load(self, client):
        """Test sustained load over time"""
        successes = 0
        total = 30
        
        for i in range(total):
            response = client.post("/api/format", json={
                "code": f"def test():\n    pass",
                "language": "python"
            })
            if response.status_code == 200:
                successes += 1
            time.sleep(0.5)
        
        success_rate = successes / total
        assert success_rate >= 0.95, f"Only {success_rate*100}% succeeded"
    
    def test_server_doesnt_crash_on_bad_input(self, client):
        """Test server handles malformed input gracefully"""
        bad_inputs = [
            {"code": None, "language": "python"},
            {"code": "test", "language": None},
            {},
            {"code": "test", "language": "invalid_lang_xyz"},
            {"code": "x" * 100000, "language": "python"},  # Large but within limit
        ]
        
        for bad_input in bad_inputs:
            response = client.post("/api/format", json=bad_input)
            # Should either return 200 (with error) or 422 (validation error)
            assert response.status_code in [200, 422]
    
    @pytest.mark.slow
    def test_long_running_stability(self, client):
        """Test stability over 5 minutes of continuous requests"""
        start_time = time.time()
        request_count = 0
        failures = 0
        
        while time.time() - start_time < 60:  # Run for 1 minute in test
            response = client.post("/api/format", json={
                "code": f"def test_{request_count}():\n    pass",
                "language": "python"
            })
            if response.status_code != 200:
                failures += 1
            request_count += 1
            time.sleep(0.2)
        
        failure_rate = failures / request_count
        assert failure_rate < 0.05, f"Failure rate: {failure_rate*100}%"