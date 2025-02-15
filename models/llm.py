from typing import Optional
from pydantic import BaseModel, SecretStr, Field
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema.language_model import BaseLanguageModel

class LLMConfig(BaseModel):
    """Base configuration for language models"""
    model: str = Field(..., description="Model name to use")
    api_key: SecretStr = Field(..., description="API key for the model")
    temperature: float = Field(0.7, description="Temperature for model output")

class GeminiConfig(LLMConfig):
    """Configuration for Google's Gemini model"""
    convert_system_message_to_human: bool = Field(True, description="Convert system messages to human format")
    top_p: float = Field(1.0, description="Top p sampling parameter")
    top_k: int = Field(32, description="Top k sampling parameter")
    max_output_tokens: int = Field(2048, description="Maximum number of tokens in output")

    def create_llm(self) -> BaseLanguageModel:
        return ChatGoogleGenerativeAI(
            model=self.model,
            api_key=self.api_key,
        )

class OpenAIConfig(LLMConfig):
    """Configuration for OpenAI models
        Note: DeepSeek also uses the OpenAIConfig with base_url set to api.deepseek.com/v1
    """
    base_url: Optional[str] = Field(None, description="Optional base URL for API endpoint.")

    def create_llm(self) -> BaseLanguageModel:
        kwargs = {
            "model": self.model,
            "api_key": self.api_key,
        }
        if self.base_url:
            kwargs["base_url"] = self.base_url
        return ChatOpenAI(**kwargs)

class AnthropicConfig(LLMConfig):
    """Configuration for Anthropic models"""
    max_tokens: Optional[int] = Field(None, description="Maximum number of tokens to generate")

    def create_llm(self) -> BaseLanguageModel:
        return ChatAnthropic(
            model=self.model,
            api_key=self.api_key
        )

def create_llm_config(model: str, api_key: str, **kwargs) -> LLMConfig:
    """Factory function to create appropriate LLM config based on model name"""
    if model.startswith("gemini"):
        return GeminiConfig(model=model, api_key=SecretStr(api_key), **kwargs)
    elif model.startswith("gpt"):
        return OpenAIConfig(model=model, api_key=SecretStr(api_key), **kwargs)
    elif "claude" in model.lower():
        return AnthropicConfig(model=model, api_key=SecretStr(api_key), **kwargs)
    elif "deepseek" in model.lower():
        return OpenAIConfig(
            model=model,
            api_key=SecretStr(api_key),
            base_url="https://api.deepseek.com/v1",
            **kwargs
        )
    else:
        raise ValueError(f"Unsupported model: {model}")
