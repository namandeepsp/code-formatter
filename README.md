# Code Formatter API

Professional code formatting service supporting Python, Go, and their frameworks.

## Architecture

- **SOLID Principles**: Clean separation of concerns
- **Dependency Injection**: Testable and maintainable
- **Strategy Pattern**: Easy to add new formatters

## Supported Languages

- Python (Black)
- Django, Flask, FastAPI (Python frameworks)
- Go, Golang (gofmt)

## API Endpoints

### 1. Format Code

**Request:**
```http
POST /api/format
Content-Type: application/json

{
  "code": "def hello( ):\n  print('world')",
  "language": "python"
}
```

**Response - Success (200):**
```json
{
  "formatted_code": "def hello():\n    print('world')\n",
  "success": true,
  "error": null
}
```

**Response - Syntax Error (200):**
```json
{
  "formatted_code": "def hello( ):\n  print('world')",
  "success": false,
  "error": "Cannot parse: 1:0: def hello( ):"
}
```

**Response - Unsupported Language (200):**
```json
{
  "formatted_code": "original code",
  "success": false,
  "error": "Unsupported language: java"
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

**Response - Server Error (500):**
```json
{
  "success": false,
  "error": "Internal server error"
}
```

### 2. Get Supported Languages

**Request:**
```http
GET /api/format/languages
```

**Response (200):**
```json
{
  "languages": ["django", "fastapi", "flask", "go", "golang", "python"]
}
```

### 3. Health Check

**Request:**
```http
GET /health
```

**Response (200):**
```json
{
  "status": "healthy"
}
```

## Local Development

```bash
# Create virtual environment
python3 -m venv venv

# Install dependencies
venv/bin/pip install -r requirements.txt

# Install Go (for Go formatting support)
sudo apt install golang-go

# Start server
venv/bin/uvicorn api.main:app --reload
```

API Documentation: http://localhost:8000/docs

## Deploy to Vercel

```bash
vercel deploy
```

## Adding New Formatters

1. Create formatter class in `api/formatters/`
2. Extend `CodeFormatter` base class
3. Register in `api/dependencies.py`
