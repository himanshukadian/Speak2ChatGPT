import os

import requests
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from gtts import gTTS
from io import BytesIO
import speech_recognition as sr


api_key = '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'  # Replace with your actual API key

@csrf_exempt
def voice_input(request):
    if request.method == 'POST':
        # Check if the voice file is present in the request
        print(request.FILES)
        if 'voice_file' not in request.FILES:
            return HttpResponse("File not present!!!")

        # Get the voice file from the request
        voice_file = request.FILES['voice_file']

        # Save the voice file to a temporary location
        with open('voice_temp.wav', 'wb+') as destination:
            for chunk in voice_file.chunks():
                destination.write(chunk)

        # Perform speech recognition to convert voice to text
        r = sr.Recognizer()
        with sr.AudioFile('voice_temp.wav') as source:
            audio_data = r.record(source)
            speech_text = r.recognize_google(audio_data)

        # Define the API endpoint and headers
        api_url = 'https://api.openai.com/v1/engines/davinci/completions'
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        data = {
            'prompt': 'Test API connection',
            'max_tokens': 10
        }

        # Make an API call
        response = requests.post(api_url, headers=headers, json=data)

        # Call the ChatGPT API to get the response text
        response_text = call_chat_gpt_api(speech_text)

        # Convert the response text to voice using gTTS
        tts = gTTS(text=response_text, lang='en')
        response_voice = BytesIO()
        tts.save(response_voice)
        response_voice.seek(0)

        # Read the generated response voice data from the BytesIO object
        response_data = response_voice.read()

        # Delete temporary files
        os.remove('voice_temp.wav')

        # Return the response voice as an audio file in the HTTP response
        response = HttpResponse(response_data, content_type='audio/mpeg')
        response['Content-Disposition'] = 'attachment; filename=response.mp3'
        return response

    return JsonResponse({'error': 'Invalid request'})

def call_chat_gpt_api(text):

    # Call the ChatGPT API to get the response text
    api_url = 'https://api.openai.com/v1/engines/davinci/completions'
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    data = {
        'prompt': f'Generate a response to: "{text}"',
        'max_tokens': 100
    }
    response = requests.post(api_url, headers=headers, json=data)
    print(response.json())

    return response.json()['choices'][0]['text']
