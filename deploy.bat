@echo off
REM Air Quality Dashboard Deployment Script for Windows
REM This script prepares and deploys the dashboard

echo 🚀 Air Quality Dashboard Deployment Script
echo ==========================================

REM Parse command line arguments
set DEPLOYMENT_TYPE=%1
set PORT=%2

if "%DEPLOYMENT_TYPE%"=="" set DEPLOYMENT_TYPE=local
if "%PORT%"=="" set PORT=8501

if "%DEPLOYMENT_TYPE%"=="local" goto local
if "%DEPLOYMENT_TYPE%"=="production" goto production
if "%DEPLOYMENT_TYPE%"=="docker" goto docker
if "%DEPLOYMENT_TYPE%"=="check" goto check
goto usage

:local
echo 🏠 Deploying locally...

REM Install dependencies
echo 📦 Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install dependencies
    exit /b 1
)

REM Run the dashboard
echo 🌟 Starting dashboard on port %PORT%...
streamlit run app.py --server.port=%PORT% --server.address=localhost
goto end

:production
echo 🏭 Deploying for production...

REM Install production dependencies
echo 📦 Installing production dependencies...
pip install -r requirements-prod.txt
if errorlevel 1 (
    echo ❌ Failed to install production dependencies
    exit /b 1
)

REM Run with production settings
echo 🌟 Starting dashboard in production mode on port %PORT%...
streamlit run app.py --server.port=%PORT% --server.address=0.0.0.0 --server.headless=true --server.enableCORS=false
goto end

:docker
echo 🐳 Deploying with Docker...

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is required but not installed.
    exit /b 1
)

REM Build and run with Docker Compose
echo 🔨 Building Docker image...
docker-compose build
if errorlevel 1 (
    echo ❌ Failed to build Docker image
    exit /b 1
)

echo 🌟 Starting dashboard with Docker Compose...
docker-compose up -d
if errorlevel 1 (
    echo ❌ Failed to start Docker containers
    exit /b 1
)

echo ✅ Dashboard is running at http://localhost:8501
echo 📊 View logs with: docker-compose logs -f
echo 🛑 Stop with: docker-compose down
goto end

:check
echo 🔍 Running deployment checks...

REM Check data files
echo 📁 Checking data files...
if exist "data\city_day.csv" (
    echo ✅ data/city_day.csv found
) else (
    echo ⚠️  Warning: data/city_day.csv not found
)

if exist "data\station_day.csv" (
    echo ✅ data/station_day.csv found
) else (
    echo ⚠️  Warning: data/station_day.csv not found
)

if exist "data\stations.csv" (
    echo ✅ data/stations.csv found
) else (
    echo ⚠️  Warning: data/stations.csv not found
)

REM Check Python syntax
echo 🐍 Checking Python syntax...
python -m py_compile app.py
if errorlevel 1 (
    echo ❌ app.py has syntax errors
    exit /b 1
)
echo ✅ app.py syntax is valid

echo ✅ All deployment checks passed!
goto end

:usage
echo ❌ Unknown deployment type: %DEPLOYMENT_TYPE%
echo.
echo Usage: %0 [deployment_type] [port]
echo.
echo Deployment types:
echo   local      - Run locally for development (default)
echo   production - Run in production mode
echo   docker     - Deploy with Docker Compose
echo   check      - Run deployment checks
echo.
echo Examples:
echo   %0 local 8501
echo   %0 production 80
echo   %0 docker
echo   %0 check
exit /b 1

:end
echo.
echo 🎉 Deployment script completed!