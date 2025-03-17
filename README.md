# Browser API

A browser automation API that enables autonomous web agents using state-of-the-art language models. Create, execute, and monitor web automation tasks using either predefined scripts or natural language instructions.

```python
# Example: Automated Google Search
await run_search_example(
    query="Latest AI developments",
    periodic=True,     # Run periodically
    period=300.0,     # Every 5 minutes
    screenshot_dir="screenshots"
)
```

## Key Features

🤖 **Dual Execution Modes**
- Script-based execution with predefined steps
- Natural language task descriptions
- [See execution modes →](docs/script-execution.md)

🎯 **Precise Control**
- Define exact browser actions
- Validation rules for each step
- Content extraction

🔄 **Task Management**
- Create and monitor tasks
- Periodic execution
- Real-time status updates
- Comprehensive logging

🛠️ **Extras**
- Async support with Quart
- [Installation guide →](docs/installation.md)

## Quick Start

1. **Install**
   ```bash
   git clone https://github.com/antimaf/browser-api.git
   cd browser-api
   python -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configure**
   Create `.env` file:
   ```env
   API_KEY=your_api_key
   OPENAI_API_KEY=your_openai_key  # Or other model keys
   ```

3. **Run**
   ```bash
   # Start the server
   python -m api.main
   
   # Try an example
   python -m examples.google_search
   ```

## Usage Examples

### 1. Quick Start Example
```python
# Example: Automated Google Search
await run_search_example(
    query="Latest AI developments",
    periodic=True,     # Run periodically
    period=300.0,     # Every 5 minutes
    screenshot_dir="screenshots"
)
```

### 2. Script-Based Execution (Recommended)
```python
from browser_api import AutomationScript, ScriptStep, BrowserAction

# Create a script
script = AutomationScript(
    name="Google Search",
    steps=[
        ScriptStep(
            step_id="navigate",
            description="Navigate to Google",
            actions=[
                BrowserAction(
                    action_type="navigate",
                    url="https://www.google.com"
                )
            ]
        )
    ]
)

# Execute via API with periodic scheduling
response = requests.post(
    "http://localhost:5001/api/tasks/script",
    headers={"X-API-Key": "your_api_key"},
    json={
        "task": "Execute search script",
        "script": script.dict(),
        "screenshot_dir": "screenshots",
        "periodic": True,
        "period": 300.0  # Every 5 minutes
    }
)
```

### 3. Direct Task Execution
```python
# Execute using natural language with periodic scheduling
response = requests.post(
    "http://localhost:5001/api/tasks",
    headers={"X-API-Key": "your_api_key"},
    json={
        "task": "Go to Google and search for 'Browser automation'",
        "model": "gpt-4",
        "headless": True,
        "periodic": True,
        "period": 300.0  # Every 5 minutes
    }
)
```

## Use Cases

- **Web Monitoring**: Periodic checks of web content changes
- **Data Collection**: Automated extraction of web data
- **Form Automation**: Streamlined form filling and submission
- **Testing**: Automated web application testing
- **Custom Workflows**: Chain multiple web interactions

## Documentation

📚 [Installation Guide](docs/installation.md)
- Complete setup instructions
- Configuration options
- Environment setup

🔧 [Script Execution Guide](docs/script-execution.md)
- Creating automation scripts
- Task configuration
- Validation rules
- Best practices

📡 [API Reference](docs/api-reference.md)
- Endpoint documentation
- Request/response formats
- Example usage

🤖 [Supported Models](docs/models.md)
- Available LLM models
- Model capabilities
- Upcoming features


## Example: Create a Task

```python
import requests

# Create a browser automation task
response = requests.post(
    "http://localhost:5001/api/tasks",
    json={
        "task": "Search for Python tutorials",
        "config": {
            "model": "gpt-4o",
            "headless": True,
            "periodic": True,
            "period": 3600  # Hourly
        }
    }
)

task_id = response.json()["task_id"]
print(f"Task created: {task_id}")
```

## Project Structure

The project structure is organised as follows:

```
browser-api/
├── api/
│   └── main.py           # API server implementation
├── handlers/
│   ├── agenthandler.py   # Main agent logic
│   ├── taskmanager.py    # Task management
│   └── scriptexecutor.py # Script executor
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

## Authors

- [Anthony Imafidon](https://github.com/antimaf)
