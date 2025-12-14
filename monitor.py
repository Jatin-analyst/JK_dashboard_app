#!/usr/bin/env python3
"""
Production monitoring script for the Air Quality Dashboard.
Checks application health and performance metrics.
"""

import requests
import time
import sys
import json
from datetime import datetime


def check_health(url="http://localhost:8501"):
    """Check if the dashboard is responding"""
    try:
        # Check main page
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return True, "Dashboard is responding"
        else:
            return False, f"Dashboard returned status code: {response.status_code}"
    except requests.exceptions.RequestException as e:
        return False, f"Dashboard is not responding: {str(e)}"


def check_streamlit_health(url="http://localhost:8501"):
    """Check Streamlit health endpoint"""
    try:
        health_url = f"{url}/_stcore/health"
        response = requests.get(health_url, timeout=5)
        if response.status_code == 200:
            return True, "Streamlit health check passed"
        else:
            return False, f"Streamlit health check failed: {response.status_code}"
    except requests.exceptions.RequestException as e:
        return False, f"Streamlit health endpoint error: {str(e)}"


def get_performance_metrics(url="http://localhost:8501"):
    """Get basic performance metrics"""
    try:
        start_time = time.time()
        response = requests.get(url, timeout=30)
        response_time = time.time() - start_time
        
        return {
            "response_time_seconds": round(response_time, 2),
            "status_code": response.status_code,
            "content_length": len(response.content),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


def monitor_dashboard(url="http://localhost:8501", interval=60, max_checks=None):
    """Continuously monitor the dashboard"""
    print(f"🔍 Starting dashboard monitoring at {url}")
    print(f"⏱️  Check interval: {interval} seconds")
    if max_checks:
        print(f"🔢 Maximum checks: {max_checks}")
    print("-" * 50)
    
    check_count = 0
    
    while True:
        check_count += 1
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Health check
        is_healthy, health_message = check_health(url)
        
        # Streamlit health check
        streamlit_healthy, streamlit_message = check_streamlit_health(url)
        
        # Performance metrics
        metrics = get_performance_metrics(url)
        
        # Status display
        status_icon = "✅" if is_healthy and streamlit_healthy else "❌"
        print(f"{status_icon} [{timestamp}] Check #{check_count}")
        print(f"   Main: {health_message}")
        print(f"   Streamlit: {streamlit_message}")
        
        if "error" not in metrics:
            print(f"   Response time: {metrics['response_time_seconds']}s")
            print(f"   Content size: {metrics['content_length']} bytes")
        else:
            print(f"   Metrics error: {metrics['error']}")
        
        print()
        
        # Exit conditions
        if max_checks and check_count >= max_checks:
            print(f"🏁 Completed {max_checks} checks")
            break
        
        if not (is_healthy and streamlit_healthy):
            print("⚠️  Dashboard is unhealthy!")
            if "--exit-on-failure" in sys.argv:
                sys.exit(1)
        
        # Wait for next check
        time.sleep(interval)


def main():
    """Main monitoring function"""
    if len(sys.argv) < 2:
        print("Usage: python monitor.py <command> [options]")
        print()
        print("Commands:")
        print("  check [url]           - Single health check")
        print("  monitor [url]         - Continuous monitoring")
        print("  metrics [url]         - Get performance metrics")
        print()
        print("Options:")
        print("  --interval=60         - Check interval in seconds")
        print("  --max-checks=10       - Maximum number of checks")
        print("  --exit-on-failure     - Exit if health check fails")
        print()
        print("Examples:")
        print("  python monitor.py check")
        print("  python monitor.py monitor --interval=30")
        print("  python monitor.py metrics http://localhost:8501")
        return
    
    command = sys.argv[1]
    url = "http://localhost:8501"
    
    # Parse URL if provided
    if len(sys.argv) > 2 and not sys.argv[2].startswith("--"):
        url = sys.argv[2]
    
    # Parse options
    interval = 60
    max_checks = None
    
    for arg in sys.argv:
        if arg.startswith("--interval="):
            interval = int(arg.split("=")[1])
        elif arg.startswith("--max-checks="):
            max_checks = int(arg.split("=")[1])
    
    if command == "check":
        print(f"🔍 Checking dashboard health at {url}")
        is_healthy, message = check_health(url)
        streamlit_healthy, streamlit_message = check_streamlit_health(url)
        
        print(f"Main: {message}")
        print(f"Streamlit: {streamlit_message}")
        
        if is_healthy and streamlit_healthy:
            print("✅ Dashboard is healthy")
            sys.exit(0)
        else:
            print("❌ Dashboard is unhealthy")
            sys.exit(1)
    
    elif command == "monitor":
        monitor_dashboard(url, interval, max_checks)
    
    elif command == "metrics":
        print(f"📊 Getting performance metrics for {url}")
        metrics = get_performance_metrics(url)
        print(json.dumps(metrics, indent=2))
    
    else:
        print(f"❌ Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()