from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import asyncio
from browser_use import Controller
from .scriptexecutor import ScriptExecutor
from models.browser import AutomationScript
from models.task import TaskStatus
import time

@dataclass
class TaskStatus:
    """Data class to store task status"""
    task_id: str
    status: str  # running, completed, failed, cancelled
    start_time: float
    end_time: Optional[float] = None
    result: Optional[dict] = None
    error: Optional[str] = None
    logs: List[str] = None

class TaskManager:
    """Task manager class to manage task execution"""
    def __init__(self):
        self.tasks: Dict[str, TaskStatus] = {}
        self.active_browsers: Dict[str, Controller] = {}
        self.task_counter = 0
        self.script_executor = ScriptExecutor()

    def generate_task_id(self) -> str:
        self.task_counter += 1
        return f"task_{int(time.time())}_{self.task_counter}"

    def register_task(self, task_id: str) -> None:
        self.tasks[task_id] = TaskStatus(
            task_id=task_id,
            status="running",
            start_time=time.time(),
            logs=[]
        )

    async def execute_task(self, task_id: str, script: AutomationScript, config: dict) -> None:
        """Execute a task with the given script and configuration"""
        try:
            # Create or get browser controller
            if task_id not in self.active_browsers:
                self.active_browsers[task_id] = Controller(
                    headless=config.get("headless", True),
                    debug_mode=config.get("debug_mode", False)
                )
            
            controller = self.active_browsers[task_id]
            agent = await controller.get_agent()
            
            # Execute the script
            result = await self.script_executor.execute_script(
                script=script,
                agent=agent,
                task_interval=0.5,
                periodic=config.get("periodic", False),
                period=config.get("period", 60.0),
                max_retries=config.get("max_retries", 3),
                stop_on_error=config.get("stop_on_error", True)
            )
            
            # Update task status
            if result["status"] == "completed":
                self.complete_task(task_id, result)
            else:
                self.fail_task(task_id, result.get("error", "Unknown error"))
            
        except Exception as e:
            self.fail_task(task_id, str(e))
        finally:
            # Cleanup browser if needed
            if task_id in self.active_browsers:
                await self.active_browsers[task_id].cleanup()
                del self.active_browsers[task_id]

    def complete_task(self, task_id: str, result: dict) -> None:
        if task_id in self.tasks:
            self.tasks[task_id].status = "completed"
            self.tasks[task_id].end_time = time.time()
            self.tasks[task_id].result = result

    def fail_task(self, task_id: str, error: str) -> None:
        if task_id in self.tasks:
            self.tasks[task_id].status = "failed"
            self.tasks[task_id].end_time = time.time()
            self.tasks[task_id].error = error

    def cancel_task(self, task_id: str) -> bool:
        if task_id in self.tasks and self.tasks[task_id].status == "running":
            self.tasks[task_id].status = "cancelled"
            self.tasks[task_id].end_time = time.time()
            return True
        return False

    def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        return self.tasks.get(task_id)

    def get_all_tasks(self) -> List[TaskStatus]:
        return list(self.tasks.values())

    def add_log(self, task_id: str, log_message: str) -> None:
        if task_id in self.tasks:
            self.tasks[task_id].logs.append(f"{datetime.now().isoformat()}: {log_message}")

    async def start_browser(self, task_id: str, headless: bool = True) -> None:
        if task_id not in self.active_browsers:
            controller = Controller(headless=headless)
            await controller.start()
            self.active_browsers[task_id] = controller

    async def stop_browser(self, task_id: str) -> None:
        if task_id in self.active_browsers:
            await self.active_browsers[task_id].stop()
            del self.active_browsers[task_id]

    def get_browser_status(self, task_id: str) -> str:
        return "running" if task_id in self.active_browsers else "stopped"

    def clear_history(self) -> None:
        """Clear all task history"""
        # Only clear completed, failed, or cancelled tasks
        active_tasks = {task_id: task for task_id, task in self.tasks.items() 
                       if task.status == "running"}
        self.tasks = active_tasks

# Global task manager instance
task_manager = TaskManager()
