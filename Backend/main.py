"""
FinBridge AI — Backend Server
FastAPI + OpenAI/Anthropic LLM for student finance AI agent
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os

from agent import FinBridgeAgent
from tools import CurrencyTool, RemittanceTool, BudgetTool, TuitionTool

app = FastAPI(title="FinBridge AI", version="1.0.0")

# CORS — allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agent and tools
agent = FinBridgeAgent()
currency_tool = CurrencyTool()
remittance_tool = RemittanceTool()
budget_tool = BudgetTool()
tuition_tool = TuitionTool()


# ===== Request/Response Models =====
class ChatRequest(BaseModel):
    message: str
    conversation_id: str | None = None

class ChatResponse(BaseModel):
    reply: str
    tool_used: str | None = None
    data: dict | None = None

class CurrencyRequest(BaseModel):
    from_currency: str
    to_currency: str
    amount: float

class RemittanceRequest(BaseModel):
    from_country: str
    to_country: str
    amount: float


# ===== API Endpoints =====

@app.get("/")
async def root():
    return {"status": "online", "service": "FinBridge AI Agent"}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main AI chat endpoint — processes user query through the agent"""
    try:
        result = await agent.process(request.message)
        return ChatResponse(
            reply=result["reply"],
            tool_used=result.get("tool_used"),
            data=result.get("data")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/convert")
async def convert_currency(request: CurrencyRequest):
    """Currency conversion endpoint"""
    result = await currency_tool.convert(
        request.from_currency,
        request.to_currency,
        request.amount
    )
    return result


@app.post("/api/remittance")
async def compare_remittance(request: RemittanceRequest):
    """Remittance comparison endpoint"""
    result = await remittance_tool.compare(
        request.from_country,
        request.to_country,
        request.amount
    )
    return result


@app.get("/api/rates/{base}")
async def get_rates(base: str = "USD"):
    """Get exchange rates for a base currency"""
    return await currency_tool.get_rates(base)


@app.get("/api/tuition/{country}")
async def get_tuition_guide(country: str):
    """Get tuition payment guide for a country"""
    return await tuition_tool.get_guide(country)


@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "agent": "ready"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
