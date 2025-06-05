
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from model_handler import ModelHandler
from mcp_handler import MCPHandler
import uvicorn

app = FastAPI(title="Multi-Model Chat API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model_handler = ModelHandler()
mcp_handler = MCPHandler()

class ChatRequest(BaseModel):
    message: str
    model: str = "gpt-4o"
    conversation_history: list = []
    deep_thinking: bool = False

class ChatResponse(BaseModel):
    response: str
    model: str
    timestamp: str
    success: bool

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        # Prepare messages
        messages = request.conversation_history + [{"role": "user", "content": request.message}]
        messages_for_api = mcp_handler.prepare_messages(messages)
        
        # Get response
        response = model_handler.get_response(
            messages_for_api, 
            request.model,
            deep_thinking=request.deep_thinking
        )
        
        from datetime import datetime
        return ChatResponse(
            response=response,
            model=request.model,
            timestamp=datetime.now().isoformat(),
            success=True
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/models")
async def get_available_models():
    return {"models": list(model_handler.models.keys())}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("api_server:app", host="0.0.0.0", port=8080, reload=True)
