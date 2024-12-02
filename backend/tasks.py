from celery_app import celery_app
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv['OPENAI_API_KEY'])

@celery_app.task(name='tasks.generate_text')
def generate_text(accumulated_results, node_id, prompt=''):
    print(f"Generate text task started with prompt: {prompt}")
    try:
        response = client.chat.completions.create(model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}])
        text = response.choices[0].message.content
        accumulated_results[node_id] = {'text': text}
        print(f"Generate text task completed with result: {text}")
        return accumulated_results
    except Exception as e:
        print(f"Error in generate_text: {str(e)}")
        accumulated_results[node_id] = {'error': str(e)}
        return accumulated_results

@celery_app.task(name='tasks.display_text')
def display_text(accumulated_results, node_id, previous_node_id):
    print(f"Display text task started")
    try:
        previous_result = accumulated_results.get(previous_node_id, {})
        if 'error' in previous_result:
            accumulated_results[node_id] = previous_result
        else:
            text = previous_result.get('text', '')
            accumulated_results[node_id] = {'displayedText': text}
        print(f"Display text task completed with result: {accumulated_results[node_id]}")
        return accumulated_results
    except Exception as e:
        print(f"Error in display_text: {str(e)}")
        accumulated_results[node_id] = {'error': str(e)}
        return accumulated_results

@celery_app.task(name='tasks.start_workflow')
def start_workflow():
    # Initialize the accumulated results dictionary
    return {}
