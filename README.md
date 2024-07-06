# GPT for Youtube Video

## Design
I chose to use a RAG (Retrieval-Augmented Generation) model to solve this problem because it combines the benefits of both retrieval-based and generation-based models. 

Retrieval-based models excel at finding relevant information from a large corpus of documents, which is crucial for answering questions accurately. On the other hand, generation-based models have the ability to generate human-like responses, allowing for more flexibility and creativity in the answers.

By using a RAG model, I can leverage the retrieval capabilities to find the most relevant information from the video transcripts stored in ChromaDB. This ensures that the answers provided are accurate and based on the actual content of the videos.

Additionally, the generation component of the RAG model allows for more natural and context-aware responses. It can take into account the entire chat history and generate responses that are tailored to the specific conversation, providing a more interactive and engaging experience for the users.

Overall, the RAG model provides a powerful solution for the Youtube-Q-A-Chatbot project, combining the strengths of retrieval and generation models to deliver accurate and context-aware answers to user's questions.


## Backend

The backend of the Youtube-Q-A-Chatbot project is responsible for handling the API requests that interact with the RAG model pipeline to generate responses using open source self-hosted LLMs.

### Technologies
#### Ollama
> Ollama is a platform that manages setting up and running open source and custom LLMs. In this project, Ollama is hosted in the VT Discovery Kubernetes Cluster and is running Meta's Llama3 and Llama2, and Mistral. LLama3 is used to create the embedding for the youtube transcripts, which are stored in ChromaDB, and is used to generate responses to the user's prompted questions. 

#### ChromaDB
> ChromaDB is the vector database that is used in this project. ChromaDB creates a collection for each youtube video. Each collection, stores the youtube video's transcripts in chunk, each chunk's embedding, and metadata regarding which part of the video each chunk corresponds to. When a question is asked, the vector db is queried for the chuck with the highest similarity. That chuck is used as context to answer the user's questions. 

#### Docker
> Docker is used in the project to containerize the core components of the project and docker-compose is used to easily bring up the required containers and define the networking rules to allow the containers to interact. 

#### Flask and Python
> Flask and Python are used to handle API requests and process the chat history. Flask is a lightweight web framework in Python that allows for easy routing and handling of HTTP requests. Python, being a versatile programming language, provides the necessary tools and libraries to process the chat history and generate responses using open source self-hosted LLMs. Together, Flask and Python form the foundation of the backend architecture, enabling seamless communication between the frontend and the LLM models.

### API Docs

#### `POST /api/chat`

This endpoint takes in the chat history of the current session and returns the LLMs response to the question.

| Parameter  | Type     | Description                                      |
| :--------- | :------- | :----------------------------------------------- |
| `messages` | `array`  | **Required**. Array of user's messages           |
| `model`    | `string` | Optional. Model for chat (default: llama2:chat)  |

##### Example body

```json
{
    "messages": [
        {
            "role": "user",
            "content": "User's message"
        }
    ],
    "model": "mistral" // Optional, default is "llama3"
}
```

#### Success Response

**Code:** `200 OK`

**Content:**

```json
{
    "text": "Assistant's response",
    "source_tags": ["source_tag_1", "source_tag_2"],
    "source_documents": ["source_document_1", "source_document_2"]
}
```

#### Error Response

**Code:** `500 Internal Server Error`

**Content:**

```json
{
    "error": "Error message"
}
```

#### `GET /api/load_transcript/<video_id>`

This endpoint loads a given youtube video's transcript in ChromaDB (vectorDB).

| Parameter  | Type     | Description                       |
| :--------- | :------- | :-------------------------------- |
| `video_id` | `string` | **Required**. Id of youtube video |

#### Success Response

**Code:** `200 OK`

**Content:**

```json
{
    "status":"video newly loaded" // or "video already added"
}
```

#### Error Response

**Code:** `500 Internal Server Error`

**Content:**

```json
{
    "error": "Error message"
}
```


### API Docs

```http
  POST /api/chat
```

This endpoint takes in the chat history of the current session and returns the LLMs response to the question.
| Parameter | Type | Description |
| :--------- | :------- | :---------------------------------------------- |
| `messages` | `array` | **Required**. Array of user's messages |
| `model` | `string` | Optional. Model for chat (default: llama2:chat) |

##### Example body

```json
{
  "messages": [
    {
      "role": "user",
      "content": "User's message"
    }
  ],
  "model": "mistral" // Optional, default is "llama3"
}
```

#### Success Response

**Code:** `200 OK`
**Content:**

```json
{
  "text": "Assistant's response",
  "source_tags": ["source_tag_1", "source_tag_2"],
  "source_documents": ["source_document_1", "source_document_2"]
}
```

#### Error Response

**Code:** `500 Internal Server Error`
**Content:**

```json
{
  "error": "Error message"
}
```

---

```http
  GET /api/load_transcript/<video_id>
```

This endpoint loads a given youtube video's transcript in ChromaDB (vectorDB)

| Parameter  | Type     | Description                       |
| :--------- | :------- | :-------------------------------- |
| `video_id` | `string` | **Required**. Id of youtube video |

#### Success Response

**Code:** `200 OK`
**Content:**

```json
{
  "status":"video newly loaded" // or "video already added"
}
```

#### Error Response

**Code:** `500 Internal Server Error`
**Content:**

```json
{
  "error": "Error message"
}
```

## Frontend
