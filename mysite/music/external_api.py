import requests
import time

API_URL = "https://api.assemblyai.com/v2/upload"
TRANSCRIBE_URL = "https://api.assemblyai.com/v2/transcript"
API_KEY = '01a3cf9455834789b39df72e5828c12b' 

def upload_mp3_to_assemblyai(file_path):
    headers = {'authorization': API_KEY}
    with open(file_path, 'rb') as f:
        response = requests.post(API_URL, headers=headers, files={'file': f})
    return response.json()['upload_url']

def get_transcription(upload_url):
    headers = {'authorization': API_KEY, 'content-type': 'application/json'}
    transcript_request = {'audio_url': upload_url}
    response = requests.post(TRANSCRIBE_URL, json=transcript_request, headers=headers)
    transcript_id = response.json()['id']

    # Polling for the transcription result
    while True:
        transcript_response = requests.get(f"{TRANSCRIBE_URL}/{transcript_id}", headers=headers)
        transcript_data = transcript_response.json()

        if transcript_data['status'] == 'completed':
            return transcript_data['text']
        elif transcript_data['status'] == 'failed':
            return None

        time.sleep(5)
