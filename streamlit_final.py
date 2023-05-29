
from __future__ import print_function
import streamlit as st
import sounddevice as sd
import numpy as np
import tempfile
import os
from scipy.io import wavfile
import os
import openai
from apiclient import discovery
from httplib2 import Http
from oauth2client import client, tools as oauth2client_tools
import re
import pyaudio
import wave
from pydub import AudioSegment
from deepgram import Deepgram
import json
import os
from googleapiclient.discovery import build

from PIL import Image
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2 import service_account
def record_audio(duration):
    fs = 44100  # Sample rate (in Hz)
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()  # Wait for the recording to complete
    return recording.flatten()

# Streamlit User Interface
st.title("Audio Recording with Streamlit")
duration = st.slider("Recording Duration (in seconds)", 1, 10, 5)
record_button = st.button("Start Recording :microphone:")

if record_button:
    # Capture audio from the microphone
    microphone_duration = duration + 1  # Add 1 second buffer for microphone input
    microphone_recording = record_audio(microphone_duration)

    # Save the recording as a temporary WAV file
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp:
        temp_path = temp.name
        wavfile.write(temp_path, 44100, microphone_recording)

    # Load the temporary WAV file and display it with the st.audio function
    audio_bytes = open(temp_path, "rb").read()
    st.audio(audio_bytes, format="audio/wav")

    # Save the recording to a permanent WAV file
    output_path = "output2.wav"  # Output path to save the WAV file
    wavfile.write(output_path, 44100, microphone_recording)

    if st.success("Audio saved to output.wav"):
        


        dg_key = '5d1fdcf0fd456264b0906048643058a76072a4a2'
        dg = Deepgram(dg_key)
        MIMETYPE = 'wav'
        def transcribe_audio(audio_file):
            options = {
            "punctuate": True,
            "model": 'general',
            "tier": 'enhanced'}

            if audio_file.endswith(MIMETYPE):
                output_file = os.path.join(os.path.dirname(audio_file), f"{os.path.basename(audio_file)[:-4]}.json")
                with open(audio_file, "rb") as f:
                    source = {"buffer": f, "mimetype": 'audio/' + MIMETYPE}

                    res = dg.transcription.sync_prerecorded(source, options)
                    with open(output_file, "w") as transcript:
                        json.dump(res, transcript)
                    return output_file
        

        # Example usage
        audio_file = "output2.wav"  # Replace with the recorded audio file name
        transcription_output = transcribe_audio(audio_file)
        if transcription_output:
            print(transcription_output)
        # Set this variable to the path of the output file you wish to read
        OUTPUT = r"output2.json"


        # The JSON is loaded with information, but if you just want to read the
        # transcript, run the code below!
        def print_transcript(transcription_file):
            with open(transcription_file, "r") as file:
                data = json.load(file)
                result = data['results']['channels'][0]['alternatives'][0]['transcript']
                result = result.split('.')
        #for sentence in result:
        # #  print(sentence + '.')
                return result[0]

        text=print_transcript(OUTPUT)
        print(text)
        openai.api_key = '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'

        def resumer(text):
            return openai.Completion.create(
            model="text-davinci-003",
            prompt=text,
            temperature=0.5,
            max_tokens=4000
            ).choices[0].text.strip()
        with open('phrase.txt', 'r') as file:
            requests = file.read()
        input=requests+text
        response=resumer(input)
        print(response)

        SCOPES = "https://www.googleapis.com/auth/forms.body"
        DISCOVERY_DOC = "https://forms.googleapis.com/$discovery/rest?version=v1"
        # Create a storage object to store user access credentials
        
        with open('token.json', 'r') as file_obj:
            store = client.Storage('token.json')
        # Initialize credentials variable
        
        creds = None
        # If credentials are invalid or non-existent, perform authorization steps to obtain valid credentials
        if not creds or not creds.valid or creds.expired:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = service_account.Credentials.from_service_account_file('credentials.json',
    scopes=['https://www.googleapis.com/auth/forms', 'https://www.googleapis.com/auth/drive'])
                

            #creds = tools.run_flow(flow, store)
        # Build a client for the Google Forms API using the obtained credentials
        #form_service = discovery.build('forms', 'v1', credentials=creds, discoveryServiceUrl=DISCOVERY_DOC, static_discovery=False)
        NEW_FORM = {
            "info": {
                "title": "chatgpt form",
            }
        }
        service = build('forms', 'v1', credentials=flow)
        form = service.forms().create(body=NEW_FORM).execute()
        # Define the information for the new form
    
        # Initialize empty lists to store categorized questions
        Single_Choice=[]
        Text_Box=[]
        Multiple_Choice=[]
        Single_Choice_question=[]
        Text_Box_question=[]
        Multiple_Choice_question=[]
        # Split the response string into lines using the newline character ('\n') and store the lines in the 'a' list
        a=response.split('\n')
        print(a)
        # Iterate over each line in 'a'
        for i in a:
            # Check if the line contains the substring "(Single Choice)"
            if "(Single Choice)" in i:
                # Append the line to the 'Single_Choice' list
                Single_Choice.append(i)
            # Check if the line contains the substring "(Text Box)"
            if "(Text Box)" in i:
                # Append the line to the 'Text_Box' list
                Text_Box.append(i)
            # Check if the line contains the substring "(Multiple Choice)"
            if "(Multiple Choice)" in i:
                # Append the line to the 'Multiple_Choice' list
                Multiple_Choice.append(i)
    # Iterate over each question in the 'Single_Choice' list
        for e in Single_Choice:
            # Extract the question text by splitting at the question mark character ('?')
            extracted_text = e.split('?')[0]
            # Extract the options from the question string
            options_liste =  e.strip().split(')')[1].split(',')
            # Create a list of dictionaries for each option
            options = [{"value": item} for item in options_liste]
            # Create a dictionary representing the question and its options
            q={
            "requests": [{
                "createItem": {
                    "item": {
                        "title": extracted_text,
                        "questionItem": {
                            "question": {
                                "required": True,
                                "choiceQuestion": {
                                    "type": "RADIO",
                                    "options": options,
                                    "shuffle": True
                                }
                            }
                        },
                    },
                    "location": {
                        "index": 0
                    }
                }
            }]
        }
            # Append the question dictionary to the 'Single_Choice_question' list
            Single_Choice_question.append(q)
            
        # Iterate over each question in the 'Text_Box' list
        for e in Text_Box:
            # Extract the question text by splitting at the question mark character ('?')
            extracted_text = e.split('?')[0]
            # Create a dictionary representing the text box question
            q={
            "requests": [{
                "createItem": {
                    "item": {
                        "title":extracted_text ,
                        "questionItem": {
                            "question": {
                                "required": True,
                                "textQuestion": {}
                            }
                        }
                    },
                    "location": {
                        "index": 0
                    }
                }
            }]
        }
            # Append the question dictionary to the 'Text_Box_question' list
            Text_Box_question.append(q)

        # Iterate over each question in the 'Multiple_Choice' list
        for e in Multiple_Choice:
            # Extract the question text by splitting at the question mark character ('?')
            extracted_text = e.split('?')[0]
            # Extract the options from the question string
            options_liste =  e.strip().split(')')[1].split(',')
            # Create a list of dictionaries for each option
            options = [{"value": item} for item in options_liste]
            # Create a dictionary representing the question and its options
            q={
            "requests": [{
                "createItem": {
                    "item": {
                        "title": extracted_text,
                        "questionItem": {
                            "question": {
                                "required": True,
                                "choiceQuestion": {
                                    "type": "CHECKBOX",
                                    "options": options,
                                    "shuffle": True
                                }
                            }
                        },
                    },
                    "location": {
                        "index": 0
                    }
                }
            }]
        }
            # Append the question dictionary to the 'Multiple_Choice_question' list
            Multiple_Choice_question.append(q)

        # Grouping the questions using a list format
        Questions=Single_Choice_question+Text_Box_question+Multiple_Choice_question    
        # Request body for adding a multiple-choice question
        # Creates the initial form
        result = service.forms().create(body=NEW_FORM).execute()
        # Adds the question to the form
        for question in Questions:
            question_setting = service.forms().batchUpdate(formId=result["formId"], body=question).execute()
        # Prints the result to show the question has been added
        get_result = service.forms().get(formId=result["formId"]).execute()
        print(get_result)
        print(get_result["responderUri"])
        st.write(get_result["responderUri"])
