import os
import tempfile
import json
import logging
from openai import OpenAI

# Initialize OpenAI client
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai = OpenAI(api_key=OPENAI_API_KEY)

logger = logging.getLogger(__name__)

def transcribe_audio(audio_file_path):
    """
    Transcribe the given audio file using OpenAI Whisper.
    
    Args:
        audio_file_path (str): Path to the audio file
        
    Returns:
        str: Transcribed text
    """
    try:
        logger.debug(f"Transcribing audio file: {audio_file_path}")
        with open(audio_file_path, "rb") as audio_file:
            response = openai.audio.transcriptions.create(
                model="whisper-1", 
                file=audio_file
            )
        return response.text
    except Exception as e:
        logger.error(f"Error transcribing audio: {str(e)}")
        raise Exception(f"Failed to transcribe audio: {str(e)}")

def generate_meeting_summary(transcript):
    """
    Generate a structured summary of the meeting transcript using OpenAI GPT-3.5-turbo. This works
    
    Args:
        transcript (str): The meeting transcript
        
    Returns:
        dict: A dictionary containing summary, decisions, and action items
    """
    try:
        logger.debug("Generating meeting summary")
        
        prompt = f"""
        You are an AI assistant specialized in summarizing software engineering meetings.
        Analyze the following meeting transcript and provide a structured response in JSON format with no additional text:

        1. Create a concise summary of the key topics discussed (limit to 400 words).
        2. Extract all decisions made during the meeting.
        3. Extract all action items and tasks, including who is responsible and deadlines if mentioned.

        Format your response as a JSON object with these keys:
        - summary: The meeting summary.
        - decisions: An array of decisions made.
        - action_items: An array of action items with assignee and deadline if available.

        Meeting Transcript:
        {transcript}

        Your answer should be only JSON.
        """
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a software engineering meeting assistant that extracts key information from meeting transcripts."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )
        
        # Debug: Print raw output
        raw_output = response.choices[0].message.content
        #print("Raw response from model:")
        #print(raw_output)
        
        # Attempt to extract JSON from the raw output
        import re
        json_str_match = re.search(r'\{.*\}', raw_output, re.DOTALL)
        if json_str_match:
            json_str = json_str_match.group(0)
            result = json.loads(json_str)
        else:
            raise Exception("Failed to extract JSON from the response.")

        return result
    except Exception as e:
        logger.error(f"Error generating meeting summary: {str(e)}")
        raise Exception(f"Failed to generate meeting summary: {str(e)}")
