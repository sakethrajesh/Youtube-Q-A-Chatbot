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
CHROMADB_URL = os.environ.get('CHROMADB_URL')
print(f'Using CHROMADB_URL: {CHROMADB_URL}', flush=True)
chroma_client = HttpClient(host='chromadb', port=8000)

# system prompt
prompt = '''
 You are an assistant who is helping a viewer understand a youtube video. The viewer has asked a question about the video.
'''

# example of how to query from chromadb
# collection.query(
#     query_texts=query_texts,
#     n_results=n_results,
#     where=where,
#     where_document=where_document
# )

def format_docs(docs):
    print(docs, flush=True)
    return docs['documents']

def ollama_llm(convo, context, stream=False, model='llama2:chat'):
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
    

def process_data(data):
    documents = []
    metadatas = []
    ids = []

    passage = ""


    for segment in data:
        passage += segment['text']

    i = 0
    for segment in data:
        documents.append(segment['text'])
        metadatas.append({'duration': segment['duration'], 'start': segment['start']})
        ids.append(str(i))

        i += 1

    return passage, ['0']
    # return documents, metadatas, ids
    

@app.route('/api/load_transcript/<video_id>', methods=['GET'])
def get_transcript(video_id):

    try:
        
        resp = requests.get('http://chromadb:8000/api/v1/collections?tenant=default_tenant&database=default_database')

        for collection in resp.json():
            if collection["name"] == video_id:
                return jsonify({"status": "video already loaded"}), 200


        collection = chroma_client.get_or_create_collection(name=video_id)
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        # documents, metadatas, ids = process_data(transcript)
        passage, ids = process_data(transcript)

        print('passage', passage)
        # print('metadata', metadatas)

        collection.add(
            documents=passage,
            # metadatas=metadatas,
            ids=ids
        )

        return jsonify({"status": "video newly loaded"}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@app.route('/api/question', methods=['POST'])
def question():
    data = request.json
    question = data['question']
    video_id = data['video_id']
    
    collection = chroma_client.get_or_create_collection(name=video_id)


    sources = collection.query(
        query_texts=question,
        n_results=10,
        # where=where,
        # where_document=where_document
    )

    return jsonify(sources)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)