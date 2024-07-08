from ollama import Client
from openai import OpenAI
import os
import json
import logging
from flask import Flask, Response, request, jsonify, stream_with_context
from chromadb import HttpClient
from youtube_transcript_api import YouTubeTranscriptApi
import time
import requests
from pytube import YouTube
import re

app = Flask(__name__)

# openai setup
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
OpenAI_client = OpenAI(
    api_key=OPENAI_API_KEY,
)

time.sleep(5)

# ollama setup
OLLAMA_URL = os.environ.get('OLLAMA_URL')
print(f'Using OLLAMA_URL: {OLLAMA_URL}', flush=True)
Ollama_client = Client(host=OLLAMA_URL)

# chromadb setup
CHROMADB_HOST = os.environ.get('CHROMADB_HOST')
CHROMADB_PORT = os.environ.get('CHROMADB_PORT')
print(f'Using CHROMADB_HOST: {CHROMADB_HOST}', flush=True)
print(f'Using CHROMADB_PORT: {CHROMADB_PORT}', flush=True)
chroma_client = HttpClient(host=CHROMADB_HOST, port=CHROMADB_PORT)

# system prompt
prompt = '''
 You are an assistant who is helping a viewer understand a youtube video. The viewer has asked a question about the video.
'''

def format_docs(docs):
    """
    Formats the retrieved documents from ChromaDB.

    Args:
        docs (dict): The retrieved documents from ChromaDB.

    Returns:
        list: The formatted documents.
    """
    print(docs, flush=True)
    return docs['documents']

def ollama_llm(convo, context, stream=False, model='llama2:chat'):
    """
    Performs language model completion using Ollama or OpenAI.

    Args:
        convo (list): The conversation messages.
        context (str): The context for the conversation.
        stream (bool, optional): Whether to stream the completion or not. Defaults to False.
        model (str, optional): The language model to use. Defaults to 'llama2:chat'.

    Returns:
        dict: The completion response.
    """
    question = convo[-1]['content']
    formatted_prompt = f"Question: {question}\n\nContext: {context}"
    convo[-1]['content'] = formatted_prompt

    print(convo, flush=True)

    if model == 'gpt-4':
        return OpenAI_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=convo,
            stream=stream
        )
    
    else:
        return Ollama_client.chat(model=model, messages=convo, stream=stream)  


@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Handles the chat API endpoint.

    Returns:
        Response: The API response.
    """
    data = request.json
    messages = data['messages']
    messages.insert(0, {"role": "assistant", "content": prompt})
    model = 'llama3'
    video_id  = data['video_id']

    print("messages", messages, flush=True)

    try:        
        question = messages[-1]['content']

        collection = chroma_client.get_or_create_collection(name=video_id)

        # get the top 3 documents from the collection that are most relevant to the question
        retrieved_docs = collection.query(
            query_texts=question,
            n_results=3,
        )

        app.logger.info(retrieved_docs)

        formatted_context = format_docs(retrieved_docs)

        text_content = ollama_llm(messages, formatted_context, model=model)

        return jsonify({"text": text_content['message']['content'], "source_tags" : retrieved_docs['metadatas'], "source_documents" : retrieved_docs['documents']}), 200
    
    except Exception as e:
        print(str(e), flush=True)
        return jsonify({"error": str(e)}), 500
    
def get_chapters(url):
    """
    Retrieves the chapters from a YouTube video.

    Args:
        url (str): The URL of the YouTube video.

    Returns:
        list: The chapters of the video.
    """
    youtube = YouTube(url)
    stream = youtube.streams.first()
    desc = youtube.description

    chapters = []

    lines = desc.split('\n')
    for line in lines:
        pattern = r'(\d{2}:\d{2}(?::\d{2})?)\s*(.*)'
        timestamps = re.findall(pattern, line)
        for timestamp in timestamps:
            time, title = timestamp
            if title == '':
                title = 'No Title'
            # Split the timestamp and convert to seconds
            parts = time.split(':')
            if len(parts) == 2:  # MM:SS format
                parts = ['00'] + parts  
            seconds = int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
            chapters.append((seconds, title))

    return chapters

def process_data(data, chapters):
    """
    Processes the transcript data and extracts passages for each chapter.

    Args:
        data (list): The transcript data.
        chapters (list): The chapters of the video.

    Returns:
        tuple: The processed documents, metadatas, and ids.
    """
    documents = []
    metadatas = []
    ids = []

    full_transcript = ""

    chapter_index = 1

    for i in range(1, len(chapters)):
        chapter_end = chapters[i][0]
        passage = ""

        while data[0]['start'] < chapter_end:
            segment = data.pop(0)
            passage += segment['text']
            full_transcript += segment['text']
        
        documents.append(passage)
        metadatas.append({'chapter_name':chapters[i][1], 'duration': chapter_end - chapters[i-1][0], 'start': chapters[i-1][0]})
        ids.append(str(chapter_index))
        chapter_index += 1
    
    documents.append(full_transcript)
    ids.append(str(++chapter_index))

    print('documents', documents)
    print('metadatas', metadatas)

    return documents, metadatas, ids
    

@app.route('/api/load_transcript/<video_id>', methods=['GET'])
def get_transcript(video_id):
    """
    Retrieves and processes the transcript of a YouTube video.

    Args:
        video_id (str): The ID of the YouTube video.

    Returns:
        Response: The API response.
    """
    try:
        
        resp = requests.get('http://chromadb:8000/api/v1/collections?tenant=default_tenant&database=default_database')

        for collection in resp.json():
            if collection["name"] == video_id:
                return jsonify({"status": "video already loaded"}), 200


        collection = chroma_client.get_or_create_collection(name=video_id)
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        chapters = get_chapters(f"https://www.youtube.com/watch?v={video_id}")

        documents, metadatas, ids = process_data(transcript, chapters)

        collection.add(
            documents=documents,
            ids=ids
        )

        return jsonify({"status": "video newly loaded"}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@app.route('/api/question', methods=['POST'])
def question():
    """
    Handles the question API endpoint.

    Returns:
        Response: The API response.
    """
    data = request.json
    question = data['question']
    video_id = data['video_id']
    
    collection = chroma_client.get_or_create_collection(name=video_id)


    sources = collection.query(
        query_texts=question,
        n_results=10,
    )

    return jsonify(sources)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)