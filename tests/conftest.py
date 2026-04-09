import pytest
from fastapi.testclient import TestClient
from api.middleware.rate_limit import rate_limiter
import os
import time

# Set development mode for testing
os.environ["ENVIRONMENT"] = "development"
os.environ["TESTING"] = "true"

from api.main import app

@pytest.fixture(scope="session")
def client():
    """Create test client with proper initialization."""
    time.sleep(1)
    test_client = TestClient(app)
    response = test_client.get("/ping")
    assert response.status_code == 200
    return test_client


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


@pytest.fixture(autouse=True)
def slow_down_tests():
    """Keep tests isolated from shared limiter state."""
    with rate_limiter.lock:
        rate_limiter.requests.clear()
        rate_limiter.requests_per_minute = 30
    yield
    time.sleep(0.1)
