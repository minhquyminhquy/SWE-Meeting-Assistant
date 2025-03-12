import torch
from PIL import Image
from fastapi import FastAPI, UploadFile, Form
from transformers import (
    Blip2Processor, 
    Blip2ForConditionalGeneration,
    WhisperProcessor, 
    WhisperForConditionalGeneration,
    pipeline
)

app = FastAPI()

# Initialize models
device = "cuda" if torch.cuda.is_available() else "cpu"

# Image processing model
blip_processor = Blip2Processor.from_pretrained("Salesforce/blip2-opt-2.7b")
blip_model = Blip2ForConditionalGeneration.from_pretrained(
    "Salesforce/blip2-opt-2.7b", load_in_8bit=True, device_map="auto"
)

# Audio processing model
whisper_processor = WhisperProcessor.from_pretrained("openai/whisper-small")
whisper_model = WhisperForConditionalGeneration.from_pretrained(
    "openai/whisper-small"
).to(device)

# Text summarization pipeline
summarizer = pipeline(
    "summarization",
    model="philschmid/flan-t5-base-samsum",
    device=0 if device == "cuda" else -1
)

def process_audio(audio_file):
    # Convert audio to text using Whisper
    audio_input = whisper_processor(
        audio_file.read(), 
        sampling_rate=16000, 
        return_tensors="pt"
    ).input_values.to(device)
    
    predicted_ids = whisper_model.generate(audio_input)
    transcript = whisper_processor.batch_decode(predicted_ids, skip_special_tokens=True)
    return transcript[0]

def process_image(image_file):
    # Process image with BLIP-2
    raw_image = Image.open(image_file).convert("RGB")
    inputs = blip_processor(raw_image, return_tensors="pt").to(device)
    
    generated_ids = blip_model.generate(**inputs, max_new_tokens=100)
    description = blip_processor.batch_decode(generated_ids, skip_special_tokens=True)
    return description[0]

def generate_summary(texts):
    # Combine and summarize information
    combined_text = "\n".join(texts)
    
    # Structured summary prompt
    prompt = f"""Generate structured meeting summary with these sections:
    1. Key Decisions
    2. Action Items
    3. Technical Insights
    4. Next Steps
    
    Input: {combined_text}
    Summary:"""
    
    summary = summarizer(
        prompt,
        max_length=500,
        do_sample=True,
        temperature=0.7,
    )[0]['summary_text']
    
    return summary

@app.post("/process_meeting")
async def process_meeting(
    audio: UploadFile = None,
    images: list[UploadFile] = None,
    text: str = Form(None)
):
    processed_texts = []
    
    if audio:
        processed_texts.append(f"Audio Transcript: {process_audio(audio.file)}")
        
    if images:
        for image in images:
            img_text = process_image(image.file)
            processed_texts.append(f"Image Description: {img_text}")
    
    if text:
        processed_texts.append(f"Additional Notes: {text}")
    
    summary = generate_summary(processed_texts)
    
    return {
        "transcript": "\n".join(processed_texts),
        "summary": summary
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)