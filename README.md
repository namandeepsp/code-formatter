# Code Formatter API

Professional code formatting service supporting Python, Go, and Java.

## 🏗 Architecture

- **SOLID Principles**: Clean separation of concerns
- **Dependency Injection**: Testable and maintainable
- **Strategy Pattern**: Easy to add new formatters
- **Consistent API Response**: Standardized response format across all endpoints

## 🎯 Supported Languages

- Python
- Go
- Java

## 📋 API Endpoints

### Authentication

All endpoints (except `/health`) require the `X-API-Key` header:

```
X-API-Key: your-secret-api-key
```

**Development Mode**: If `ENVIRONMENT=development`, API key validation is skipped.

---

### 1. Format Code

**Endpoint:** `POST /api/format`

**Description:** Formats source code according to language-specific standards.

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

**Response - Syntax Error (200):**
```json
{
  "success": false,
  "error": "Cannot format: invalid syntax",
  "data": {
    "formatted_code": "def hello( ):\n  print('world')"
  }
}
```

**Response - Unsupported Language (200):**
```json
{
  "success": false,
  "error": "Unsupported language: rust",
  "data": {
    "formatted_code": "original code"
  }
}
```

**Response - Invalid Request (422):**
```json
{
  "success": false,
  "error": "Invalid request format",
  "details": [
    {
      "loc": ["body", "language"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**Response - Unauthorized (401):**
```json
{
  "detail": "Unauthorized access"
}
```

**Response - Server Error (500):**
```json
{
  "success": false,
  "error": "Internal server error"
}
```

---

### 2. Get Supported Languages

**Endpoint:** `GET /api/format/languages`

**Description:** Returns list of all supported programming languages.

**Headers:**
```
X-API-Key: your-secret-api-key
```

**Request Body:** None

**Response - Success (200):**
```json
{
  "success": true,
  "error": null,
  "data": {
    "languages": ["go", "java", "python"]
  }
}
```

**Response - Error (200):**
```json
{
  "success": false,
  "error": "Service unavailable",
  "data": null
}
```

**Response - Unauthorized (401):**
```json
{
  "detail": "Unauthorized access"
}
```

---

### 3. Detect Language

**Endpoint:** `POST /api/format/detect`

**Description:** Detects the programming language of provided code.

**Headers:**
```
Content-Type: application/json
X-API-Key: your-secret-api-key
```

**Request Body:**
```json
{
  "code": "public class Hello {\n  public static void main(String[] args) {\n    System.out.println(\"Hello\");\n  }\n}"
}
```

**Response - Success (200):**
```json
{
  "success": true,
  "error": null,
  "data": {
    "language": "java",
    "confidence": "high"
  }
}
```

**Response - Unknown Language (200):**
```json
{
  "success": true,
  "error": null,
  "data": {
    "language": null,
    "confidence": "unknown"
  }
}
```

**Response - Error (200):**
```json
{
  "success": false,
  "error": "Processing error",
  "data": null
}
```

**Response - Unauthorized (401):**
```json
{
  "detail": "Unauthorized access"
}
```

---

### 4. Health Check

**Endpoint:** `GET /health`

**Description:** Checks if the API is running and healthy.

**Headers:** None

**Request Body:** None

**Response - Success (200):**
```
OK
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

- **success**: `true` if operation succeeded, `false` otherwise
- **error**: Error message if operation failed, `null` if successful
- **data**: Response data object if successful, `null` if failed

---

## 🚀 Development

### Prerequisites

- Python 3.12+
- Go 1.21+ (for Go formatting)
- Java 11+ (for Java formatting)
- Docker and Docker Compose (optional but recommended)

### Option 1: Native Development (No Docker)

```bash
# Clone the repository
git clone https://github.com/namandeepsp/code-formatter.git
cd code-formatter

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
# .\venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Install Go
# Ubuntu/Debian
sudo apt update && sudo apt install golang-go
# macOS
brew install go

# Install Java
# Ubuntu/Debian
sudo apt install default-jdk default-jre
# macOS
brew install openjdk

# Download Google Java Format
curl -L https://github.com/google/google-java-format/releases/download/v1.17.0/google-java-format-1.17.0-all-deps.jar -o google-java-format.jar

# Start development server with hot reload
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### Option 2: Docker Development (Recommended)

```bash
# Build and run with Docker Compose
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop all services
docker-compose down
```

---

## 🏭 Production Deployment

### Option 1: Docker Production Build

```bash
# Build optimized production image
docker build -t code-formatter-api:prod .

# Run production container
docker run -d -p 8000:8000 \
  --name code-formatter \
  --restart unless-stopped \
  -e ENVIRONMENT=production \
  -e API_KEY=your-secret-key \
  code-formatter-api:prod

# Check logs
docker logs -f code-formatter

# Stop container
docker stop code-formatter
```

### Option 2: Deploy to Render

1. Push code to GitHub
2. Go to [render.com](https://render.com)
3. Create new Web Service → Connect GitHub repo
4. Configure:
   - **Runtime**: Docker
   - **Environment Variables**:
     - `ENVIRONMENT`: production
     - `API_KEY`: your-secret-key
5. Deploy

Your API will be live at `https://your-service-name.onrender.com`

---

## 🔐 Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ENVIRONMENT` | development | Set to `production` to enforce API key validation |
| `API_KEY` | (none) | Secret API key for authentication (required in production) |

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

### Format Go Code

```bash
curl -X POST http://localhost:8000/api/format \
  -H "Content-Type: application/json" \
  -H "X-API-Key: test-key" \
  -d '{
    "code": "package main\nimport \"fmt\"\nfunc main(  ) {\n  fmt.Println(  \"Hello\"  )\n}",
    "language": "go"
  }'
```

### Format Java Code

```bash
curl -X POST http://localhost:8000/api/format \
  -H "Content-Type: application/json" \
  -H "X-API-Key: test-key" \
  -d '{
    "code": "public class Hello{public static void main(String[]args){System.out.println(\"Hello\");}}",
    "language": "java"
  }'
```

### Get Supported Languages

```bash
curl -X GET http://localhost:8000/api/format/languages \
  -H "X-API-Key: test-key"
```

### Detect Language

```bash
curl -X POST http://localhost:8000/api/format/detect \
  -H "Content-Type: application/json" \
  -H "X-API-Key: test-key" \
  -d '{
    "code": "def hello():\n    print(\"world\")"
  }'
```

### Health Check

```bash
curl http://localhost:8000/health
```

---

## 🛠 Tech Stack

- **Framework**: FastAPI
- **Server**: Uvicorn
- **Python Formatter**: Black
- **Go Formatter**: gofmt
- **Java Formatter**: Google Java Format
- **Validation**: Pydantic
- **Containerization**: Docker

---

## 📄 License

MIT License
