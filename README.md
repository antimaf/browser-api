# Browser API

A Flask-based API that provides browser automation capabilities using various LLM models.

## Supported Models
- GPT-4 (OpenAI)
- GPT-3.5 Turbo (OpenAI)
- Claude 3.5 Sonnet (Anthropic)
- DeepSeek
- Gemini (Google)

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
Create a `.env` file with your API keys:
```env
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
DEEPSEEK_API_KEY=your_deepseek_key
GEMINI_API_KEY=your_gemini_key
```

3. Run the server:
```bash
python -m api.main
```

## API Usage

Send POST requests to `/api` with the following JSON body:
```json
{
    "model": "gpt-4o",  // or "gpt-3.5-turbo", "Claude 3.5 Sonnet", "DeepSeek", "Gemini"
    "task": "Your task description",
    "api_key": "your_api_key",  // Optional: if not provided, will use server-side keys
    "headless": true,  // Whether to run browser in headless mode
    "max_steps": 10    // Maximum number of steps for the agent to take
}
```
