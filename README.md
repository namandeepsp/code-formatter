# Code Formatter API

FastAPI service to format Python, Go, and Java code with health checks, metrics, and request rate limiting.

## Features
- Python formatting via `black` + `isort`
- Go formatting via `gofmt` (if available)
- Java formatting via `google-java-format.jar` (if available)
- Language detection endpoint
- Rate limiting middleware
- Health and metrics endpoints
- Automated test suite (formatting, stability, rate-limit, health)

## API Endpoints
- `POST /api/format` - format code
- `POST /api/format/detect` - detect language
- `GET /api/format/languages` - list supported languages
- `GET /api/format/health` - formatter health details
- `GET /health` - service health summary
- `GET /metrics` - process metrics
- `GET /ping` - lightweight liveness check

## Response Contract
Most formatter failures are returned as:
- HTTP `200`
- `{"success": false, "error": "..."}`

Input/validation and middleware errors may return `4xx/5xx`.

## Local Development
```bash
git clone https://github.com/namandeepsp/code-formatter.git
cd code-formatter
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

## Docker
```bash
docker-compose up --build
```

```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## Tests
```bash
pytest -v -s
```

```bash
pytest tests/ --cov=api --cov-report=term-missing
```

## Environment Variables
- `ENVIRONMENT` (`development` or `production`)
- `API_KEY` (required in production)
- `TESTING` (`true` in tests)
- `FORMATTER_TIMEOUT` (default formatter timeout in seconds)
- `JAVA_OPTS` (optional JVM flags)

## CI/CD
GitHub Actions workflow: `.github/workflows/test.yml`
- Builds Docker image
- Runs container
- Executes integration checks against running service

Note: Full repo `pytest` suite can still be run locally or in CI as a separate job if desired.

## Notes on Optional Formatters
- If `gofmt` is not installed, Go formatting returns a graceful error.
- If Java formatter dependencies are unavailable, Java formatting degrades gracefully.

## License
MIT
