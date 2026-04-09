import pytest
import time
import concurrent.futures
import os


class TestStability:
    
    @pytest.mark.slow
    def test_concurrent_requests(self, client, sample_python_code):
        """Test handling of concurrent requests"""
        def make_request():
            try:
                response = client.post("/api/format", json=sample_python_code)
                return response.status_code == 200
            except:
                return False
        
        # Use small number of concurrent requests to avoid overwhelming
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(make_request) for _ in range(5)]
            results = [f.result() for f in futures]
        
        success_rate = sum(results) / len(results)
        # Allow lower success rate if rate limiting kicks in
        assert success_rate >= 0.6, f"Success rate too low: {success_rate:.0%}"
    
    @pytest.mark.slow
    def test_memory_stability(self, client):
        """Test memory usage remains stable under load"""
        memory_readings = []
        
        # Make small number of requests
        for i in range(10):
            response = client.post("/api/format", json={
                "code": f"def test_{i}():\n    pass",
                "language": "python"
            })
            assert response.status_code == 200
            
            # Check memory every few requests
            if i % 3 == 0:
                try:
                    metrics_response = client.get("/metrics")
                    if metrics_response.status_code == 200:
                        metrics = metrics_response.json()
                        memory_readings.append(metrics.get("memory_mb", 0))
                except:
                    pass
            
            time.sleep(0.1)
        
        # If we got memory readings, check they're stable
        if len(memory_readings) >= 2:
            memory_growth = memory_readings[-1] - memory_readings[0]
            # Memory growth should be reasonable (less than 100MB)
            assert memory_growth < 100, f"Memory grew by {memory_growth:.1f}MB"
    
    @pytest.mark.slow
    def test_sustained_load(self, client):
        """Test service handles sustained load"""
        successes = 0
        failures = 0
        total = 10  # Small number for stability
        
        for i in range(total):
            try:
                response = client.post("/api/format", json={
                    "code": f"def test_{i}():\n    pass",
                    "language": "python"
                })
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        successes += 1
                    else:
                        failures += 1
                else:
                    failures += 1
            except:
                failures += 1
            
            time.sleep(0.15)  # Small delay between requests
        
        success_rate = successes / total
        # Allow some failures due to rate limiting or timeouts
        assert success_rate >= 0.7, f"Success rate too low: {success_rate:.0%}"
    
    def test_server_doesnt_crash_on_bad_input(self, client):
        """Test server handles invalid input gracefully"""
        bad_inputs = [
            {"code": None, "language": "python"},
            {"code": "test", "language": None},
            {},
            {"code": "test", "language": "invalid_lang_xyz"},
            {"code": "x" * 100000, "language": "python"},
            {"code": 12345, "language": "python"},  # Wrong type
            {"code": "", "language": ""},
            {"code": "def test(): pass", "language": "PYTHON"},  # Uppercase
        ]
        
        for i, bad_input in enumerate(bad_inputs):
            try:
                response = client.post("/api/format", json=bad_input)
                # Should return client error (4xx) or success with error field
                assert response.status_code in [200, 400, 413, 422], \
                    f"Input {i} returned {response.status_code}"
                
                if response.status_code == 200:
                    data = response.json()
                    assert "success" in data
            except Exception as e:
                # Any exception here means server crashed
                pytest.fail(f"Server crashed on input {i}: {bad_input} - Error: {e}")
    
    def test_timeout_handling(self, client):
        """Test that timeouts are handled gracefully"""
        # Create complex code that might take time to format
        complex_code = """
def complex_function():
    result = 0
    for i in range(1000):
        for j in range(1000):
            result += i * j
    return result
""" * 10  # Repeat to make it larger
        
        response = client.post("/api/format", json={
            "code": complex_code,
            "language": "python"
        })
        
        # Should complete or timeout gracefully
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        # Either success or clean timeout error
        if not data["success"]:
            assert "error" in data
            # Error message should indicate timeout or format failure
            error_msg = data["error"].lower()
            assert any(word in error_msg for word in ["timeout", "error", "fail"])
    
    def test_rapid_health_checks(self, client):
        """Test health endpoints under rapid requests"""
        endpoints = ["/ping", "/health", "/metrics", "/api/format/languages"]
        
        for endpoint in endpoints:
            for _ in range(5):
                response = client.get(endpoint)
                assert response.status_code in [200, 503], \
                    f"{endpoint} returned {response.status_code}"
                time.sleep(0.05)
    
    def test_recovery_after_errors(self, client):
        """Test service recovers after processing errors"""
        # Send malformed code
        for _ in range(3):
            response = client.post("/api/format", json={
                "code": "def broken",
                "language": "python"
            })
            assert response.status_code == 200
        
        # Should still handle valid requests
        time.sleep(0.5)
        response = client.post("/api/format", json={
            "code": "def working():\n    return True",
            "language": "python"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_mixed_language_requests(self, client):
        """Test alternating between different languages"""
        requests = [
            {"code": "def test(): pass", "language": "python"},
            {"code": "package main\nfunc main() {}", "language": "go"},
            {"code": "public class Test {}", "language": "java"},
            {"code": "def test2(): pass", "language": "python"},
        ]
        
        for req in requests:
            response = client.post("/api/format", json=req)
            assert response.status_code == 200
            data = response.json()
            assert "success" in data
            time.sleep(0.1)
    
    @pytest.mark.skipif(os.getenv("CI") == "true", reason="Skipped in CI environment")
    @pytest.mark.timeout(60)
    def test_long_running_stability(self, client):
        """Test stability over longer period (skipped in CI)"""
        start_time = time.time()
        request_count = 0
        error_count = 0
        
        # Run for up to 30 seconds
        while time.time() - start_time < 30:
            try:
                response = client.post("/api/format", json={
                    "code": f"def test_{request_count}():\n    pass",
                    "language": "python"
                })
                if response.status_code != 200:
                    error_count += 1
                else:
                    data = response.json()
                    if not data.get("success"):
                        error_count += 1
            except:
                error_count += 1
            
            request_count += 1
            time.sleep(0.2)
        
        error_rate = error_count / request_count if request_count > 0 else 1
        assert error_rate < 0.3, f"Error rate too high: {error_rate:.0%}"
        assert request_count > 50, f"Only made {request_count} requests"
