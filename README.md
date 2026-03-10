# Code Formatter API

Professional code formatting service supporting Python, Go, and their frameworks.

## 🏗 Architecture

- **SOLID Principles**: Clean separation of concerns
- **Dependency Injection**: Testable and maintainable
- **Strategy Pattern**: Easy to add new formatters

## 🎯 Supported Languages

- Python (Black)
- Django, Flask, FastAPI (Python frameworks)
- Go, Golang (gofmt)

## 📋 API Endpoints

### 1. Format Code

**Request:**
```http
POST /api/format
Content-Type: application/json

{
  "code": "def hello( ):\n  print('world')",
  "language": "python"
}

Response - Success (200):

json
{
  "formatted_code": "def hello():\n    print('world')\n",
  "success": true,
  "error": null
}
Response - Syntax Error (200):

json
{
  "formatted_code": "def hello( ):\n  print('world')",
  "success": false,
  "error": "Cannot parse: 1:0: def hello( ):"
}
Response - Unsupported Language (200):

json
{
  "formatted_code": "original code",
  "success": false,
  "error": "Unsupported language: java"
}
Response - Invalid Request (422):

json
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
Response - Server Error (500):

json
{
  "success": false,
  "error": "Internal server error"
}
2. Get Supported Languages
Request:

http
GET /api/format/languages
Response (200):

json
{
  "languages": ["django", "fastapi", "flask", "go", "golang", "python"]
}
3. Health Check
Request:

http
GET /health
Response (200):

json
{
  "status": "healthy"
}
🚀 Development
Prerequisites
Python 3.12+

Go 1.21+ (for Go formatting)

Docker and Docker Compose (optional but recommended)

Git

Option 1: Native Development (No Docker)
bash
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

# Install Go (for Go formatting support)
# Ubuntu/Debian
sudo apt update && sudo apt install golang-go
# macOS
brew install go
# Windows (with Chocolatey)
choco install golang

# Start development server with hot reload
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Or use the provided script
./dev.sh native
Option 2: Docker Development (Recommended)
Using Docker Commands
bash
# Build the Docker image
docker build -t code-formatter-api:dev .

# Run with hot reload (mounts local code)
docker run -p 8000:8000 \
  -v $(pwd)/api:/app/api \
  -e ENVIRONMENT=development \
  code-formatter-api:dev \
  uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
Using Docker Compose (Easiest)
bash
# Start the API with hot reload
docker-compose up

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f api

# Rebuild and start
docker-compose up --build

# Stop all services
docker-compose down
Option 3: Development with Debugging
bash
# Using docker-compose with debug profile
docker-compose -f docker-compose.yml -f docker-compose.debug.yml up

# This enables:
# - Debugpy on port 5678
# - Hot reload
# - Volume mounts for all code changes
🏭 Production Deployment
Option 1: Docker Production Build
bash
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
Option 2: Docker Compose Production
bash
# Start with production configuration
docker-compose --profile production up -d

# This includes:
# - API service
# - Nginx reverse proxy
# - SSL/TLS support (if configured)
# - Auto-restart policy