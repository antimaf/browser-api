#imports
import os
from typing import Optional, List, Dict, Any
from pydantic import SecretStr, BaseModel
import time
import asyncio
from flask import jsonify
import json
from datetime import datetime

#browser_use imports
from browser_use import Agent, Browser, BrowserConfig

from models.llm import create_llm_config
from models.browser import AutomationScript, BrowserAction, ScriptStep

import logging
logger = logging.getLogger(__name__)


class AgentHandler:
    '''
    AgentHandler
    Handles the agent logic for the API

    Args:
        task (str): The task description
        api_key (Optional[str]): The API key for the model
        model (str): The model to use
        headless (bool): Whether to run in headless mode
        max_steps (int): The maximum number of steps to take in the agent
        script (Optional[AutomationScript]): Predefined automation script
        variables (Optional[Dict[str, str]]): Variables for script execution
        screenshot_dir (Optional[str]): Directory to save screenshots
        record_video (bool): Whether to record video of the session
        debug_mode (bool): Whether to run in debug mode with more logging
    '''
    def __init__(
        self, 
        task: str, 
        api_key: Optional[str], 
        model: str, 
        headless: bool, 
        max_steps: int,
        script: Optional[AutomationScript] = None,
        variables: Optional[Dict[str, str]] = None,
        screenshot_dir: Optional[str] = None,
        record_video: bool = False,
        debug_mode: bool = False
    ):
        self.task = task
        self.api_key = api_key
        self.model = model
        self.headless = headless
        self.max_steps = max_steps
        self.script = script
        self.variables = variables or {}
        self.screenshot_dir = screenshot_dir
        self.record_video = record_video
        self.debug_mode = debug_mode
        self.execution_log = []
        self.screenshots = []
        self.video_path = None

        # Initialize LLM configuration
        self.llm_config = create_llm_config(model, api_key) if api_key else None

    def _log_action(self, action: str, details: Dict[str, Any]) -> None:
        """Log an action with timestamp"""
        self.execution_log.append({
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "details": details
        })
        if self.debug_mode:
            logger.debug(f"Action: {action}, Details: {json.dumps(details)}")

    async def take_screenshot(self, controller: Browser, step_id: str) -> str:
        """Take a screenshot and save it"""
        if not self.screenshot_dir:
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{step_id}_{timestamp}.png"
        filepath = os.path.join(self.screenshot_dir, filename)
        await controller.screenshot(filepath)
        self.screenshots.append(filepath)
        return filepath

    async def execute_script(self, controller: Browser) -> Dict[str, Any]:
        """Execute a predefined automation script"""
        if not self.script:
            return {"error": "No script provided"}

        results = []
        for step in self.script.steps:
            step_result = {
                "step_id": step.step_id,
                "description": step.description,
                "status": "started",
                "actions": []
            }

            try:
                for action in step.actions:
                    # Replace variables in action values
                    if action.value and isinstance(action.value, str):
                        for var_name, var_value in self.variables.items():
                            action.value = action.value.replace(f"${var_name}", var_value)

                    action_result = await self._execute_action(controller, action)
                    step_result["actions"].append(action_result)

                    if self.screenshot_dir:
                        screenshot = await self.take_screenshot(controller, step.step_id)
                        if screenshot:
                            action_result["screenshot"] = screenshot

                # Validate step if validation rules exist
                if step.validation:
                    validation_result = await self._validate_step(controller, step.validation)
                    step_result["validation"] = validation_result

                step_result["status"] = "completed"
            except Exception as e:
                step_result["status"] = "failed"
                step_result["error"] = str(e)
                logger.error(f"Step {step.step_id} failed: {str(e)}")
                break

            results.append(step_result)

        return {
            "script_name": self.script.name,
            "steps": results,
            "screenshots": self.screenshots,
            "video": self.video_path,
            "execution_log": self.execution_log
        }

    async def _execute_action(self, controller: Browser, action: BrowserAction) -> Dict[str, Any]:
        """Execute a single browser action"""
        result = {
            "action_type": action.action_type,
            "status": "started"
        }

        try:
            if action.action_type == "click":
                await controller.click(action.selector)
            elif action.action_type == "type":
                await controller.type(action.selector, action.value)
            elif action.action_type == "navigate":
                await controller.navigate(action.url)
            elif action.action_type == "scroll":
                await controller.scroll(action.coordinates["x"], action.coordinates["y"])
            elif action.action_type == "wait":
                await asyncio.sleep(action.wait_time or 1)
            
            result["status"] = "completed"
            self._log_action(action.action_type, {
                "selector": action.selector,
                "value": action.value,
                "url": action.url,
                "coordinates": action.coordinates
            })
        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            logger.error(f"Action {action.action_type} failed: {str(e)}")

        return result

    async def _validate_step(self, controller: Browser, validation: Dict[str, Any]) -> Dict[str, bool]:
        """Validate a step using specified rules"""
        results = {}
        
        if "element_exists" in validation:
            for selector in validation["element_exists"]:
                results[f"element_exists_{selector}"] = await controller.element_exists(selector)
                
        if "url_contains" in validation:
            current_url = await controller.get_current_url()
            results["url_contains"] = validation["url_contains"] in current_url
            
        if "text_visible" in validation:
            for text in validation["text_visible"]:
                results[f"text_visible_{text}"] = await controller.text_visible(text)
                
        return results

    async def execute(self) -> Dict[str, Any]:
        """
        Execute the agent task or script.
        Returns a dictionary containing execution results, screenshots, and logs.
        """
        logger.info(f"Executing task: {self.task}, model: {self.model}, headless: {self.headless}, max_steps: {self.max_steps}")
        
        try:
            # Initialize the browser with proper configuration
            browser = Browser(config=BrowserConfig(headless=self.headless))
            context = await browser.new_context()

            if self.record_video:
                # Start video recording
                if not os.path.exists(self.screenshot_dir):
                    os.makedirs(self.screenshot_dir)
                await context.start_video_recording(self.screenshot_dir)

            # Execute task based on script or AI agent
            if self.script:
                result = await self.execute_script(context)
            else:
                # Execute using AI agent
                agent = Agent(
                    task=self.task,
                    llm=self._get_llm(),
                    max_actions_per_step=4
                )
                agent_result = await agent.run()
                result = {
                    "success": True,
                    "output": str(agent_result),
                    "execution_log": [],
                    "screenshots": [],
                    "video": None
                }

            # Add screenshots if directory is specified
            if self.screenshot_dir:
                if not os.path.exists(self.screenshot_dir):
                    os.makedirs(self.screenshot_dir)
                await context.screenshot(path=os.path.join(self.screenshot_dir, "final.png"))

            return result

        except Exception as e:
            logger.error(f"Error executing task: {str(e)}")
            return {"error": str(e), "execution_log": [], "screenshots": [], "video": None}
        finally:
            # Cleanup
            if self.record_video:
                await context.stop_video_recording()
            await context.close()
            await browser.close()

    def _get_llm(self):
        """Get the appropriate language model based on configuration"""
        if not self.llm_config:
            raise ValueError("No API key provided for the model")
        return self.llm_config.create_llm()
