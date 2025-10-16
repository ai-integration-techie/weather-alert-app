#!/usr/bin/env python3
"""
Development runner for Weather Insights Advisor Python implementation
"""

import sys
import uvicorn

if __name__ == "__main__":
    print("🌤️  Starting Weather Insights Advisor (Python)")
    print("📡 Multi-agent weather intelligence system")
    print("🔗 Access the API at: http://localhost:8080")
    print("📚 API Documentation: http://localhost:8080/docs")
    print()
    
    try:
        uvicorn.run(
            "python_src.adk.main:app",
            host="0.0.0.0",
            port=8080,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Shutting down gracefully...")
        sys.exit(0)
