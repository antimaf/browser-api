#imports
import os
from typing import Optional
import asyncio
from flask import jsonify
from pydantic import SecretStr

from browser_use import Agent
from browser_use.controller import Controller

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI

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
    '''
    def __init__(self, task: str, api_key: Optional[str], model: str, headless: bool, max_steps: int):
        self.task = task
        self.api_key = api_key
        self.model = model
        self.headless = headless
        self.max_steps = max_steps
    
    async def execute(self) -> str:
        """
        Handles the interaction with the language model based on the specified task and model type.

        Returns:
            str: The result from the agent after processing the task. 
                 Returns an error message if the model is unsupported or the API key is missing.
        """
        logger.info(f"Executing task: {self.task}, model: {self.model}, headless: {self.headless}, max_steps: {self.max_steps}")
        SERVER_API_KEYS = {
            "gpt-4o": os.getenv('OPENAI_API_KEY'),  # OpenAI API key for GPT-4
            "gpt-3.5-turbo": os.getenv('OPENAI_API_KEY'),  # OpenAI API key for GPT-3.5
            "Claude 3.5 Sonnet": os.getenv('ANTHROPIC_API_KEY'),  # Anthropic API key for Claude
            "DeepSeek": os.getenv('DEEPSEEK_API_KEY'),  # DeepSeek API key
            "Gemini": os.getenv('GEMINI_API_KEY'),  # Gemini API key
        }
        
        # Use provided API key if available, otherwise fall back to server API keys
        api_key_to_use = self.api_key if self.api_key else SERVER_API_KEYS.get(self.model)
        if api_key_to_use is None:
            return jsonify({"error": f"No API key available for model: {self.model}"}), 400

        match self.model:
            case 'gpt-4o' | 'gpt-3.5-turbo':
                llm = ChatOpenAI(model=self.model, api_key=SecretStr(api_key_to_use))
            case 'Claude 3.5 Sonnet':
                llm = ChatAnthropic(model_name='claude-3-5-sonnet-20240620', api_key=SecretStr(api_key_to_use), timeout=100, stop=None, temperature=0.0)
            case 'DeepSeek':
                llm = ChatOpenAI(model='DEEPSEEK-CHAT', api_key=SecretStr(api_key_to_use))
            case 'Gemini':
                llm = ChatGoogleGenerativeAI(model='gemini-2.0-flash-exp', api_key=SecretStr(api_key_to_use))
            case _:
                return jsonify({"error": f"Unsupported model: {self.model}"}), 400
                
        agent = Agent(
            task=self.task,
            llm=llm,
            max_actions_per_step=4,
        )
        
        try:
            history = await agent.run(max_steps=self.max_steps)
            logger.info('Agent completed successfully')
            return history
        except Exception as e:
            logger.error(f"Error during task execution: {str(e)}")
            return str(e)
