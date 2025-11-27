# NyX AI - DeepInfra API Gateway

A lightweight FastAPI-based gateway for DeepInfra models.

## Features

- 🚀 Simple in-memory API key management
- 🤖 Multiple DeepInfra models supported
- 🔒 API key authentication with rate limiting (1000 requests/day)
- 📊 OpenAI-compatible API endpoints

## Available Models

- llama-2-7b, llama-2-13b, llama-2-70b
- llama-3-8b, llama-3-70b
- codellama-34b
- mistral-7b
- mixtral-8x7b, mixtral-8x22b
- gemma-7b
- wizardlm-2-7b, wizardlm-2-8x22b
- dolphin-mixtral-8x7b
- airoboros-70b
- dbrx-instruct
- zephyr-141b

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Start the server

```bash
python main.py
```

The API will be available at `http://localhost:8000`

### Endpoints

- `GET /` - Welcome message
- `GET /v1/models` - List available models
- `POST /v1/chat/completions` - Chat completions (OpenAI-compatible)

### API Key Management

Set the `MASTER_KEY` environment variable to enable a master API key:

```bash
set MASTER_KEY=your-master-key
```

## Example Request

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama-3-8b",
    "messages": [{"role": "user", "content": "Hello!"}],
    "temperature": 0.7,
    "stream": false
  }'
```

## Configuration

- Default port: 8000
- Rate limit: 1000 requests per day per API key
- Master key: Set via `MASTER_KEY` environment variable
