# User Gaze Track API

A modular API for managing gaze tracking data, subjects, and measurements.

## Structure

```
api/
├── __init__.py          # Module initialization
├── routes.py            # API route definitions
├── services.py          # Business logic and data processing
├── config.py            # API configuration and settings
└── README.md            # This documentation
```

## Modules

### routes.py
Contains all API endpoint definitions using Flask blueprints. Routes are organized by functionality:

- **Subject Management**: `/api/get-subjects`
- **Data Retrieval**: `/api/get-user-points`, `/api/get-user-tasklogs`
- **Data Storage**: `/api/save-points`, `/api/save-tasklogs`
- **Data Export**: `/api/download-points`, `/api/download-tasklogs`, `/api/download-all`
- **Configuration**: `/api/config`, `/api/tasks`

### services.py
Contains business logic organized into service classes:

- **SubjectService**: Subject management operations
- **MeasurementService**: Measurement data processing
- **TaskLogService**: Task logging operations
- **ExportService**: Data export functionality

### config.py
Centralized configuration for API settings, swagger documentation, and response messages.

## API Endpoints

### GET /api/get-subjects
Returns a list of all registered subjects.

**Response:**
```json
[
  {
    "id": 1,
    "name": "John",
    "surname": "Doe", 
    "age": 25
  }
]
```

### GET /api/get-user-points?id={subject_id}
Returns measurement points for a specific subject.

**Parameters:**
- `id` (int): Subject ID

**Response:**
```json
{
  "subject_id": 1,
  "points": [
    {
      "date": "2023-01-01 12:00:00",
      "x_mouse": 100.5,
      "y_mouse": 200.3,
      "x_gaze": 105.2,
      "y_gaze": 198.7
    }
  ]
}
```

### GET /api/get-user-tasklogs?id={subject_id}
Returns task logs for a specific subject.

### POST /api/save-points
Saves measurement points to the database.

**Body:**
```json
{
  "id": 1,
  "points": [
    {
      "date": "1/1/2023, 12:00:00 PM",
      "gaze": {"x": 105.2, "y": 198.7},
      "mouse": {"x": 100.5, "y": 200.3}
    }
  ]
}
```

### POST /api/save-tasklogs
Saves task logs to the database.

### GET /api/download-points?id={subject_id}
Downloads measurement points as CSV for a specific subject.

### GET /api/download-tasklogs?id={subject_id}
Downloads task logs as CSV for a specific subject.

### GET /api/download-all
Downloads all measurement points as CSV for all subjects.

### GET /api/config
Returns the configuration file.

### GET /api/tasks
Returns the tasks file.

## Usage

The API is automatically registered with the main Flask application via blueprints:

```python
from api.routes import api_bp
app.register_blueprint(api_bp)
```

All API endpoints are prefixed with `/api/` and return JSON responses unless otherwise specified.

## Error Handling

The API returns appropriate HTTP status codes:
- `200`: Success
- `404`: Resource not found (subject, data, etc.)
- `400`: Bad request (invalid data format)
- `500`: Internal server error

## Data Formats

### Date Format
All dates in requests should be in the format: `"MM/DD/YYYY, HH:MM:SS AM/PM"`

### CSV Export Format
CSV files include appropriate headers and UTF-8 encoding for proper display of special characters.
