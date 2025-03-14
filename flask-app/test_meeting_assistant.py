import os
import json
import logging
from openai import OpenAI

# Initialize OpenAI client
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise EnvironmentError("Please set the OPENAI_API_KEY environment variable.")

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
        print("Raw response from model:")
        print(raw_output)
        
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


if __name__ == "__main__":
    audio_path = r"D:\Coursework\COMP.CS.530 FineTuneLLM\Capstone Project - Git\uploads\1c66328b-5518-4723-9d6d-5b9ee18d0836.mp3"
    #transcript = transcribe_audio(audio_path)
    transcript ="""Hi, everyone, this is the March field and PM monthly for the Sec section. Sarah, you have a lot of great updates, you want to go ahead and get us going? So with the 18.0 release, we're introducing time-based data retention limits for vulnerabilities for .com customers. So this will not impact dedicated or self-managed customers. But for .com customers, this is really important to make sure your customers are aware. If vulnerabilities haven't been updated in 12 months, they will go into an archive for up to three years. And then after three years, that data will get deleted. By doing this, we expect to have quite a few performance improvements that will help in general with the vulnerability report. So that we'll be able to add more filters and make all of the data just easier for customers to use. We're expecting communication to the field to go out later this week and to customers as well. The sort of 18.0 breaking change notice did go out. So why doesn't it impact self-managed? Because it's a setting you can set yourself? Yeah, I mean, the scalability problems that exist with the vulnerability report today impact .com customers. Because self-managed customers can control their own infrastructure. But get lab.com customers have no control over. Yeah, so the main goal there is just to improve performance for everybody who's using the platform. I see the next topic and it's a question in my RFP. Cool. I'll jump to that one. Then Mirko, unless anybody has questions or comments, feel free to interrupt. I have a question. I just because this is such a big change. Do you have how is this being communicated to customers to make sure they're not caught off guard? So we do have a communication plan. Marketing has already written up communication and the email is ready to go. Marketing also kind of put a hold on sending that out because it's a large department. And there were folks who wanted more of a field guide, which is why it's gotten delayed a little bit. But we're hoping to get the communication out this week via email. And so it's basically email the customers and then email and Slack notifications to field teams and a field guide. Awesome. All right. One B. So vulnerability severity overrides are live on get lab.com and going out with this month's release. So basically, if you can change the status of a vulnerability, you can also override its severity. And this applies for all scanner results. So is this on a result or is this something where you can change it for definition, like that a certain vulnerability does not have CVS 98, but 78 or whatever. So in the configuration file or does it mean override of results? It's an override of the result. So you would go to the vulnerability report, see the result. And then from the vulnerability report itself or from the vulnerability details page, you'd be able to change the severity. And it's pretty manual. We do imagine that customers are going to want a more automated way to do it. They can use the API. So we do have a large customer who's using the API to automate this. But in terms of being able to automate it within the product, there's a separate issue related to kind of creating a security policy that would allow you to take different parameters and use those to change the severity. So, OK, then it's nothing that you can preset for a group. That's what I wanted to know. Yep, that's right. The reason it was built this way was to meet a contractual obligation to a large customer. Are we thinking about configuration file for this? Not currently. I mean, I think it sounds like you're talking about custom rules. So I think my team built this feature to meet the contractual obligation. But going forward, if we wanted to create custom rules for this, that would potentially relate to my team or scanner teams, application security testing teams. And then there is a thought that a security policy could be used, like I said, which would be similar to maybe creating a custom rule. Because you're basically wanting to automate things, right? I guess from your perspective, is there a difference between writing a rule and being able to update the severity within the rule versus, you know, overriding it at the end once the scanner is already run, but if it's still automated? Yeah, no, just thinking about having things set up on a group level. I just got this question and then this would, yeah, I don't know. So it might only be for a limited space in GitLab or limit like a group. I don't know. So I just got questions back from my RFP answers and then I don't know all the options they have in mind, but they say something like changing severity levels on group level. So I think this doesn't mean manual override. But I'm not 100% sure. Yeah, I don't think there, I mean, with the policy route, there'd probably be a way to scope it at a group level. But with the API, there's nothing related to scoping anything at a level. It would just be applicable to like all vulnerabilities. Yeah, but yeah, with the policy, I don't know how you would change that. But maybe I haven't thought it through yet. So I come back with that question to you, I guess. Thank you. I guess moving on to C, we also have for UI configured DAST scans or on-demand DAST scans, they're now more usable because in the past there was a limited set of variables that could be used, which made them challenging to use. But now they can, although the CI variables that would be available to you in a YAML file are available via the UI as well. But do they know if it's DAST4 or DAST5 because there's been a big change? I thought I had all CI variables for DAST5 in it. But I mean, DAST is changing all the time, so I don't know what it's like today. Yeah, this change happened, I think, in the February release. So it should be applicable to the latest DAST version. DAST4 was basically, I mean, it's not the major version anymore, right? DAST5 came out in 17.0? I need to recheck that really all the things are there because I haven't seen all of them. Okay. And I think I'll move the other two topics to the private section. Did you still want to chat about C, Sarah? Oh, we just were chatting about that one. Oh, you did make it through that one. Okay. All right. I'm going to go ahead and stop the recording."""

    print("Transcript:")
    print(transcript)
    
    meeting_summary = generate_meeting_summary(transcript)
    print("Meeting Summary:")
    print(meeting_summary)
