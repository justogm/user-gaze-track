"""
API module for user gaze tracking application.

This module provides a RESTful API for managing subjects, measurements,
task logs, and data export functionality.
"""

from .routes import api_bp
from .config import API_VERSION, API_PREFIX

__version__ = API_VERSION
__all__ = ["api_bp", "API_VERSION", "API_PREFIX"]
