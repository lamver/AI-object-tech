import os
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Any, List
from huggingface_hub import hf_hub_download
from llama_cpp import Llama
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Разрешаем всё (CORS), чтобы не было ошибок 405/403
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

REPO_ID = os.getenv("MODEL_REPO")
MODEL_FILE = os.getenv("MODEL_FILE")
HF_TOKEN = os.getenv("HF_TOKEN")
llm = None

@app.on_event("startup")
async def startup_event():
    global llm
    model_path = os.path.join("./models", MODEL_FILE)
    if not os.path.exists(model_path):
        hf_hub_download(
            repo_id=REPO_ID, 
            filename=MODEL_FILE, 
            local_dir="./models", 
            local_dir_use_symlinks=False,
            token=HF_TOKEN
            )
    
    llm = Llama(
        model_path=model_path,
        n_ctx=int(os.getenv("N_CTX", 4096)),
        n_threads=int(os.getenv("N_THREADS", 4)),
        chat_format=os.getenv("CHAT_FORMAT", "gemma"),
        verbose=False # Чтобы не спамить в логи
    )
    print("🚀 API READY")

# Оставляем одну версию модели запроса
class ChatRequest(BaseModel):
    model: Optional[str] = None 
    messages: List[dict]
    response_format: Optional[dict] = None
    temperature: float = 0.1

@app.post("/v1/chat/completions")
async def chat(request: ChatRequest):
    try:
        # Извлекаем схему из формата OpenAI
        # Мы ищем её в response_format -> json_schema -> schema
        schema = None
        if request.response_format:
            if "json_schema" in request.response_format:
                schema = request.response_format["json_schema"].get("schema")
            elif "schema" in request.response_format:
                schema = request.response_format.get("schema")

        # Формируем аргументы для llama-cpp
        completion_args = {
            "messages": request.messages,
            "temperature": request.temperature,
        }

        # Если схема передана, активируем грамматику JSON
        if schema:
            completion_args["response_format"] = {
                "type": "json_object",
                "schema": schema
            }

        output = llm.create_chat_completion(**completion_args)
        
        return output

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))