from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from enum import Enum

class ActionType(str, Enum):
    CLICK = "click"
    TYPE = "type"
    NAVIGATE = "navigate"
    WAIT = "wait"
    SCROLL = "scroll"
    SCREENSHOT = "screenshot"
    EXTRACT = "extract"

class BrowserAction(BaseModel):
    action_type: ActionType
    selector: Optional[str] = None
    value: Optional[str] = None
    url: Optional[str] = None
    coordinates: Optional[Dict[str, int]] = None
    wait_time: Optional[int] = None
    
    class Config:
        use_enum_values = True

class ValidationRule(BaseModel):
    type: str = Field(..., description="Type of validation (element_exists, text_contains, etc)")
    selector: Optional[str] = None
    expected_value: Optional[str] = None
    timeout: Optional[int] = Field(5000, description="Timeout in milliseconds")

class ScriptStep(BaseModel):
    step_id: str
    description: str
    actions: List[BrowserAction]
    validation: Optional[Dict[str, Any]] = None

class AutomationScript(BaseModel):
    name: str
    description: str
    steps: List[ScriptStep]
    variables: Optional[Dict[str, str]] = None
