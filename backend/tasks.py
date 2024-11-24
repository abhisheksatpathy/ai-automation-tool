## backend/tasks.py
#
#from celery_app import celery_app
#import openai
#import os
#from dotenv import load_dotenv
#from time import sleep
#from random import uniform
#
#load_dotenv()
#
## Set the OpenAI API key
#openai.api_key = os.getenv('OPENAI_API_KEY')
#
#def exponential_backoff(attempt, max_attempts=3, base_delay=1):
#    if attempt >= max_attempts:
#        return False
#    delay = base_delay * (2 ** attempt) + uniform(0, 0.1)
#    sleep(delay)
#    return True
#
#@celery_app.task(name='tasks.generate_text')
#def generate_text(prompt=''):
#    print(f"Generate text task started with prompt: {prompt}")
#    try:
#        response = openai.ChatCompletion.create(
#            model="gpt-3.5-turbo",
#            messages=[{"role": "user", "content": prompt}]
#        )
#        result = {'text': response['choices'][0]['message']['content']}
#        print(f"Generate text task completed with result: {result}")
#        return result
#    except Exception as e:
#        print(f"Error in generate_text: {str(e)}")
#        return {'error': str(e)}
#
#@celery_app.task(name='tasks.display_text')
#def display_text(previous_result):
#    print(f"Display text task started with input: {previous_result}")
#    try:
#        if isinstance(previous_result, dict):
#            if 'error' in previous_result:
#                return previous_result
#            text = previous_result.get('text', '')
#        else:
#            text = str(previous_result) if previous_result else ''
#        
#        result = {'displayedText': text}
#        print(f"Display text task completed with result: {result}")
#        return result
#    except Exception as e:
#        print(f"Error in display_text: {str(e)}")
#        return {'error': str(e)}
#

# backend/tasks.py

# backend/tasks.py

from celery_app import celery_app
import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

@celery_app.task(name='tasks.generate_text')
def generate_text(accumulated_results, node_id, prompt=''):
    print(f"Generate text task started with prompt: {prompt}")
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        text = response.choices[0].message['content']
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
