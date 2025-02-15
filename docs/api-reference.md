# API Reference

## API Endpoints

### Create Task
`POST /api/tasks`

Create a new browser automation task.

Request body:
```json
{
    "task": "Task description",
    "config": {
        "model": "gpt-4o",
        "headless": true,
        "max_steps": 5,
        "debug_mode": true,
        "periodic": false,
        "period": 60.0,
        "max_retries": 3,
        "stop_on_error": true
    },
    "script": {
        "name": "Script Name",
        "description": "Script Description",
        "steps": [...]
    }
}
```

### Create Script-Based Task
`POST /api/tasks/script`

Execute a predefined automation script.

Request body:
```json
{
    "task": "string",
    "script": {
        "name": "string",
        "description": "string",
        "steps": [
            {
                "step_id": "string",
                "description": "string",
                "actions": [
                    {
                        "action_type": "string",
                        "selector": "string",
                        "url": "string",
                        "value": "string"
                    }
                ],
                "validation": {
                    "type": "string",
                    "selector": "string"
                }
            }
        ]
    },
    "model": "string",
    "headless": true,
    "max_retries": 3,
    "screenshot_dir": "string",
    "debug_mode": true
}
```

Response:
```json
{
    "task_id": "string",
    "status": "string",
    "result": {
        "success": true,
        "steps": [
            {
                "step_id": "string",
                "status": "string",
                "actions": [
                    {
                        "type": "string",
                        "status": "string",
                        "content": "string"
                    }
                ],
                "screenshot": "string"
            }
        ],
        "screenshots": ["string"],
        "video_path": "string",
        "execution_log": [
            {
                "timestamp": "string",
                "action": "string",
                "details": {}
            }
        ]
    }
}
```

### Get Task Status
`GET /api/tasks/{task_id}`

Get the status and result of a task.

Response:
```json
{
    "task_id": "string",
    "status": "string",
    "result": {
        "success": true,
        "output": "Task execution result",
        "execution_log": [],
        "screenshots": [],
        "video": null
    }
}
```

### Cancel Task
`POST /api/tasks/{task_id}/cancel`

Cancel a running task.

Response:
```json
{
    "task_id": "task_1234567890",
    "status": "cancelled"
}
```

## Example Usage

Using curl:
```bash
curl -X POST http://localhost:5001/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Search for information about AI on Google",
    "model": "gemini-pro",
    "api_key": "your_api_key",
    "headless": true,
    "max_steps": 10
  }'
```

Using Python:
```python
import requests

response = requests.post(
    "http://localhost:5001/api/tasks",
    json={
        "task": "Search for information about AI on Google",
        "model": "gemini-pro",
        "api_key": "your_api_key",
        "headless": True,
        "max_steps": 10
    }
)
print(response.json())
```
