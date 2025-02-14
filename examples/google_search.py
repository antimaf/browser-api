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
    api_url: str = "http://localhost:5001"
):
    """
    Example of using the API to perform a Google search
    
    Args:
        query: Search query to execute
        api_key: Optional API key for authentication
        api_url: Base URL of the browser API
    """
    # Create the automation script
    script = create_google_search_script(query)
    
    # Create task configuration
    config = TaskConfig(
        model="gpt-4o",  # or any other supported model
        headless=True,
        max_steps=5,
        debug_mode=True
    )
    
    # Create the task
    task = TaskCreate(
        task=f"Search Google for: {query}",
        config=config
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
        json=task.model_dump(),
        headers=headers
    )
    response.raise_for_status()
    task_id = response.json()["task_id"]
    
    # Poll for task completion
    while True:
        status_response = requests.get(
            f"{api_url}/api/tasks/{task_id}",
            headers=headers
        )
        status_response.raise_for_status()
        status = status_response.json()
        
        if status["status"] in ["completed", "failed"]:
            print(f"Task {status['status']}")
            if status.get("error"):
                print(f"Error: {status['error']}")
            if status.get("result"):
                print(f"Result: {status['result']}")
            break
            
        await asyncio.sleep(1)

if __name__ == "__main__":
    # Example usage
    import dotenv
    dotenv.load_dotenv()
    
    asyncio.run(run_search_example(
        query="Python browser automation",
        api_key=os.getenv("API_KEY")
    ))
