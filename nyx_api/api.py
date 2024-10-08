import os
import json
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import StreamingResponse
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from typing import List
import httpx
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime, timedelta
from fastapi.middleware.cors import CORSMiddleware
import uuid
import asyncio
import datetime
import time
from datetime import datetime
from pymongo import MongoClient

dt = datetime.strptime('2019-12-04T10:20:30.400', '%Y-%m-%dT%H:%M:%S.%f')

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
api_key_header = APIKeyHeader(name="Authorization", scheme_name="Bearer")

uri = "mongodb+srv://snipershot281:bIwDZRrqQryzquUh@nyx.hnjano2.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(uri, server_api=ServerApi('1'))

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

db = client['nyx']
api_keys = db['api_keys']


MODEL_NAMES = {
    "llama-2-7b": "meta-llama/Llama-2-70b-chat-hf",
    "llama-2-13b": "meta-llama/Llama-2-13b-chat-hf",
    "llama-2-70b-chat": "meta-llama/Llama-2-7b-chat-hf",
    "codellama34-b": "codellama/CodeLlama-34b-Instruct-hf",
    "airoboros-70b": "jondurbin/airoboros-l2-70b-gpt4-1.4.1",
    "mistral-7b": "mistralai/Mistral-7B-Instruct-v0.1",
    "mixtral-8x7B" :"mistralai/Mixtral-8x7B-Instruct-v0.1",
    "lzlv-70b":"lizpreciatior/lzlv_70b_fp16_hf",
    "dolphin-mixtral-8x7b":"cognitivecomputations/dolphin-2.6-mixtral-8x7b",
    "meta-llama/Meta-Llama-3-70B-Instruct" : "meta-llama/Meta-Llama-3-70B-Instruct",
    "meta-llama/Meta-Llama-3-8B-Instruct" : "meta-llama/Meta-Llama-3-8B-Instruct",
    "mistralai/Mixtral-8x22B-Instruct-v0.1" :"mistralai/Mixtral-8x22B-Instruct-v0.1",
    "microsoft/WizardLM-2-8x22B" : "microsoft/WizardLM-2-8x22B",
    "microsoft/WizardLM-2-7" : "microsoft/WizardLM-2-7",
    "databricks/dbrx-instruct" : "databricks/dbrx-instruct",
    "HuggingFaceH4/zephyr-orpo-141b-A35b-v0.1" : "HuggingFaceH4/zephyr-orpo-141b-A35b-v0.1",
    "google/gemma-1.1-7b-it" : "google/gemma-1.1-7b-it",
}

MANTON_MODEL_NAMES = {
    "claude-instant-1.2":"claude-instant-1.2",
    "google-gemini-pro" : "google-gemini-pro",
    "claude-2.0" :"claude-2.0",
    "claude-2.1" : "claude-2.1"

}

GITHUB_MODEL_NAMES = {
    "text-search-babbage-doc-001": "text-search-babbage-doc-001",
    "gpt-4-0613": "gpt-4-0613",
    "gpt-4": "gpt-4",
    "babbage": "babbage",
    "gpt-3.5-turbo-0613": "gpt-3.5-turbo-0613",
    "text-babbage-001": "text-babbage-001",
    "gpt-3.5-turbo": "gpt-3.5-turbo",
    "gpt-3.5-turbo-1106": "gpt-3.5-turbo-1106",
    "curie-instruct-beta": "curie-instruct-beta",
    "gpt-3.5-turbo-0301": "gpt-3.5-turbo-0301",
    "gpt-3.5-turbo-16k-0613": "gpt-3.5-turbo-16k-0613",
    "text-embedding-ada-002": "text-embedding-ada-002",
    "davinci-similarity": "davinci-similarity",
    "curie-similarity": "curie-similarity",
    "babbage-search-document": "babbage-search-document",
    "curie-search-document": "curie-search-document",
    "babbage-code-search-code": "babbage-code-search-code",
    "ada-code-search-text": "ada-code-search-text",
    "text-search-curie-query-001": "text-search-curie-query-001",
    "text-davinci-002": "text-davinci-002",
    "ada": "ada",
    "text-ada-001": "text-ada-001",
    "ada-similarity": "ada-similarity",
    "code-search-ada-code-001": "code-search-ada-code-001",
    "text-similarity-ada-001": "text-similarity-ada-001",
    "text-davinci-edit-001": "text-davinci-edit-001",
    "code-davinci-edit-001": "code-davinci-edit-001",
    "text-search-curie-doc-001": "text-search-curie-doc-001",
    "text-curie-001": "text-curie-001",
    "curie": "curie",
    "davinci": "davinci",
    "gpt-4-0314": "gpt-4-0314"
}




def verify_nyx_api_key(thothaiapikey):
    target_thothkey = thothaiapikey.replace("Bearer ", "")
    if os.environ['MASTER_KEY'] in target_thothkey:
        return True
    found_item = find_api_key(target_thothkey)

    if found_item:
        reset_time = datetime.fromisoformat(found_item["reset_time"])
        if found_item["requests"] >= 1000 and datetime.now() - reset_time < timedelta(days=1):
            return False
        else:
            if datetime.now() - reset_time >= timedelta(days=1):
                found_item["requests"] = 0
                found_item["reset_time"] = datetime.now().isoformat()
                db['api_keys'].update_one({'_id': found_item['_id']}, {"$set": found_item}, upsert=False)
            return True
    else:
        return False

def find_api_key(target_thothkey):
    return db['api_keys'].find_one({"nyxkey": target_thothkey})

def generate_nyx_api_key(key, discord_id):
    newkeydata = {
        "nyxkey": key,
        "requests": 0,
        "reset_time": str(datetime.now().isoformat())
    }
    db['api_keys'].insert_one(newkeydata)

class Message(BaseModel):
    role: str
    content: str

class RequestBody(BaseModel):
    model: str
    messages: List[Message]
    max_tokens: int = 8000
    temperature: float = 0.7
    stream: bool = False

async def process_completions(body: RequestBody):
  url = 'https://api.deepinfra.com/v1/openai/chat/completions'
  del body.max_tokens
  if body.stream:
    async with httpx.AsyncClient() as client:
        async with client.stream("POST", url, headers={'Content-Type': 'application/json'}, json=body.model_dump(), timeout=360) as resp:
            async for chunk in resp.aiter_bytes():
                yield chunk
  else:
    response = await httpx.AsyncClient().post(url, headers={'Content-Type': 'application/json'}, json=body.model_dump(), timeout=360)
    yield response.content

async def process_manton_completions(body: RequestBody):
  url = 'https://free.chatgpt.org.uk/api/openai/v1/chat/completions'
  headers = {
      'Accept': '*/*',
      'Content-Type': 'application/json',
      'origin': 'https://gpt.manton.fun',
      'referer': 'https://gpt.manton.fun/',
      'x-requested-with': 'XMLHttpRequest',
  }
  if body.stream:
    async with httpx.AsyncClient() as client:
        async with client.stream("POST", url, headers=headers, json=body.model_dump(), timeout=360) as resp:
            async for chunk in resp.aiter_bytes():
                if chunk:
                  yield chunk
  else:
    response = await httpx.AsyncClient().post(url, headers=headers, json=body.model_dump(), timeout=360)
    yield response.content



async def process_github_completions(body: RequestBody):
  url = 'https://copilot-b67.onrender.com/v1/chat/completions'
  headers = {
      'Accept': '*/*',
      'Content-Type': 'application/json',
      'origin': 'https://gpt.manton.fun',
      'referer': 'https://gpt.manton.fun/',
      'x-requested-with': 'XMLHttpRequest',
  }
  if body.stream:
    async with httpx.AsyncClient() as client:
        async with client.stream("POST", url, headers=headers, json=body.model_dump(), timeout=360) as resp:
            async for chunk in resp.aiter_bytes():
                if chunk:
                  yield chunk
  else:
    response = await httpx.AsyncClient().post(url, headers=headers, json=body.model_dump(), timeout=360)
    yield response.content

@app.get("/v1/models")
async def get_models():
    all_models = list(MODEL_NAMES.keys()) + list(MANTON_MODEL_NAMES.keys()) + list(GITHUB_MODEL_NAMES.keys())
    return {"models": all_models}


@app.get("/")
def read_root():
    return {"Heyyy!": "Welcome to NyX AI! Join our Discord server: https://discord.com/invite/9bqRWAP74f"}

@app.post("/openai/chat/completions/v1/chat/completions")
@app.post("/openai/chat/completions/chat/completions") 
@app.post("/openai/chat/completions")
@app.post("/v1/chat/completions")
async def get_completions(body: RequestBody, key: str = Depends(api_key_header)):
  if not verify_nyx_api_key(key):
      raise HTTPException(status_code=401, detail="Invalid API key or daily limit reached")
  target_thothkey = key.replace("Bearer ", "")
  found_item = find_api_key(target_thothkey)

  if found_item:
      found_item["requests"] += 5
      db['api_keys'].update_one({'_id': found_item['_id']}, {"$set": found_item}, upsert=False)

  model_name = MODEL_NAMES.get(body.model)
  manton_model_name = MANTON_MODEL_NAMES.get(body.model)
  github_model_name = GITHUB_MODEL_NAMES.get(body.model)

  if model_name:
      body.model = model_name
      if body.stream:
          response = StreamingResponse(process_completions(body), media_type="text/event-stream")
          response.headers["X-Accel-Buffering"] = "no"
          return response
      else:
          async for chunk in process_completions(body):
              return json.loads(chunk)
  elif manton_model_name:
      body.model = manton_model_name
      if body.stream:
        response = StreamingResponse(process_manton_completions(body), media_type="text/event-stream")
        response.headers["X-Accel-Buffering"] = "no"
        return response
      else:
          async for chunk in process_manton_completions(body):
              return json.loads(chunk)
  elif github_model_name:
      body.model = github_model_name
      if body.stream:
        response = StreamingResponse(process_github_completions(body), media_type="text/event-stream")
        response.headers["X-Accel-Buffering"] = "no"
        return response
      else:
          async for chunk in process_github_completions(body):
              return json.loads(chunk)
  else:
      raise HTTPException(status_code=400, detail="Invalid model name")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
