"""
FastAPI router for document management endpoints.
"""

from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from typing import List, Dict

router = APIRouter()

# This will be populated with the actual endpoint implementations
# from the main.py file during refactoring