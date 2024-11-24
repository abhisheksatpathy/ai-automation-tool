## backend/workflow_executor.py
#
#from celery import chain
#from typing import Dict, Any
#from tasks import generate_text, display_text
#from celery_app import celery_app
#
#TASK_MAPPING = {
#    'generateText': generate_text,
#    'displayText': display_text,
#}
#
#def execute_workflow(workflow: Dict[str, Any]):
#    try:
#        print(f"Starting workflow execution with {len(workflow['blocks'])} blocks")
#
#        task_signatures = []  # List to hold task signatures
#
#        # Process blocks in the order they appear
#        for block in workflow['blocks']:
#            task_type = block['type']
#            data = block.get('data', {})
#
#            # Get the task function
#            task_func = TASK_MAPPING.get(task_type)
#            if not task_func:
#                raise ValueError(f"Unknown task type: {task_type}")
#
#            # Prepare the task signature
#            if task_type == 'generateText':
#                prompt = data.get('prompt', '')
#                task_sig = task_func.s(prompt=prompt)
#                print(f"Prepared generate_text task with prompt: {prompt}")
#            elif task_type == 'displayText':
#                task_sig = task_func.s()
#                print(f"Prepared display_text task")
#            else:
#                raise ValueError(f"Unknown task type: {task_type}")
#
#            task_signatures.append(task_sig)
#
#        if not task_signatures:
#            raise ValueError("No tasks to execute in the workflow")
#
#        # Chain the tasks explicitly using chain()
#        tasks_chain = chain(*task_signatures)
#
#        # Execute the chain of tasks asynchronously
#        result = tasks_chain.apply_async()
#        print(f"Workflow started with task_id: {result.id}")
#        return result  # This is an AsyncResult with an id
#
#    except Exception as e:
#        print(f"Workflow execution failed: {str(e)}")
#        raise
#
#def get_task_status(task_id: str) -> Dict[str, Any]:
#    """Get the status of a task by its ID."""
#    try:
#        result = celery_app.AsyncResult(task_id)
#        print(f"Checking task {task_id} status: {result.state}")
#        
#        if result.ready():
#            if result.successful():
#                task_result = result.get()
#                print(f"Task completed successfully: {task_result}")
#                return {
#                    'state': 'SUCCESS',
#                    'result': task_result
#                }
#            else:
#                error = str(result.result)
#                print(f"Task failed with error: {error}")
#                return {
#                    'state': 'FAILURE',
#                    'error': error
#                }
#        else:
#            print(f"Task {task_id} is {result.state}")
#            return {
#                'state': result.state
#            }
#    except Exception as e:
#        print(f"Error getting task status: {str(e)}")
#        return {
#            'state': 'FAILURE',
#            'error': str(e)
#        }
# backend/workflow_executor.py

# backend/workflow_executor.py

from celery import chain
from typing import Dict, Any
from tasks import generate_text, display_text, start_workflow
from celery_app import celery_app  # Ensure this is used

TASK_MAPPING = {
    'generateText': generate_text,
    'displayText': display_text,
}

def execute_workflow(workflow: Dict[str, Any]):
    try:
        print(f"Starting workflow execution with {len(workflow['blocks'])} blocks")

        # Start with the initial task that initializes accumulated_results
        tasks_chain = start_workflow.s()
        previous_node_id = None  # To keep track of the previous node's ID

        # Process blocks in the order they appear
        for block in workflow['blocks']:
            node_id = block['id']
            task_type = block['type']
            data = block.get('data', {})

            task_func = TASK_MAPPING.get(task_type)
            if not task_func:
                raise ValueError(f"Unknown task type: {task_type}")

            # Prepare the task signature
            if task_type == 'generateText':
                prompt = data.get('prompt', '')
                task_sig = task_func.s(node_id=node_id, prompt=prompt)
                print(f"Prepared generate_text task with prompt: {prompt}")
            elif task_type == 'displayText':
                if previous_node_id is None:
                    raise ValueError("displayText task requires a previous node")
                task_sig = task_func.s(node_id=node_id, previous_node_id=previous_node_id)
                print(f"Prepared display_text task")
            else:
                raise ValueError(f"Unknown task type: {task_type}")

            # Chain the tasks using the '|' operator
            tasks_chain = tasks_chain | task_sig
            previous_node_id = node_id  # Update the previous node ID

        # Execute the chain of tasks asynchronously
        result = tasks_chain.apply_async()
        print(f"Workflow started with task_id: {result.id}")
        return result  # This is a Celery AsyncResult with an ID

    except Exception as e:
        print(f"Workflow execution failed: {str(e)}")
        raise

def get_task_status(task_id: str) -> Dict[str, Any]:
    """Get the status of a task by its ID."""
    try:
        result = celery_app.AsyncResult(task_id)
        print(f"Checking task {task_id} status: {result.state}")

        if result.ready():
            if result.successful():
                task_result = result.get()
                print(f"Task completed successfully: {task_result}")
                return {
                    'state': 'SUCCESS',
                    'result': task_result
                }
            else:
                error = str(result.result)
                print(f"Task failed with error: {error}")
                return {
                    'state': 'FAILURE',
                    'error': error
                }
        else:
            print(f"Task {task_id} is {result.state}")
            return {
                'state': result.state
            }
    except Exception as e:
        print(f"Error getting task status: {str(e)}")
        return {
            'state': 'FAILURE',
            'error': str(e)
        }
