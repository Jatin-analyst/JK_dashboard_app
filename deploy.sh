#!/bin/bash

# Air Quality Dashboard Deployment Script
# This script prepares and deploys the dashboard

set -e  # Exit on any error

echo "🚀 Air Quality Dashboard Deployment Script"
echo "=========================================="

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command_exists python3; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

if ! command_exists pip; then
    echo "❌ pip is required but not installed."
    exit 1
fi

echo "✅ Prerequisites check passed"

# Parse command line arguments
DEPLOYMENT_TYPE=${1:-local}
PORT=${2:-8501}

case $DEPLOYMENT_TYPE in
    "local")
        echo "🏠 Deploying locally..."
        
        # Install dependencies
        echo "📦 Installing dependencies..."
        pip install -r requirements.txt
        
        # Run the dashboard
        echo "🌟 Starting dashboard on port $PORT..."
        streamlit run app.py --server.port=$PORT --server.address=localhost
        ;;
        
    "production")
        echo "🏭 Deploying for production..."
        
        # Install production dependencies
        echo "📦 Installing production dependencies..."
        pip install -r requirements-prod.txt
        
        # Run with production settings
        echo "🌟 Starting dashboard in production mode on port $PORT..."
        streamlit run app.py \
            --server.port=$PORT \
            --server.address=0.0.0.0 \
            --server.headless=true \
            --server.enableCORS=false
        ;;
        
    "docker")
        echo "🐳 Deploying with Docker..."
        
        if ! command_exists docker; then
            echo "❌ Docker is required but not installed."
            exit 1
        fi
        
        # Build and run with Docker Compose
        echo "🔨 Building Docker image..."
        docker-compose build
        
        echo "🌟 Starting dashboard with Docker Compose..."
        docker-compose up -d
        
        echo "✅ Dashboard is running at http://localhost:8501"
        echo "📊 View logs with: docker-compose logs -f"
        echo "🛑 Stop with: docker-compose down"
        ;;
        
    "check")
        echo "🔍 Running deployment checks..."
        
        # Check data files
        echo "📁 Checking data files..."
        if [ ! -f "data/city_day.csv" ]; then
            echo "⚠️  Warning: data/city_day.csv not found"
        else
            echo "✅ data/city_day.csv found"
        fi
        
        if [ ! -f "data/station_day.csv" ]; then
            echo "⚠️  Warning: data/station_day.csv not found"
        else
            echo "✅ data/station_day.csv found"
        fi
        
        if [ ! -f "data/stations.csv" ]; then
            echo "⚠️  Warning: data/stations.csv not found"
        else
            echo "✅ data/stations.csv found"
        fi
        
        # Check Python syntax
        echo "🐍 Checking Python syntax..."
        python3 -m py_compile app.py
        echo "✅ app.py syntax is valid"
        
        # Check imports
        echo "📦 Checking imports..."
        python3 -c "
import sys
import os
sys.path.append('src')
try:
    from data.real_data_processor import RealDataProcessor
    from ui.sidebar_filters import create_sidebar_filters
    from ui.dashboard_layout import create_dashboard_layout
    print('✅ All imports successful')
except ImportError as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)
"
        
        echo "✅ All deployment checks passed!"
        ;;
        
    *)
        echo "❌ Unknown deployment type: $DEPLOYMENT_TYPE"
        echo ""
        echo "Usage: $0 [deployment_type] [port]"
        echo ""
        echo "Deployment types:"
        echo "  local      - Run locally for development (default)"
        echo "  production - Run in production mode"
        echo "  docker     - Deploy with Docker Compose"
        echo "  check      - Run deployment checks"
        echo ""
        echo "Examples:"
        echo "  $0 local 8501"
        echo "  $0 production 80"
        echo "  $0 docker"
        echo "  $0 check"
        exit 1
        ;;
esac