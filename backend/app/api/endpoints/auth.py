import os
import io
import numpy as np
import base64
import wave
from pathlib import Path
from fastapi import APIRouter, HTTPException, Depends, Request, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging
from app.core.config import settings
import json
import asyncio
from datetime import datetime

# Configure logging
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL))
logger = logging.getLogger(__name__)

router = APIRouter()

# Simple health check endpoint
@router.get("/health")
async def health_check():
    """
    Simple health check endpoint to verify the service is running
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "auth"
    }

# Simple hello endpoint with optional name parameter
@router.get("/hello")
async def say_hello(name: Optional[str] = "World"):
    """
    Simple greeting endpoint
    """
    return {"message": f"Hello, {name}!"}
