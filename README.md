Here's your **updated README** with all the new features (rate limiting, health checks, testing, CI/CD, and stability fixes):

---

```markdown
# Code Formatter API

Professional code formatting service supporting Python, Go, and Java with production-ready stability features.

## ✨ Features

- **Multi-language Support**: Python, Go, Java
- **Rate Limiting**: 30 requests per minute per IP
- **Memory Leak Prevention**: Subprocess pooling and temp file cleanup
- **Self-Healing**: Automatic JAR download if missing
- **Health Monitoring**: Detailed health checks and lightweight ping endpoint
- **CI/CD**: GitHub Actions + Render auto-deploy with test gatekeeping
- **Testing**: 30+ integration and stability tests

## 🏗 Architecture

- **SOLID Principles**: Clean separation of concerns
- **Dependency Injection**: Testable and maintainable
- **Strategy Pattern**: Easy to add new formatters
- **Consistent API Response**: Standardized response format across all endpoints
- **Rate Limiting**: In-memory rate limiter (30 req/min)
- **Process Pool**: Managed subprocesses with automatic cleanup

## 🎯 Supported Languages

- Python
- Go
- Java

## 📋 API Endpoints

### Authentication

All endpoints (except `/health`, `/ping`, `/metrics`) require the `X-API-Key` header:

```
X-API-Key: your-secret-api-key
```

**Development Mode**: If `ENVIRONMENT=development`, API key validation is skipped.

---

### 1. Format Code

**Endpoint:** `POST /api/format`

**Description:** Formats source code according to language-specific standards.

**Rate Limit:** 30 requests per minute

**Headers:**
```
Content-Type: application/json
X-API-Key: your-secret-api-key
```

**Request Body:**
```json
{
  "code": "def hello( ):\n  print('world')",
  "language": "python"
}
```

**Response - Success (200):**
```json
{
  "success": true,
  "error": null,
  "data": {
    "formatted_code": "def hello():\n    print('world')\n"
  }
}
```

**Response - Rate Limited (429):**
```json
{
  "detail": "Rate limit exceeded. Max 30 requests per minute"
}
```

---

### 2. Get Supported Languages

**Endpoint:** `GET /api/format/languages`

**Description:** Returns list of all supported programming languages.

---

### 3. Detect Language

**Endpoint:** `POST /api/format/detect`

**Description:** Detects the programming language of provided code.

---

### 4. Health Check (Detailed)

**Endpoint:** `GET /health`

**Description:** Returns detailed health status including memory usage and formatter availability.

**Response (200):**
```json
{
  "status": "healthy",
  "timestamp": 5192.585,
  "memory_usage_mb": 68.94,
  "formatters": {
    "available": ["go", "java", "python"],
    "count": 3,
    "python_working": true
  }
}
```

---

### 5. Ping (Lightweight)

**Endpoint:** `GET /ping`

**Description:** Ultra-light endpoint for cron jobs and keep-alive. Returns just "pong".

**Response (200):**
```
pong
```

---

### 6. Metrics

**Endpoint:** `GET /metrics`

**Description:** Returns memory and CPU metrics for monitoring.

**Response (200):**
```json
{
  "memory_mb": 68.94,
  "cpu_percent": 2.5,
  "uptime_seconds": 3600
}
```

---

## 📊 Response Format

All API responses follow a consistent format:

```json
{
  "success": boolean,
  "error": string | null,
  "data": object | null
}
```

---

## 🚀 Development

### Prerequisites

- Python 3.12+
- Go 1.21+ (for Go formatting)
- Java 11+ (for Java formatting)
- Docker and Docker Compose (optional)

### Option 1: Native Development

```bash
# Clone the repository
git clone https://github.com/namandeepsp/code-formatter.git
cd code-formatter

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Download Google Java Format
curl -L https://github.com/google/google-java-format/releases/download/v1.17.0/google-java-format-1.17.0-all-deps.jar -o google-java-format.jar

# Start development server
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### Option 2: Docker Development (Recommended)

```bash
# Build and run
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop
docker-compose down
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=api --cov-report=term-missing

# Run specific test file
pytest tests/test_health.py -v

# Skip slow tests
pytest tests/ -v -m "not slow"
```

---

## 🔄 CI/CD Pipeline

This project uses **GitHub Actions** for continuous integration and **Render** for deployment.

### How It Works:

1. **Push code** to GitHub
2. **GitHub Actions** runs the test suite automatically
3. **If tests pass** → Render deploys the new version
4. **If tests fail** → Render keeps running the old version

### GitHub Actions Workflow:

```yaml
name: Test Code Formatter
on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest tests/ -v
```

### Render Configuration:

Set **Auto-Deploy** → **"After CI Checks Pass"** in Render dashboard.

---

## 🏭 Production Deployment

### Deploy to Render

1. Push code to GitHub
2. Go to [render.com](https://render.com)
3. Create new Web Service → Connect GitHub repo
4. Configure:
   - **Runtime**: Docker
   - **Auto-Deploy**: After CI Checks Pass
   - **Environment Variables**:
     - `ENVIRONMENT`: production
     - `API_KEY`: your-secret-key
5. Deploy

### Keep-Alive with Cron Job

Use the lightweight `/ping` endpoint to prevent Render free tier spin-down:

```bash
# Every 2 minutes
*/2 * * * * curl -s -o /dev/null -w "%{http_code}\n" https://your-service.onrender.com/ping
```

---

## 🔐 Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ENVIRONMENT` | development | Set to `production` to enforce API key validation |
| `API_KEY` | (none) | Secret API key (required in production) |
| `JAVA_OPTS` | -Xmx256m | Java memory limit |

---

## 📝 Example Usage

### Format Python Code

```bash
curl -X POST http://localhost:8000/api/format \
  -H "Content-Type: application/json" \
  -H "X-API-Key: test-key" \
  -d '{
    "code": "def hello( ):\n  print(\"world\")",
    "language": "python"
  }'
```

### Check Health

```bash
# Detailed health check
curl http://localhost:8000/health

# Lightweight ping (for cron)
curl http://localhost:8000/ping

# Metrics
curl http://localhost:8000/metrics
```

---

## 🛠 Tech Stack

| Component | Technology |
|-----------|------------|
| **Framework** | FastAPI |
| **Server** | Uvicorn |
| **Python Formatter** | Black + isort |
| **Go Formatter** | gofmt |
| **Java Formatter** | Google Java Format |
| **Validation** | Pydantic |
| **Testing** | pytest + pytest-cov |
| **CI/CD** | GitHub Actions |
| **Deployment** | Render (Docker) |
| **Containerization** | Docker |

---

## 📁 Project Structure

```
code-formatter/
├── api/
│   ├── formatters/       # Python, Go, Java formatters
│   ├── middleware/       # Auth + rate limiting
│   ├── models/           # Pydantic models
│   ├── routes/           # API endpoints
│   ├── services/         # Business logic + process pool
│   ├── dependencies.py   # DI container
│   └── main.py           # FastAPI app
├── tests/                # 30+ integration tests
├── .github/workflows/    # GitHub Actions CI
├── dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## 📄 License

MIT License

## 🙏 Acknowledgments

- Built with FastAPI
- Formatters: Black, gofmt, Google Java Format
- Deployed on Render
- CI/CD with GitHub Actions

---

**Live Demo:** [https://code-formatter-4uzi.onrender.com](https://code-formatter-4uzi.onrender.com)
```

---

## ✅ **Summary of Changes Made**

| Section | What Was Added |
|---------|----------------|
| **Features** | Rate limiting, memory leak prevention, self-healing, monitoring |
| **API Endpoints** | `/ping`, `/metrics`, rate limit response (429) |
| **Testing** | Complete testing section with commands |
| **CI/CD** | GitHub Actions + Render "After CI Checks Pass" workflow |
| **Keep-Alive** | Cron job configuration using `/ping` |
| **Project Structure** | Directory tree showing new files |
| **Environment Variables** | Added `JAVA_OPTS` |
| **Live Demo** | Link to your Render service |

**Ready to commit and push!** 🚀