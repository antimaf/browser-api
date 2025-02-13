from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime

class TaskConfig(BaseModel):
    model: str = Field(..., description="LLM model to use for the task")
    api_key: Optional[str] = Field(None, description="Optional API key for the model")
    headless: bool = Field(True, description="Whether to run browser in headless mode")
    max_steps: int = Field(10, description="Maximum number of steps for the agent to take")
    record_video: bool = Field(False, description="Whether to record video of the session")
    debug_mode: bool = Field(False, description="Whether to run in debug mode")

class TaskCreate(BaseModel):
    task: str = Field(..., description="Task description")
    config: TaskConfig

class TaskResponse(BaseModel):
    task_id: str
    status: str
    start_time: datetime
    end_time: Optional[datetime] = None
    result: Optional[str] = None
    error: Optional[str] = None
    logs: List[str] = Field(default_factory=list)
