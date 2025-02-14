import os
import asyncio
import requests
from typing import Optional
from models.browser import AutomationScript, ScriptStep, BrowserAction, ActionType
import logging

logger = logging.getLogger(__name__)

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
    max_retries: int = 3,
    headless: bool = True,
    screenshot_dir: Optional[str] = None
):
    """
    Example of using the API to perform a Google search
    
    Two methods are demonstrated:
    1. Script-based execution (recommended): Uses a predefined automation script
    2. Direct task execution: Uses natural language task description
    
    Args:
        query: Search query to execute
        api_key: Optional API key for authentication
        api_url: Base URL of the browser API
        periodic: Whether to run the search periodically
        period: Time between runs if periodic (in seconds)
        max_retries: Maximum number of retries per action
        headless: Whether to run in headless mode
        screenshot_dir: Directory to save screenshots
    """
    headers = {"X-API-Key": api_key} if api_key else {}
    
    while True:  # Main loop for periodic execution
        try:
            # Method 1: Script-based execution (recommended)
            print("\nMethod 1: Script-based execution")
            script = create_google_search_script(query)
            
            script_response = requests.post(
                f"{api_url}/api/tasks/script",
                headers=headers,
                json={
                    "task": f"Search Google for: {query}",
                    "script": script.dict(),
                    "model": "gpt-4",  # or any other supported model
                    "headless": headless,
                    "max_retries": max_retries,
                    "screenshot_dir": screenshot_dir,
                    "debug_mode": True,
                    "periodic": periodic,
                    "period": period
                }
            )
            
            script_result = script_response.json()
            print(f"Task ID: {script_result['task_id']}")
            print(f"Status: {script_result['status']}")
            if script_result.get('screenshots'):
                print(f"Screenshots saved to: {script_result['screenshots']}")
            
            # Method 2: Direct task execution
            print("\nMethod 2: Direct task execution")
            task_response = requests.post(
                f"{api_url}/api/tasks",
                headers=headers,
                json={
                    "task": f"Go to Google and search for '{query}'. Extract the search results.",
                    "model": "gpt-4",
                    "headless": headless,
                    "max_steps": 5,
                    "periodic": periodic,
                    "period": period
                }
            )
            
            task_result = task_response.json()
            print(f"Task ID: {task_result['task_id']}")
            print(f"Status: {task_result['status']}")
            
            # If not periodic, break after one execution
            if not periodic:
                break
                
            # Wait for the specified period before next execution
            print(f"\nWaiting {period} seconds before next execution...")
            await asyncio.sleep(period)
            
        except KeyboardInterrupt:
            print("\nExecution interrupted by user")
            break
        except Exception as e:
            print(f"\nError during execution: {e}")
            if not periodic:
                break
            print(f"Waiting {period} seconds before retry...")
            await asyncio.sleep(period)

if __name__ == "__main__":
    import dotenv
    dotenv.load_dotenv()
    
    # Example usage
    asyncio.run(run_search_example(
        query="Latest AI developments",
        api_key=os.getenv("API_KEY"),
        screenshot_dir="screenshots",
        headless=True,
        periodic=True,     # Run periodically
        period=300.0      # Every 5 minutes
    ))
