# Installation Guide

## Prerequisites
- Python 3.11+
- Playwright
- Virtual Environment (recommended)

## Installation Steps

1. Clone the repository:
```bash
git clone https://github.com/antimaf/browser-api.git
cd browser-api
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

Create a `.env` file with your configuration:

```env
API_KEY=your_api_key
TEST_USERNAME=test_user  # For login example
TEST_PASSWORD=test_pass  # For login example
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
DEEPSEEK_API_KEY=your_deepseek_key
GEMINI_API_KEY=your_gemini_key
```

## Running the Server

Start the API server:
```bash
python -m api.main
```

The server will start on `http://localhost:5001` by default.

## Quick Start

1. Start the API server:
```bash
python -m api.main
```

2. Run an example script:
```bash
python -m examples.google_search
```
