from typing import Dict, Optional
from pydantic import BaseModel, Field

class ModelConfig(BaseModel):
    type: str = Field(..., description="Model provider (OpenAI, Anthropic, etc)")
    description: str
    api_key_required: bool = True
    max_tokens: Optional[int] = None
    rate_limit: Optional[int] = None

class APIConfig(BaseModel):
    default_model: str = "gpt-4"
    models: Dict[str, ModelConfig]
    rate_limits: Dict[str, int]
    default_timeout: int = 300
    max_concurrent_tasks: int = 10
    screenshot_dir: Optional[str] = None
    debug_mode: bool = False
