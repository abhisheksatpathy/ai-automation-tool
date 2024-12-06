from celery import chain
from typing import Dict, Any
from tasks import generate_text, display_text, generate_image, display_image, text_to_speech, start_workflow
from celery_app import celery_app  
from collections import defaultdict, deque
import logging

TASK_MAPPING = {
    'generateText': generate_text,
    'displayText': display_text,
    'generateImage': generate_image,
    'displayImage': display_image,
    'textToSpeech': text_to_speech
}

logger = logging.getLogger(__name__)

def build_dependency_graph(blocks: list, edges: list) -> Dict[str, list]:
    """
    Builds a dependency graph where each key is a node_id and the value is a list of node_ids that depend on it.
    """
    graph = defaultdict(list)
    in_degree = defaultdict(int)
    
    # Initialize in_degree for all nodes
    for block in blocks:
        node_id = block['id']
        in_degree[node_id] = 0
    
    # Build graph and compute in-degrees
    for edge in edges:
        source = edge['source']
        target = edge['target']
        graph[source].append(target)
        in_degree[target] += 1
    
    return graph, in_degree

def topological_sort(blocks: list, edges: list) -> list:
    """
    Performs topological sorting on the dependency graph.
    Returns a list of node_ids in the order they should be executed.
    """
    graph, in_degree = build_dependency_graph(blocks, edges)
    queue = deque([node for node in in_degree if in_degree[node] == 0])
    sorted_order = []
    
    while queue:
        node = queue.popleft()
        sorted_order.append(node)
        
        for neighbor in graph[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
    
    if len(sorted_order) != len(blocks):
        raise ValueError("Cycle detected in workflow dependencies.")
    
    return sorted_order

def get_block_by_id(blocks: list, node_id: str) -> Dict[str, Any]:
    """
    Retrieves a block dictionary by its node_id.
    """
    for block in blocks:
        if block['id'] == node_id:
            return block
    raise ValueError(f"Block with id {node_id} not found.")

def execute_workflow(workflow: Dict[str, Any]):
    try:
        blocks = workflow.get('blocks', [])
        edges = []

        for block in blocks:
            node_id = block['id']
            inputs = block.get('inputs', {})
            for input_key, source_node_id in inputs.items():
                edges.append({
                    'source': source_node_id,
                    'target': node_id
                })
        
        logger.info(f"Starting workflow execution with {len(blocks)} blocks")

        # Perform topological sort to determine execution order
        execution_order = topological_sort(blocks, edges)
        logger.info(f"Execution order: {execution_order}")

        # Start with the initial task that initializes accumulated_results
        tasks_chain = start_workflow.s()

        # Map to store task signatures by node_id
        task_signatures = {}

        # Process blocks in the order they appear
        for node_id in execution_order:
            block = get_block_by_id(blocks, node_id)
            task_type = block['type']
            data = block.get('data', {})
            #inputs = block.get('inputs', {})
            task_func = TASK_MAPPING.get(task_type)
            if not task_func:
                raise ValueError(f"Unknown task type: {task_type}")

            # Prepare the task signature
            if task_type == 'generateText':
                prompt = data.get('prompt', '')
                task_sig = task_func.s(node_id=node_id, prompt=prompt)
                logger.info(f"Prepared generate_text task for node {node_id} with prompt: {prompt}")
            elif task_type == 'displayText':
                previous_node_id = block['inputs'].get('input')
                if previous_node_id is None:
                    raise ValueError("displayText task requires a previous node")
                task_sig = task_func.s(node_id=node_id, previous_node_id=previous_node_id)
                logger.info(f"Prepared display_text task for node {node_id} dependent on {previous_node_id}")
            elif task_type == 'generateImage':
                prompt = data.get('prompt', '')
                if not prompt:
                    previous_node_id = block['inputs'].get('input')
                    if not previous_node_id:
                        raise ValueError("generateImage task requires a prompt or a previous node")
                    task_sig = task_func.s(node_id=node_id, prompt=None, previous_node_id=previous_node_id)
                    logger.info(f"Prepared generate_image task for node {node_id} dependent on {previous_node_id}")
                else:
                    task_sig = task_func.s(node_id=node_id, prompt=prompt)
                    logger.info(f"Prepared generate_image task for node {node_id} with prompt: {prompt}")
            elif task_type == 'displayImage':
                previous_node_id = block['inputs'].get('input')
                if not previous_node_id:
                    raise ValueError("displayImage task requires a previous node")
                task_sig = task_func.s(node_id=node_id, previous_node_id=previous_node_id)
                logger.info(f"Prepared display_image task for node {node_id} dependent on {previous_node_id}")
            elif task_type == 'textToSpeech':
                previous_node_id = block['inputs'].get('input')
                if not previous_node_id:
                    raise ValueError("textToSpeech task requires a previous node")
                task_sig = task_func.s(node_id=node_id, previous_node_id=previous_node_id)
                logger.info(f"Prepared text_to_speech task for node {node_id} dependent on {previous_node_id}")
            else:
                raise ValueError(f"Unknown task type: {task_type}")
            
            task_signatures[node_id] = task_sig

        for node_id in execution_order:
            tasks_chain = tasks_chain | task_signatures[node_id]

        # Execute the chain of tasks asynchronously
        result = tasks_chain.apply_async()
        logger.info(f"Workflow started with task_id: {result.id}")
        return result  # This is a Celery AsyncResult with an ID

    except Exception as e:
        logger.error(f"Workflow execution failed: {str(e)}")
        raise

def get_task_status(task_id: str) -> Dict[str, Any]:
    """Get the status of a task by its ID."""
    try:
        result = celery_app.AsyncResult(task_id)
        logger.info(f"Checking task {task_id} status: {result.state}")

        if result.ready():
            if result.successful():
                task_result = result.get()
                logger.info(f"Task completed successfully: {task_result}")
                return {
                    'state': 'SUCCESS',
                    'result': task_result
                }
            else:
                error = str(result.result)
                logger.error(f"Task failed with error: {error}")
                return {
                    'state': 'FAILURE',
                    'error': error
                }
        else:
            logger.info(f"Task {task_id} is {result.state}")
            return {
                'state': result.state
            }
    except Exception as e:
        logger.error(f"Error getting task status: {str(e)}")
        return {
            'state': 'FAILURE',
            'error': str(e)
        }
