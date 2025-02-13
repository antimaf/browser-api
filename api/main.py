#Server dependencies
from flask import Flask, request, jsonify
from flask_cors import CORS

#Local imports
from handlers.agenthandler import AgentHandler

app = Flask(__name__)
CORS(app)

@app.route('/api', methods=['POST'])
async def api():
    """
    API endpoint to execute a browser-use agent.

    Request body should contain the following fields:
    - model: str, the model to use
    - task: str, the task description
    - api_key: str, the API key for the model
    - headless: bool, whether to run the browser in headless mode
    - max_steps: int, the maximum number of steps to take in the agent

    Returns the result from the agent after processing the task.
    """
    data = request.json
    model, task, api_key, headless, max_steps = data['model'], data['task'], data['api_key'], data['headless'], data['max_steps']
    agent_handler = AgentHandler(task, api_key, model, headless, max_steps)
    return await agent_handler.execute()

if __name__ == '__main__':
    app.run(debug=True)
