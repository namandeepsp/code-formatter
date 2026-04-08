import pytest
from fastapi.testclient import TestClient
from api.main import app
import os

# Set development mode for testing
os.environ["ENVIRONMENT"] = "development"

@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)

@pytest.fixture
def sample_python_code():
    return {
        "code": "def hello( ):\n  print('world')",
        "language": "python"
    }

@pytest.fixture
def sample_go_code():
    return {
        "code": "package main\nfunc main(  ) {\n  println(  \"hello\"  )\n}",
        "language": "go"
    }

@pytest.fixture
def sample_java_code():
    return {
        "code": "public class Test{public static void main(String[]args){System.out.println(\"hi\");}}",
        "language": "java"
    }

@pytest.fixture
def sample_malformed_code():
    return {
        "code": "def broken( )\n  print('missing colon')",
        "language": "python"
    }