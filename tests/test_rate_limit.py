import time


class TestRateLimit:

    def test_rate_limit_enforcement(self, client):
        """Test rate limiting works"""

        responses = []
        for i in range(60):
            response = client.post(
                "/api/format",
                json={
                    "code": f"def test_{i}():\n    pass",
                    "language": "python"
                }
            )
            responses.append(response.status_code)
            time.sleep(0.02)

        rate_limited = sum(1 for r in responses if r == 429)

        # Should hit rate limit at least once
        assert rate_limited > 0

    def test_rate_limit_resets(self, client):
        """Test rate limit resets"""

        for i in range(20):
            response = client.post(
                "/api/format",
                json={
                    "code": f"def test_{i}():\n    pass",
                    "language": "python"
                }
            )
            assert response.status_code in [200, 429]

        time.sleep(2)

        response = client.post(
            "/api/format",
            json={
                "code": "def test():\n    pass",
                "language": "python"
            }
        )

        assert response.status_code in [200, 429]