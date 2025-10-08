"""
FastAPI router for web scraping endpoints.
"""

from fastapi import APIRouter, Form, HTTPException
from typing import List, Dict

router = APIRouter()

# This will be populated with the actual endpoint implementations
# from the main.py file during refactoring