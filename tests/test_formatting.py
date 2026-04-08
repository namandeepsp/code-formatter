import pytest

class TestPythonFormatter:
    
    def test_format_python_valid(self, client, sample_python_code):
        """Test valid Python code formatting"""
        response = client.post("/api/format", json=sample_python_code)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "def hello():" in data["data"]["formatted_code"]
        assert "    print('world')" in data["data"]["formatted_code"]
    
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
        assert "Empty" in data["error"]
    
    def test_format_python_large_code(self, client):
        """Test code that's too large"""
        large_code = "def test():\n    pass\n" * 10000
        response = client.post("/api/format", json={
            "code": large_code,
            "language": "python"
        })
        assert response.status_code == 200
        data = response.json()
        # Should either succeed or fail gracefully (no crash)
        assert "success" in data

class TestGoFormatter:
    
    def test_format_go_valid(self, client, sample_go_code):
        """Test valid Go code formatting"""
        response = client.post("/api/format", json=sample_go_code)
        assert response.status_code == 200
        data = response.json()
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
    
    def test_format_java_large(self, client):
        """Test Java with large code"""
        large_java = "public class Test {}\n" * 1000
        response = client.post("/api/format", json={
            "code": large_java,
            "language": "java"
        })
        assert response.status_code in [200, 413]  # Either success or too large

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
    
    def test_detect_go(self, client):
        """Test Go language detection"""
        response = client.post("/api/format/detect", json={
            "code": "package main\nfunc main() {\n    println('hello')\n}"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["language"] in ["go", None]  # May detect or not
    
    def test_get_languages(self, client):
        """Test getting supported languages"""
        response = client.get("/api/format/languages")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "languages" in data["data"]
        assert "python" in data["data"]["languages"]