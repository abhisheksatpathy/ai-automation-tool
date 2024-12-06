from celery_app import celery_app
from openai import OpenAI
import os
import logging
from io import BytesIO
from azure_storage import upload_audio_to_blob, generate_blob_sas_url

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

key = os.environ['OPENAI_API_KEY']

client = OpenAI(api_key=key)

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
            accumulated_results[node_id] = {'displayedText': text, 'text': text}
        print(f"Display text task completed with result: {accumulated_results[node_id]}")
        return accumulated_results
    except Exception as e:
        print(f"Error in display_text: {str(e)}")
        accumulated_results[node_id] = {'error': str(e)}
        return accumulated_results

@celery_app.task(name='tasks.generate_image')
def generate_image(accumulated_results, node_id, prompt='', previous_node_id=None):
    logger.info(f"Generate image task started with prompt: {prompt}")
    try:
        if not prompt and previous_node_id:
            # Fetch the prompt from the previous node's result
            previous_result = accumulated_results.get(previous_node_id, {})
            prompt = previous_result.get('text', '')
            if not prompt:
                raise ValueError("No prompt found in previous node results.")
            logger.info(f"Using prompt from node {previous_node_id}: {prompt}")
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            n=1,
            size="1024x1024"
        )
        image_url = response.data[0].url
        accumulated_results[node_id] = {'image_url': image_url}
        logger.info(f"Generate image task completed for node {node_id} with image URL: {image_url}")
        return accumulated_results
    except Exception as e:
        logger.error(f"Error in generate_image for node {node_id}: {str(e)}")
        accumulated_results[node_id] = {'error': str(e)}
        return accumulated_results

@celery_app.task(name='tasks.display_image')
def display_image(accumulated_results, node_id, previous_node_id):
    logger.info(f"Display image task started")
    try:
        previous_result = accumulated_results.get(previous_node_id, {})
        if 'error' in previous_result:
            accumulated_results[node_id] = previous_result
        else:
            image_url = previous_result.get('image_url', '')
            accumulated_results[node_id] = {'image_url': image_url}
        logger.info(f"Display image task completed with result: {accumulated_results[node_id]}")
        return accumulated_results
    except Exception as e:
        logger.error(f"Error in display_image: {str(e)}")
        accumulated_results[node_id] = {'error': str(e)}
        return accumulated_results

@celery_app.task(name='tasks.text_to_speech')
def text_to_speech(accumulated_results, node_id, previous_node_id):
    logger.info(f"Text-to-speech task started")
    try:
        previous_result = accumulated_results.get(previous_node_id, {})
        text = previous_result.get('text', '')
        if not text:
            raise ValueError("No text found in previous node results.")

        # Save the audio file to a BytesIO stream
        audio_stream = BytesIO()

        with client.audio.speech.with_streaming_response.create(
                model="tts-1",
                voice="echo",
                input=text,
                response_format="mp3"  # You can also use "pcm" if needed
        ) as response:
            for chunk in response.iter_bytes(1024):
                audio_stream.write(chunk)

        audio_stream.seek(0)

        # Upload to Azure Blob Storage
        filename = upload_audio_to_blob(audio_stream)

        #Generate the URL to access the audio file
        audio_url = generate_blob_sas_url(filename)

        accumulated_results[node_id] = {'audio_url': audio_url}
        logger.info("Text-to-speech task completed")
        return accumulated_results
    except Exception as e:
        logger.error(f"Error in text_to_speech: {str(e)}")
        accumulated_results[node_id] = {'error': str(e)}
        return accumulated_results

@celery_app.task(name='tasks.start_workflow')
def start_workflow():
    # Initialize the accumulated results dictionary
    return {}
