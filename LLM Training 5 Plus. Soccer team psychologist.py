#!/usr/bin/env python
# coding: utf-8

# In[14]:


# imports

import os
import json
from dotenv import load_dotenv
from openai import OpenAI
import gradio as gr


# In[15]:


# Initialization

load_dotenv(override=True)

openai_api_key = os.getenv('OPENAI_API_KEY')
if openai_api_key:
    print(f"OpenAI API Key exists and begins {openai_api_key[:8]}")
else:
    print("OpenAI API Key not set")
    
MODEL = "gpt-4o-mini"
openai = OpenAI()


# In[16]:


system_message = "You are a psychologist for a soccer team who helps players stay mentally sharp and not let obstacles such as injuries, suspensions, off-field issues, or family problems affect their concentration."
system_message += "Give very kind and nice answers to keep the athelete's motivation; but not very long answers and instead of long answers, try to ask questions about more details and then response based on that response and reach a conclusion after an acceptable amount of questions. "
system_message += "After making the athelete's calm, try to give them useful instructions to do for being able to deal with their problem."


# In[17]:


#Audio
from pydub import AudioSegment
from pydub.playback import play
from io import BytesIO


def talker(message):
    response = openai.audio.speech.create(
      model="tts-1",
      voice="nova",   #type of the voice 
      input=message
    )
    
    audio_stream = BytesIO(response.content)
    audio = AudioSegment.from_file(audio_stream, format="mp3")
    play(audio)


# In[20]:


def chat(message, history):
    messages = [{"role": "system", "content": system_message}] + history + [{"role": "user", "content": message}]
    response = openai.chat.completions.create(model=MODEL, messages=messages)
    reply = response.choices[0].message.content
    talker(reply)
    return reply

# Function to generate markdown instructions
def generate_instructions(history):
    conversation_text = "\n".join([
        f"Player: {h['content']}" if h["role"] == "user" else f"Psychologist: {h['content']}"
        for h in history if h["role"] in ["user", "assistant"]
    ])
    
    prompt = f"""
    Based on the following conversation between a soccer player and their psychologist,
    write clear, motivational, and practical instructions for the player.
    Format the response in Markdown with headers, bullet points, and short sentences.

    Conversation:
    {conversation_text}
    """

    response = openai.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a sports psychologist writing practical instructions."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

# Wrap ChatInterface + extra button inside Blocks
with gr.Blocks() as demo:
    chatbot = gr.ChatInterface(fn=chat, type="messages")
    instructions_btn = gr.Button("Generate Instructions")
    instructions_output = gr.Markdown()

    # Connect button
    instructions_btn.click(fn=generate_instructions, inputs=chatbot.chatbot, outputs=instructions_output)

demo.launch()


# In[ ]:




