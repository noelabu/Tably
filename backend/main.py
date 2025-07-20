import os
import uvicorn
from fastapi import FastAPI
from app.core.app import create_app
from app.core.config import settings

# Ensure .env is loaded at startup
try:
    from dotenv import load_dotenv
    load_dotenv()
    print(f"Environment loaded. AWS credentials: {'YES' if os.getenv('AWS_ACCESS_KEY_ID') else 'NO'}")
except ImportError:
    print("dotenv not available")
    pass

# Create the FastAPI app instance
app = create_app(settings)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
