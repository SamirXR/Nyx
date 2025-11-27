import os
import json
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import StreamingResponse
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from typing import List, Dict
import httpx
from datetime import datetime, timedelta
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
api_key_header = APIKeyHeader(name="Authorization", scheme_name="Bearer")

# In-memory storage for API keys (replaces MongoDB)
api_keys_store: Dict[str, Dict] = {}


# DeepInfra models only
MODEL_NAMES = {
    "deepseek-v3": "deepseek-ai/DeepSeek-V3-0324-Turbo",
    "llama-4-maverick": "meta-llama/Llama-4-Maverick-17B-128E-Instruct-Turbo",
}


def verify_nyx_api_key(thothaiapikey):
    target_thothkey = thothaiapikey.replace("Bearer ", "")
    
    # Check master key
    master_key = os.environ.get('MASTER_KEY', 'nx-master-key-default')
    if master_key in target_thothkey:
        return True
    
    # Check stored API keys
    found_item = find_api_key(target_thothkey)
    
    if found_item:
        reset_time = datetime.fromisoformat(found_item["reset_time"])
        if found_item["requests"] >= 1000 and datetime.now() - reset_time < timedelta(days=1):
            return False
        else:
            if datetime.now() - reset_time >= timedelta(days=1):
                found_item["requests"] = 0
                found_item["reset_time"] = datetime.now().isoformat()
                api_keys_store[target_thothkey] = found_item
            return True
    else:
        return False

def find_api_key(target_thothkey):
    return api_keys_store.get(target_thothkey)

def generate_nyx_api_key(key):
    newkeydata = {
        "nyxkey": key,
        "requests": 0,
        "reset_time": str(datetime.now().isoformat())
    }
    api_keys_store[key] = newkeydata

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
    if hasattr(body, 'max_tokens'):
        delattr(body, 'max_tokens')
    
    if body.stream:
        async with httpx.AsyncClient() as client:
            async with client.stream("POST", url, headers={'Content-Type': 'application/json'}, json=body.model_dump(), timeout=360) as resp:
                async for chunk in resp.aiter_bytes():
                    yield chunk
    else:
        response = await httpx.AsyncClient().post(url, headers={'Content-Type': 'application/json'}, json=body.model_dump(), timeout=360)
        yield response.content

@app.get("/v1/models")
async def get_models():
    return {"models": list(MODEL_NAMES.keys())}

@app.get("/")
def read_root():
    return {"message": "Welcome to NyX AI - DeepInfra API Gateway"}

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
        found_item["requests"] += 1
        api_keys_store[target_thothkey] = found_item
    
    model_name = MODEL_NAMES.get(body.model)
    
    if model_name:
        body.model = model_name
        if body.stream:
            response = StreamingResponse(process_completions(body), media_type="text/event-stream")
            response.headers["X-Accel-Buffering"] = "no"
            return response
        else:
            async for chunk in process_completions(body):
                return json.loads(chunk)
    else:
        raise HTTPException(status_code=400, detail="Invalid model name. Use /v1/models to see available models.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
