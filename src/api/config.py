"""
API configuration and settings for the user gaze tracking application.
"""

API_VERSION = "v1"
API_PREFIX = "/api"

# Swagger documentation configuration
SWAGGER_CONFIG = {
    "title": "User Gaze Track API",
    "description": "API for managing gaze tracking data and subjects",
    "version": API_VERSION,
    "basePath": API_PREFIX,
    "tags": [
        {"name": "subjects", "description": "Operations related to subjects"},
        {
            "name": "measurements",
            "description": "Operations related to gaze and mouse measurements",
        },
        {"name": "task-logs", "description": "Operations related to task logging"},
        {"name": "exports", "description": "Data export functionality"},
        {"name": "config", "description": "Configuration file access"},
    ],
}

# Response messages
API_RESPONSES = {
    "SUBJECT_NOT_FOUND": "Subject not found",
    "NO_SUBJECTS": "No registered subjects",
    "SUCCESS": "success",
    "TASKLOGS_SAVED": "TaskLogs saved successfully.",
}
