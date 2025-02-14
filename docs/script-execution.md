# Script Execution Guide

Scripts are executed with the following features:

- **Retry Mechanism**: Configurable retries for failed actions
- **Periodic Execution**: Run scripts at specified intervals
- **Error Handling**: Detailed error reporting and optional stop-on-error
- **Validation**: Built-in step validation (element exists, text contains, URL changed)
- **Variable Substitution**: Use variables in your scripts that are filled at runtime

The Browser API supports two modes of execution: script-based and direct task execution. Each mode has its own advantages and use cases.

## 1. Script-Based Execution (Recommended)

Script-based execution provides precise control over browser actions and is recommended for:
- Repeatable automation tasks
- Complex multi-step workflows
- Tasks requiring validation
- Scenarios needing exact timing or specific actions

### Creating a Script

```python
from browser_api import AutomationScript, ScriptStep, BrowserAction

script = AutomationScript(
    name="My Automation",
    description="Automate a web workflow",
    steps=[
        ScriptStep(
            step_id="step1",
            description="Navigate to website",
            actions=[
                BrowserAction(
                    action_type="navigate",
                    url="https://example.com"
                )
            ],
            validation={
                "type": "element_exists",
                "selector": "#main-content"
            }
        )
    ]
)
```

### Available Actions

| Action Type | Description | Required Parameters |
|------------|-------------|-------------------|
| navigate | Navigate to URL | url |
| click | Click element | selector |
| type | Type text | selector, value |
| extract | Extract content | selector |
| screenshot | Take screenshot | selector (optional) |

### Validation Rules

Each step can include validation rules to ensure proper execution:

```python
validation={
    "type": "element_exists",  # Check if element exists
    "selector": "#result"      # CSS selector to verify
}
```

### Executing a Script

```python
response = requests.post(
    "http://localhost:5001/api/tasks/script",
    headers={"X-API-Key": "your_api_key"},
    json={
        "task": "Execute automation script",
        "script": script.dict(),
        "model": "gpt-4",
        "headless": True,
        "screenshot_dir": "screenshots",
        "debug_mode": True
    }
)
```

## 2. Direct Task Execution

Direct task execution uses natural language to describe the desired task. This mode is ideal for:
- Quick, one-off automation tasks
- Simple workflows
- Exploratory automation
- When exact steps are not critical

### Example Usage

```python
response = requests.post(
    "http://localhost:5001/api/tasks",
    headers={"X-API-Key": "your_api_key"},
    json={
        "task": "Go to example.com and extract all article titles",
        "model": "gpt-4",
        "headless": True,
        "max_steps": 5
    }
)
```

## Example: Google Search

```python
from examples.google_search import run_search_example

await run_search_example(
    query="Python automation",
    periodic=True,    # Run periodically
    period=300.0,    # Every 5 minutes
    max_retries=3    # Retry failed actions up to 3 times
)
```

## Example: Login Form

```python
from examples.login_form import run_login_example

await run_login_example(
    url="https://example.com/login",
    username="user@example.com",
    password="password123",
    max_retries=3
)
```

## Features
- Create and execute browser automation scripts
- Periodic script execution with configurable intervals
- Robust error handling and retry mechanisms
- Real-time task status monitoring
- Variable substitution in scripts
- Step validation and verification
- Screenshot and text extraction capabilities

## Best Practices

1. **Script Organization**
   - Use meaningful step IDs and descriptions
   - Group related actions into steps
   - Add validation rules for critical steps

2. **Error Handling**
   - Set appropriate max_retries for actions
   - Include validation rules
   - Use debug_mode during development

3. **Performance**
   - Use headless mode when possible
   - Optimize selectors for reliability
   - Group related actions into single steps

4. **Monitoring**
   - Enable debug_mode for detailed logs
   - Use screenshot_dir to capture visual state
   - Monitor task status via API

## Examples

See the `examples/` directory for complete working examples:
- `google_search.py`: Search automation with both execution modes
- `form_submission.py`: Form automation with validation
- `monitoring.py`: Periodic website monitoring
