# Use a base image
FROM python:3.11

# Set the working directory
WORKDIR /app

# Install any dependencies
RUN pip install langchain
RUN pip install ollama
RUN pip install langchain_community
RUN pip install chromadb
RUN pip install pypdf
RUN pip install flask
RUN pip install openai
RUN pip install youtube-transcript-api

COPY app.py .

ENTRYPOINT ["python3", "app.py"]