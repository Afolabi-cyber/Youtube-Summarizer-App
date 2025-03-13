from flask import Flask, render_template, request, jsonify
import requests
from youtube_transcript_api import YouTubeTranscriptApi
from google import genai

app = Flask(__name__)

# Initialize Gemini AI client
client = genai.Client(api_key="YOUR_API_KEY")

# Define the summarization prompt
def get_summarization_prompt(transcript):
    return f"""
    You are an AI assistant that specializes in summarizing YouTube video transcripts. 
    Please provide a clear, concise, and informative summary of the following transcript:
    {transcript}
    """

def summarize_text(text):
    try:
        prompt = get_summarization_prompt(text)
        response = client.models.generate_content(
            model="gemini-2.0-flash", contents=prompt
        )
        return response.text
    except Exception as e:
        return f"Gemini AI summarization failed: {str(e)}"

# Extract video ID from YouTube link
def get_video_id(url):
    if "youtube.com" in url:
        return url.split("v=")[-1].split("&")[0]
    elif "youtu.be" in url:
        return url.split("/")[-1]
    return None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        video_url = request.form['video_url']
        video_id = get_video_id(video_url)
        if not video_id:
            return jsonify({"error": "Invalid YouTube URL"})
        
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            full_text = " ".join([t["text"] for t in transcript])
            summary = summarize_text(full_text)
            return jsonify({"summary": summary})
        except Exception as e:
            return jsonify({"error": str(e)})
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
