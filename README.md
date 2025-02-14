# Browser API

A browser automation API that enables autonomous web agents using state-of-the-art language models. Create, execute, and monitor web automation tasks using natural language instructions.

```python
# Example: Automated Google Search
await run_search_example(
    query="Latest AI developments",
    periodic=True,     # Run periodically
    period=300.0      # Every 5 minutes
)
```

## Key Features

🤖 **Multi-Model Support**
- OpenAI GPT-4o, Claude 3.5, Gemini Pro, DeepSeek
- Choose the best model for your use case
- [See all supported models →](docs/models.md)

🌐 **Browser Automation**
- Natural language task descriptions
- Headless or visible browser modes
- Screenshot and text extraction
- [Learn about script execution →](docs/script-execution.md)

⚡ **Robust Execution**
- Automatic retries for failed actions
- Periodic task execution
- Real-time status monitoring
- Comprehensive validation
- [API documentation →](docs/api-reference.md)

🔒 **Enterprise Ready**
- Secure API key management
- Async support with Quart
- Detailed logging system
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
