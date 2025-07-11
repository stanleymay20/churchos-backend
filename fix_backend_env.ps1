# CHURCHOS™ Backend Environment Fix Script for Windows
# Sacred Operating System for Prophetic Church Governance

Write-Host "🕊️ CHURCHOS™ Backend Environment Setup" -ForegroundColor Green
Write-Host "Setting up sacred backend environment..." -ForegroundColor Yellow

# Check if Python is installed
try {
    $pythonVersion = python --version
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.11+ from https://python.org" -ForegroundColor Red
    exit 1
}

# Check if pip is available
try {
    $pipVersion = pip --version
    Write-Host "✅ pip found: $pipVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ pip not found. Please ensure pip is installed with Python" -ForegroundColor Red
    exit 1
}

# Create virtual environment
Write-Host "📦 Creating virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "⚠️  Virtual environment already exists. Removing..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force "venv"
}

python -m venv venv
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to create virtual environment" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Virtual environment created" -ForegroundColor Green

# Activate virtual environment
Write-Host "🔧 Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to activate virtual environment" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Virtual environment activated" -ForegroundColor Green

# Upgrade pip
Write-Host "⬆️  Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to upgrade pip" -ForegroundColor Red
    exit 1
}
Write-Host "✅ pip upgraded" -ForegroundColor Green

# Install core dependencies first
Write-Host "📦 Installing core dependencies..." -ForegroundColor Yellow

# Install FastAPI and Uvicorn first
pip install fastapi==0.109.0
pip install "uvicorn[standard]==0.27.0"

# Install database dependencies
pip install sqlalchemy==2.0.25
pip install psycopg2-binary==2.9.9 --only-binary :all:
pip install alembic==1.13.1

# Install authentication dependencies
pip install firebase-admin==6.4.0
pip install python-jose[cryptography]==3.3.0
pip install passlib[bcrypt]==1.7.4
pip install python-dotenv==1.0.0

# Install AI and OpenAI dependencies
pip install openai==1.12.0
pip install aiohttp==3.9.1

# Install WebRTC dependencies
pip install aiortc==1.5.0
pip install websockets==12.0

# Install data validation dependencies
pip install pydantic==2.5.3
pip install pydantic-settings==2.1.0

# Install HTTP client dependencies
pip install httpx==0.26.0
pip install requests==2.31.0

# Install CORS middleware
pip install fastapi-cors==0.0.6

# Install development dependencies
pip install pytest==7.4.4
pip install pytest-asyncio==0.23.2
pip install black==23.12.1
pip install isort==5.13.2

# Install utility dependencies
pip install python-dateutil==2.8.2
pip install pytz==2023.3
pip install python-multipart==0.0.6

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
    exit 1
}
Write-Host "✅ All dependencies installed successfully" -ForegroundColor Green

# Create .env file if it doesn't exist
if (-not (Test-Path ".env")) {
    Write-Host "📝 Creating .env file from template..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "✅ .env file created. Please edit with your configuration." -ForegroundColor Green
} else {
    Write-Host "✅ .env file already exists" -ForegroundColor Green
}

# Test uvicorn installation
Write-Host "🧪 Testing uvicorn installation..." -ForegroundColor Yellow
try {
    $uvicornVersion = uvicorn --version
    Write-Host "✅ uvicorn found: $uvicornVersion" -ForegroundColor Green
} catch {
    Write-Host "⚠️  uvicorn not found in PATH, but can be run with: python -m uvicorn" -ForegroundColor Yellow
}

# Create run script
Write-Host "📝 Creating run script..." -ForegroundColor Yellow
$runScript = @"
# CHURCHOS™ Backend Run Script
# Activate virtual environment and start server

Write-Host "🕊️ Starting CHURCHOS™ Backend..." -ForegroundColor Green

# Activate virtual environment
& ".\venv\Scripts\Activate.ps1"

# Start the server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
"@

$runScript | Out-File -FilePath "run_backend.ps1" -Encoding UTF8
Write-Host "✅ Run script created: run_backend.ps1" -ForegroundColor Green

# Display next steps
Write-Host ""
Write-Host "🎉 CHURCHOS™ Backend Environment Setup Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Edit .env file with your configuration" -ForegroundColor White
Write-Host "2. Run: .\run_backend.ps1" -ForegroundColor White
Write-Host "3. Or manually: python -m uvicorn app.main:app --reload" -ForegroundColor White
Write-Host "4. Access API at: http://localhost:8000" -ForegroundColor White
Write-Host "5. View docs at: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "📜 Sacred Technology for Prophetic Church Governance" -ForegroundColor Cyan
Write-Host "© 2024 CHURCHOS™. All rights reserved." -ForegroundColor Cyan 