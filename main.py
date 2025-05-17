import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, Response, url_for, redirect
import PyPDF2

app = Flask(__name__)

load_dotenv()

extracted_text = ""

@app.route("/", methods=["POST", "GET"])
def home():
    if request.method == "POST":
        file = request.files.get("file")

        if not file or file.filename == "":
            return "No file selected"

        if file.filename.lower().endswith(".pdf"):
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                global extracted_text
                extracted_text = page.extract_text()

    return render_template("index.html", text=extracted_text)

@app.route("/generate_audio", methods=["POST", "GET"])
def generate_audio():
    import boto3

    # Initialize Polly client
    polly = boto3.client(
        'polly',
        region_name='us-east-1',
        aws_access_key_id=os.environ.get("AMAZON_ACCESS_KEY"),
        aws_secret_access_key=os.environ.get("AMAZON_SECRET_KEY")
    )

    # Generate speech
    response = polly.synthesize_speech(
        Text=extracted_text,
        OutputFormat='mp3',
        VoiceId='Joanna'
    )

    # Read the audio stream and send it to the browser
    audio_stream = response['AudioStream'].read()
    return Response(audio_stream, mimetype='audio/mpeg')


if __name__ == "__main__":
    app.run(debug=True)