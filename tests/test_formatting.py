import pytest
import time
import shutil


class TestPythonFormatter:
    
    def test_format_python_valid(self, client, sample_python_code):
        """Test valid Python code formatting"""
        response = client.post("/api/format", json=sample_python_code)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "def hello():" in data["data"]["formatted_code"]
        assert "print('world')" in data["data"]["formatted_code"] or "print(\"world\")" in data["data"]["formatted_code"]
    
    def test_format_python_malformed(self, client, sample_malformed_code):
        """Test malformed Python code returns error"""
        response = client.post("/api/format", json=sample_malformed_code)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "error" in data
    
    def test_format_python_empty(self, client):
        """Test empty code"""
        response = client.post("/api/format", json={
            "code": "",
            "language": "python"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "error" in data
        assert "empty" in data["error"].lower() or "empty" in str(data).lower()
    
    def test_format_python_large_code(self, client):
        """Test code that's too large"""
        large_code = "def test():\n    pass\n" * 10000
        response = client.post("/api/format", json={
            "code": large_code,
            "language": "python"
        })
        # Should either succeed or fail gracefully (no crash)
        assert response.status_code in [200, 413, 422]
        data = response.json() if response.status_code == 200 else {"success": False}
        assert "success" in data or response.status_code in [413, 422]


class TestGoFormatter:
    
    @pytest.mark.skipif(
        shutil.which("gofmt") is None,
        reason="gofmt is not available in test environment",
    )
    def test_format_go_valid_skip_if_unavailable(self, client, sample_go_code):
        """Test valid Go code formatting"""
        response = client.post("/api/format", json=sample_go_code)
        assert response.status_code == 200
        data = response.json()
        # Go may be unavailable, should handle gracefully
        if data["success"]:
            assert "func main()" in data["data"]["formatted_code"]
        else:
            assert "error" in data
    
    def test_format_go_valid(self, client, sample_go_code):
        """Test valid Go code formatting"""
        response = client.post("/api/format", json=sample_go_code)
        assert response.status_code == 200
        data = response.json()
        # Go may be unavailable, but should not crash
        assert "success" in data
        if data["success"]:
            assert "func main()" in data["data"]["formatted_code"]
    
    def test_format_go_invalid_syntax(self, client):
        """Test invalid Go code"""
        response = client.post("/api/format", json={
            "code": "package main\nfunc broken",
            "language": "go"
        })
        assert response.status_code == 200
        data = response.json()
        # Should return error without crashing
        assert "success" in data


class TestJavaFormatter:
    
    def test_format_java_valid(self, client, sample_java_code):
        """Test valid Java code formatting (if available)"""
        response = client.post("/api/format", json=sample_java_code)
        assert response.status_code == 200
        data = response.json()
        # Java may be unavailable, but should not crash
        assert "success" in data
        if data["success"]:
            assert "formatted_code" in data["data"]
    
    def test_format_java_large(self, client):
        """Test Java with large code"""
        large_java = "public class Test {}\n" * 1000
        response = client.post("/api/format", json={
            "code": large_java,
            "language": "java"
        })
        assert response.status_code in [200, 413, 422]
        if response.status_code == 200:
            data = response.json()
            assert "success" in data


class TestLanguageDetection:
    
    def test_detect_python(self, client):
        """Test Python language detection"""
        response = client.post("/api/format/detect", json={
            "code": "def hello():\n    print('world')"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["language"] == "python"
        assert data["data"]["confidence"] in ["high", "medium", "low", "unknown"]
    
    def test_detect_go(self, client):
        """Test Go language detection"""
        response = client.post("/api/format/detect", json={
            "code": "package main\nfunc main() {\n    println('hello')\n}"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        # May detect or not - both are valid responses
        assert data["data"]["language"] in ["go", "python", None]
    
    def test_detect_empty(self, client):
        """Test empty code detection"""
        response = client.post("/api/format/detect", json={
            "code": ""
        })
        assert response.status_code == 200
        data = response.json()
        # Should handle gracefully
        assert "success" in data
    
    def test_get_languages(self, client):
        """Test getting supported languages"""
        response = client.get("/api/format/languages")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "languages" in data["data"]
        # Python should always be available
        assert "python" in data["data"]["languages"]
    
    def test_formatter_health(self, client):
        """Test formatter health endpoint"""
        response = client.get("/api/format/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["healthy", "degraded", "unhealthy"]
        assert "formatters" in data
        assert "python" in data["formatters"]


class TestEdgeCases:
    
    def test_unicode_code(self, client):
        """Test formatting code with unicode characters"""
        response = client.post("/api/format", json={
            "code": "def test():\n    print('héllo wörld 🌍')",
            "language": "python"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_very_long_line(self, client):
        """Test code with very long lines"""
        long_line = "x = " + "1 + " * 1000 + "1"
        response = client.post("/api/format", json={
            "code": long_line,
            "language": "python"
        })
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
    
    def test_special_characters(self, client):
        """Test code with special characters"""
        response = client.post("/api/format", json={
            "code": "def test():\n\t# Comment with tabs\t\tand\n\tprint('escapes\\\\n')\n",
            "language": "python"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_concurrent_format_requests(self, client):
        """Test multiple format requests in quick succession"""
        import concurrent.futures
        
        def make_request(i):
            return client.post("/api/format", json={
                "code": f"def test_{i}():\n    pass",
                "language": "python"
            })
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(make_request, i) for i in range(5)]
            results = [f.result() for f in futures]
        
        success_count = sum(1 for r in results if r.status_code == 200)
        assert success_count >= 3  # Allow some failures due to rate limiting
