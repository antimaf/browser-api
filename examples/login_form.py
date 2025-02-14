#External dependencies
import os
import asyncio
import requests
from typing import Optional

# Local imports
from models.browser import AutomationScript, ScriptStep, BrowserAction, ActionType
from models.task import TaskConfig, TaskCreate

def create_login_script(url: str) -> AutomationScript:
    """
    Create a script that fills out a login form
    """
    return AutomationScript(
        name="Login Form",
        description="Fill out and submit a login form",
        variables={
            "username": "",  # To be filled by user
            "password": ""   # To be filled by user
        },
        steps=[
            ScriptStep(
                step_id="navigate",
                description="Navigate to login page",
                actions=[
                    BrowserAction(
                        action_type=ActionType.NAVIGATE,
                        url=url
                    )
                ]
            ),
            ScriptStep(
                step_id="fill_form",
                description="Fill out login form",
                actions=[
                    BrowserAction(
                        action_type=ActionType.TYPE,
                        selector="input[type='email'], input[name='username']",
                        value="${username}"
                    ),
                    BrowserAction(
                        action_type=ActionType.TYPE,
                        selector="input[type='password']",
                        value="${password}"
                    )
                ]
            ),
            ScriptStep(
                step_id="submit",
                description="Submit login form",
                actions=[
                    BrowserAction(
                        action_type=ActionType.CLICK,
                        selector="button[type='submit'], input[type='submit']"
                    )
                ],
                validation={
                    "type": "url_changed",
                    "timeout": 5000
                }
            )
        ]
    )

async def run_login_example(
    url: str,
    username: str,
    password: str,
    api_key: Optional[str] = None,
    api_url: str = "http://localhost:5001",
    max_retries: int = 3
):
    """
    Example of using the API to automate a login process
    
    Args:
        url: The URL of the login page
        username: Username to login with
        password: Password to login with
        api_key: Optional API key for authentication
        api_url: Base URL of the browser API
        max_retries: Maximum number of retries per action
    """
    # Create the automation script
    script = create_login_script(url)
    script.variables = {
        "username": username,
        "password": password
    }
    
    # Create task configuration
    config = TaskConfig(
        model="gpt-4o",  # or any other supported model
        headless=True,
        max_steps=5,
        debug_mode=True,
        max_retries=max_retries,
        stop_on_error=True  # Stop on first error for login attempts
    )
    
    # Create the task
    task = TaskCreate(
        task=f"Login to {url} using provided credentials",
        config=config,
        script=script.dict()
    )
    
    # Set up headers
    headers = {
        "Content-Type": "application/json"
    }
    if api_key:
        headers["X-API-Key"] = api_key
    
    # Submit task to API
    response = requests.post(
        f"{api_url}/api/tasks",
        json=task.dict(),
        headers=headers
    )
    response.raise_for_status()
    task_id = response.json()["task_id"]
    
    print(f"Task created with ID: {task_id}")
    print("Monitoring task execution...")
    
    # Poll for task completion
    try:
        while True:
            status_response = requests.get(
                f"{api_url}/api/tasks/{task_id}",
                headers=headers
            )
            status_response.raise_for_status()
            status = status_response.json()
            
            print(f"\rTask status: {status['status']}", end="")
            
            if status["status"] in ["completed", "failed", "cancelled"]:
                print(f"\nTask {status['status']}")
                if status.get("error"):
                    print(f"Error: {status['error']}")
                if status.get("result"):
                    print("\nResults:")
                    for run in status["result"]["runs"]:
                        print(f"\nRun at {run['start_time']}:")
                        for task_result in run["results"]:
                            if task_result["success"]:
                                print(f"✓ {task_result['task']}")
                            else:
                                print(f"✗ {task_result['task']}")
                                print(f"  Error: {task_result['error']}")
                break
            
            await asyncio.sleep(1)
    
    except KeyboardInterrupt:
        print("\nCancelling task...")
        requests.post(f"{api_url}/api/tasks/{task_id}/cancel", headers=headers)
        print("Task cancelled")

if __name__ == "__main__":
    # Example usage
    import dotenv
    dotenv.load_dotenv()
    
    asyncio.run(run_login_example(
        url="https://example.com/login",
        username=os.getenv("TEST_USERNAME"),
        password=os.getenv("TEST_PASSWORD"),
        api_key=os.getenv("API_KEY"),
        max_retries=3
    ))
