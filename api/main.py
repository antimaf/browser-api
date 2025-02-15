''' Main API entry point for the browser automation service '''

import sys
import os

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

#External dependencies
from quart import Quart, jsonify, request
from quart_cors import cors
import os
from datetime import datetime, timedelta
from functools import wraps
from typing import Dict, Optional

#Local imports
from handlers.agenthandler import AgentHandler
from handlers.taskmanager import task_manager
from models.browser import AutomationScript
from config.logging import setup_logging

app = Quart(__name__)
app = cors(app)
app = setup_logging(app)

# Simple API key verification
def require_api_key(f):
    @wraps(f)
    async def decorated(*args, **kwargs):
        if app.debug:  # Skip API key check in debug mode
            return await f(*args, **kwargs)
        api_key = request.headers.get('X-API-Key')
        if not api_key or api_key != os.getenv('API_KEY'):
            return jsonify({"error": "Invalid API key"}), 401
        return await f(*args, **kwargs)
    return decorated

@app.route('/api/status', methods=['GET'])
async def api_status():
    """Get API service status"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    })

@app.route('/api/tasks', methods=['POST'])
@require_api_key
async def create_task():
    """Create and execute a new browser task"""
    try:
        data = await request.get_json()
        print(f"Received task data: {data}")  # Debug log
        
        task_id = task_manager.generate_task_id()
        task_manager.register_task(task_id)
        
        agent_handler = AgentHandler(
            task=data['task'],
            api_key=data['api_key'],
            model=data['model'],
            headless=data.get('headless', True),
            max_steps=data.get('max_steps', 10)
        )
        result = await agent_handler.execute()
        task_manager.complete_task(task_id, result)
        return jsonify({"task_id": task_id, "status": "completed", "result": result})
    except Exception as e:
        import traceback
        print(f"Error creating task: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")  # Debug log
        if 'task_id' in locals():
            task_manager.fail_task(task_id, str(e))
        return jsonify({"error": str(e)}), 500

@app.route('/api/tasks/<task_id>', methods=['GET'])
@require_api_key
async def get_task_status(task_id):
    """Get status of a specific task"""
    task = task_manager.get_task(task_id)
    if task:
        return jsonify(task)
    return jsonify({"error": "Task not found"}), 404

@app.route('/api/tasks', methods=['GET'])
@require_api_key
async def list_tasks():
    """List all tasks"""
    tasks = task_manager.list_tasks()
    return jsonify(tasks)

@app.route('/api/tasks/<task_id>/cancel', methods=['POST'])
@require_api_key
async def cancel_task(task_id):
    """Cancel a running task"""
    success = task_manager.cancel_task(task_id)
    if success:
        return jsonify({"status": "cancelled"})
    return jsonify({"error": "Task not found or already completed"}), 404

@app.route('/api/tasks/script', methods=['POST'])
@require_api_key
async def create_script_task():
    """Create and execute a task using a predefined automation script"""
    try:
        data = await request.get_json()
        task_id = task_manager.generate_task_id()
        task_manager.register_task(task_id)
        
        # Create agent handler with script
        agent_handler = AgentHandler(
            task=data['task'],
            api_key=data.get('api_key'),
            model=data.get('model', 'gpt-4'),
            headless=data.get('headless', True),
            max_steps=data.get('max_steps', 10),
            script=AutomationScript(**data['script']),  # Convert dict to AutomationScript
            variables=data.get('variables'),
            screenshot_dir=data.get('screenshot_dir'),
            record_video=data.get('record_video', False),
            debug_mode=data.get('debug_mode', False)
        )
        
        # Execute the script
        result = await agent_handler.execute_script()
        task_manager.complete_task(task_id, result)
        
        return jsonify({
            "task_id": task_id,
            "status": "completed",
            "result": result,
            "screenshots": agent_handler.screenshots,
            "video_path": agent_handler.video_path,
            "execution_log": agent_handler.execution_log
        })
        
    except Exception as e:
        import traceback
        print(f"Error executing script task: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        if 'task_id' in locals():
            task_manager.fail_task(task_id, str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)
