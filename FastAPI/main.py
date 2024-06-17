# server.py
import sys, os

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from transformers import AutoModelForCausalLM, AutoTokenizer

import torch

sys.path.append("/home/Chatbot/LangChain/src")
app = FastAPI()

import rm_ollama

# 필요한 모델과 파라미터 설정
model_id = 'beomi/Llama-3-Open-Ko-8B'
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(model_id)

class GenerateRequest(BaseModel):
    question: str

@app.post("/generate")
async def generate(request: GenerateRequest):
    try:
        question = request.question
        data = rm_ollama.run(question, model_id, tokenizer, model)

        response_data = {
            "response": data
        }
        return JSONResponse(content=response_data, status_code=200)
    except Exception as e:
        # 예외 발생시 데이터베이스 연결 종료 후 예외 발생
        raise HTTPException(status_code=500, detail=f"Error generate data: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8722)
