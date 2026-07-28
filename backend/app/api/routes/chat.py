"""Chat endpoint — the HTTP surface for talking to the travel agent."""

from fastapi import APIRouter, Depends

from app.agent.orchestrator import TravelAgentOrchestrator
from app.api.deps import get_orchestrator
from app.schemas.conversation import ChatRequest, ChatResponse

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def send_message(
    request: ChatRequest,
    orchestrator: TravelAgentOrchestrator = Depends(get_orchestrator),
) -> ChatResponse:
    return orchestrator.handle_message(request)
