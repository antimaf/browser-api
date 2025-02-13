# Browser API

A powerful API that provides browser automation capabilities using various LLM models. This API allows you to create autonomous agents that can perform web-based tasks using natural language instructions.

## Features
- 🤖 Multiple LLM Support: Compatible with OpenAI, Anthropic, Google, and DeepSeek models
- 🌐 Browser Automation: Headless and visible browser modes
- 📸 Screenshot Capture: Automatically capture screenshots during task execution
- 🎥 Video Recording: Record browser sessions for task analysis
- 🔄 Async Support: Built with Quart for async operations
- 🛡️ CORS Support: Built-in CORS handling for web applications
- 📝 Logging: Comprehensive logging system for debugging

## Supported Models
- OpenAI
  - GPT-4
  - GPT-3.5 Turbo
- Anthropic
  - Claude 2
  - Claude 3.5 Sonnet
- Google
  - Gemini Pro
- DeepSeek
  - DeepSeek Reasoner

## Prerequisites
- Python 3.11+
- Playwright
- Virtual Environment (recommended)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/browser-api.git
cd browser-api
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install Playwright browsers:
```bash
playwright install
```

5. Set up environment variables:
Create a `.env` file with your API keys:
```env
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
DEEPSEEK_API_KEY=your_deepseek_key
GEMINI_API_KEY=your_gemini_key
```

## Running the Server

Start the API server:
```bash
python -m api.main
```

The server will start on `http://localhost:5001` by default.

## API Endpoints

### Create Task
`POST /api/tasks`

Create a new browser automation task.

Request body:
```json
{
    "task": "Search for information about AI on Google",
    "model": "gemini-pro",  // or "gpt-4", "claude-2", "deepseek-reasoner"
    "api_key": "your_api_key",  // Optional: if not provided, will use server-side keys
    "headless": true,  // Whether to run browser in headless mode
    "max_steps": 10,   // Maximum number of steps for the agent to take
    "record_video": false,  // Whether to record the browser session
    "debug_mode": false     // Enable debug logging
}
```

Response:
```json
{
    "task_id": "task_1234567890",
    "status": "completed",
    "result": {
        "success": true,
        "output": "Task execution result",
        "execution_log": [],
        "screenshots": [],
        "video": null
    }
}
```

### Get Task Status
`GET /api/tasks/{task_id}`

Get the status and result of a task.

Response:
```json
{
    "task_id": "task_1234567890",
    "status": "completed",
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

## Development

The project structure is organized as follows:

```
browser-api/
├── api/
│   └── main.py           # API server implementation
├── handlers/
│   ├── agenthandler.py   # Main agent logic
│   └── taskmanager.py    # Task management
├── models/
│   ├── browser.py        # Browser-related models
│   ├── llm.py           # LLM configurations
│   └── task.py          # Task-related models
├── config/
│   ├── __init__.py
│   └── logging.py       # Logging configuration
├── examples/            # Example scripts
├── requirements.txt
└── README.md
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
