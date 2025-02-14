# Script Execution Guide

Scripts are executed with the following features:

- **Retry Mechanism**: Configurable retries for failed actions
- **Periodic Execution**: Run scripts at specified intervals
- **Error Handling**: Detailed error reporting and optional stop-on-error
- **Validation**: Built-in step validation (element exists, text contains, URL changed)
- **Variable Substitution**: Use variables in your scripts that are filled at runtime

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
