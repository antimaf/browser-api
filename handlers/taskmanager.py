from typing import Dict, List, Optional
import time
from dataclasses import dataclass
from datetime import datetime
import asyncio
from browser_use  import Controller

@dataclass
class TaskStatus:
    task_id: str
    status: str  # running, completed, failed, cancelled
    start_time: float
    end_time: Optional[float] = None
    result: Optional[str] = None
    error: Optional[str] = None
    logs: List[str] = None

class TaskManager:
    def __init__(self):
        self.tasks: Dict[str, TaskStatus] = {}
        self.active_browsers: Dict[str, Controller] = {}
        self.task_counter = 0

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

    def complete_task(self, task_id: str, result: str) -> None:
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
