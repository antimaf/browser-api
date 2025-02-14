from typing import Dict, Any, Optional
from models.browser import AutomationScript, BrowserAction, ActionType
from browser_use import Agent, Browser, BrowserConfig
import asyncio
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ScriptExecutor:
    """Service to convert AutomationScript to browser_use tasks and execute them"""
    
    def __init__(self, browser_config: Optional[BrowserConfig] = None):
        self.browser_config = browser_config or BrowserConfig()
    
    def _action_to_task(self, action: BrowserAction) -> str:
        """Convert a BrowserAction to a browser_use task string"""
        if action.action_type == ActionType.NAVIGATE:
            return f"Navigate to {action.url}"
        elif action.action_type == ActionType.CLICK:
            return f"Click on element matching selector: {action.selector}"
        elif action.action_type == ActionType.TYPE:
            return f"Type '{action.value}' into element matching selector: {action.selector}"
        elif action.action_type == ActionType.WAIT:
            return f"Wait for {action.wait_time} milliseconds"
        elif action.action_type == ActionType.SCROLL:
            if action.coordinates:
                return f"Scroll to coordinates x:{action.coordinates.get('x')}, y:{action.coordinates.get('y')}"
            return "Scroll to bottom of page"
        elif action.action_type == ActionType.SCREENSHOT:
            return f"Take screenshot of element matching selector: {action.selector}"
        elif action.action_type == ActionType.EXTRACT:
            return f"Extract text from element matching selector: {action.selector}"
        else:
            raise ValueError(f"Unsupported action type: {action.action_type}")
    
    def script_to_tasks(self, script: AutomationScript) -> list[str]:
        """Convert an AutomationScript to a list of browser_use tasks"""
        tasks = []
        
        # Handle variable substitution
        variables = script.variables or {}
        
        for step in script.steps:
            for action in step.actions:
                # Handle variable substitution in values
                if action.value and isinstance(action.value, str):
                    for var_name, var_value in variables.items():
                        action.value = action.value.replace(f"${{{var_name}}}", var_value)
                
                task = self._action_to_task(action)
                tasks.append(task)
                
                # Add validation task if specified
                if step.validation:
                    validation_type = step.validation.get("type")
                    selector = step.validation.get("selector")
                    timeout = step.validation.get("timeout", 5000)
                    
                    if validation_type == "element_exists":
                        tasks.append(f"Wait for element matching selector: {selector} (timeout: {timeout}ms)")
                    elif validation_type == "text_contains":
                        expected = step.validation.get("expected_value")
                        tasks.append(f"Verify text in {selector} contains '{expected}' (timeout: {timeout}ms)")
                    elif validation_type == "url_changed":
                        tasks.append(f"Wait for URL to change (timeout: {timeout}ms)")
        
        return tasks
    
    async def execute_script(
        self,
        script: AutomationScript,
        agent: Agent,
        task_interval: float = 0.5,  # Time between tasks in seconds
        periodic: bool = False,      # Whether to run the script periodically
        period: float = 60.0,       # Period in seconds if periodic
        max_retries: int = 3,       # Maximum number of retries per task
        stop_on_error: bool = True  # Whether to stop execution on error
    ) -> Dict[str, Any]:
        """
        Execute an automation script using a browser_use agent
        
        Args:
            script: The AutomationScript to execute
            agent: The browser_use Agent to use
            task_interval: Time to wait between tasks
            periodic: Whether to run the script periodically
            period: Time between script runs if periodic
            max_retries: Maximum number of retries per task
            stop_on_error: Whether to stop execution on error
        
        Returns:
            Dict containing execution results and execution metadata
        """
        tasks = self.script_to_tasks(script)
        execution_results = {
            "script_name": script.name,
            "runs": [],
            "is_periodic": periodic,
            "period": period if periodic else None,
            "total_runs": 0,
            "successful_runs": 0,
            "failed_runs": 0,
            "start_time": datetime.now().isoformat()
        }
        
        async def run_once() -> Dict[str, Any]:
            run_results = []
            run_success = True
            run_start_time = datetime.now().isoformat()
            
            for task in tasks:
                for attempt in range(max_retries):
                    try:
                        result = await agent.execute_task(task)
                        run_results.append({
                            "task": task,
                            "result": result,
                            "success": True,
                            "attempt": attempt + 1,
                            "timestamp": datetime.now().isoformat()
                        })
                        await asyncio.sleep(task_interval)
                        break
                    except Exception as e:
                        logger.error(f"Error executing task '{task}' (attempt {attempt + 1}/{max_retries}): {str(e)}")
                        if attempt == max_retries - 1:  # Last attempt
                            run_results.append({
                                "task": task,
                                "error": str(e),
                                "success": False,
                                "attempt": attempt + 1,
                                "timestamp": datetime.now().isoformat()
                            })
                            run_success = False
                            if stop_on_error:
                                return {
                                    "success": False,
                                    "results": run_results,
                                    "error": f"Failed after {max_retries} attempts: {str(e)}",
                                    "start_time": run_start_time,
                                    "end_time": datetime.now().isoformat()
                                }
                        await asyncio.sleep(task_interval)  # Wait before retry
            
            return {
                "success": run_success,
                "results": run_results,
                "start_time": run_start_time,
                "end_time": datetime.now().isoformat()
            }
        
        try:
            if periodic:
                while True:
                    result = await run_once()
                    execution_results["total_runs"] += 1
                    if result["success"]:
                        execution_results["successful_runs"] += 1
                    else:
                        execution_results["failed_runs"] += 1
                    execution_results["runs"].append(result)
                    
                    if not result["success"] and stop_on_error:
                        break
                    
                    await asyncio.sleep(period)
            else:
                result = await run_once()
                execution_results["total_runs"] = 1
                execution_results["successful_runs"] = 1 if result["success"] else 0
                execution_results["failed_runs"] = 0 if result["success"] else 1
                execution_results["runs"].append(result)
        
        except asyncio.CancelledError:
            logger.info("Script execution was cancelled")
            execution_results["status"] = "cancelled"
        except Exception as e:
            logger.error(f"Unexpected error during script execution: {str(e)}")
            execution_results["status"] = "error"
            execution_results["error"] = str(e)
        else:
            execution_results["status"] = "completed"
        
        execution_results["end_time"] = datetime.now().isoformat()
        return execution_results
