import os
import asyncio
import requests
from typing import Optional
from models.browser import AutomationScript, ScriptStep, BrowserAction, ActionType
from models.task import TaskConfig, TaskCreate

def create_google_search_script(search_query: str) -> AutomationScript:
    """
    Create a script that performs a Google search and captures the results
    """
    return AutomationScript(
        name="Google Search",
        description=f"Perform a Google search for '{search_query}' and capture results",
        steps=[
            ScriptStep(
                step_id="navigate",
                description="Navigate to Google",
                actions=[
                    BrowserAction(
                        action_type=ActionType.NAVIGATE,
                        url="https://www.google.com"
                    )
                ]
            ),
            ScriptStep(
                step_id="search",
                description="Enter search query",
                actions=[
                    BrowserAction(
                        action_type=ActionType.TYPE,
                        selector="input[name='q']",
                        value=search_query
                    ),
                    BrowserAction(
                        action_type=ActionType.CLICK,
                        selector="input[type='submit']"
                    )
                ],
                validation={
                    "type": "element_exists",
                    "selector": "#search"
                }
            ),
            ScriptStep(
                step_id="capture",
                description="Capture search results",
                actions=[
                    BrowserAction(
                        action_type=ActionType.EXTRACT,
                        selector=".g"
                    ),
                    BrowserAction(
                        action_type=ActionType.SCREENSHOT,
                        selector="#search"
                    )
                ]
            )
        ]
    )

async def run_search_example(
    query: str,
    api_key: Optional[str] = None,
    api_url: str = "http://localhost:5001",
    periodic: bool = False,
    period: float = 60.0,
    max_retries: int = 3
):
    """
    Example of using the API to perform a Google search
    
    Args:
        query: Search query to execute
        api_key: Optional API key for authentication
        api_url: Base URL of the browser API
        periodic: Whether to run the search periodically
        period: Time between runs if periodic (in seconds)
        max_retries: Maximum number of retries per action
    """
    # Create the automation script
    script = create_google_search_script(query)
    
    # Create task configuration
    config = TaskConfig(
        model="gpt-4o",  # or any other supported model
        headless=True,
        max_steps=5,
        debug_mode=True,
        periodic=periodic,
        period=period,
        max_retries=max_retries
    )
    
    # Create the task
    task = TaskCreate(
        task=f"Search Google for: {query}",
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
    
    # Poll for task completion or until interrupted
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
                                if "result" in task_result and task_result["result"]:
                                    print(f"  Result: {task_result['result']}")
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
    
    asyncio.run(run_search_example(
        query="Python browser automation",
        api_key=os.getenv("API_KEY"),
        periodic=True,  # Run the search periodically
        period=300.0   # Every 5 minutes
    ))
