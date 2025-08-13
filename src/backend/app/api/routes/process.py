import dataclasses
from typing import Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
import logging
import os
import json

from app.agent.manager import AgentManager
from app.agent.manager import AgentManager
from app.middleware.auth_middleware import verify_auth
from app.models.prompt_analysis import PromptType, TokenResponse
from app.models.response import ResponseType
from app.services.processing.prompt_processing_service import PromptProcessingServiceV2
from app.services.reasoning.insight_service import InsightService
from app.services.message_service import MessageService
from app.services.rate_limiter import RateLimiter
from app.services.reasoning.reasoning_service import ReasoningService
from app.services.reasoning.agent_response_service import AgentResponseService
from app.services.thread_service import ThreadService
from app.services.data_access.data_access_service import DataAccessService


router = APIRouter()
reasoning_service = ReasoningService()
insight_service = InsightService()
agent_response_service = AgentResponseService()
thread_service = ThreadService()
prompt_processing_service = PromptProcessingServiceV2()
data_access_service = DataAccessService()


class PromptRequest(BaseModel):
    prompt: str
    thread_id: str | None = None


@router.get("/health")
def health_check():
    return {"status": True}


@router.websocket("/ws/v4/process-prompt")
async def websocket_process_promptv4(
    websocket: WebSocket,
    # auth_data: dict = Depends(verify_auth)
):
    await websocket.accept()
    try:
        # user_wallet = auth_data["wallet_address"]
        # session_id = auth_data["session_id"]
        user_wallet = "0x1234"
        session_id = str(uuid.uuid4())

        # Send initial connection success message
        await websocket.send_json(
            {
                "type": "connection",
                "message": "WebSocket connection established",
                "session_id": session_id,
            }
        )

        while True:
            try:
                # Receive message from client
                data = await websocket.receive_text()
                logging.info(f"Received data: {data}")
                request_data = json.loads(data)

                if not request_data.get("prompt", "").strip():
                    await websocket.send_json(
                        {"type": "error", "message": "Prompt cannot be empty"}
                    )
                    continue

                # Check rate limit
                await RateLimiter().check_rate_limit(session_id, "api")

                # Process the prompt
                manager = AgentManager()
                response = await manager.run(
                    request_data["prompt"],
                    user_wallet,
                    request_data.get("thread_id"),
                    session_id=session_id,
                )

                # Send response back to client
                # await websocket.send(response)
                await websocket.send_json(response.model_dump())

            except WebSocketDisconnect:
                break
            except Exception as e:
                await websocket.send_json({"type": "error", "message": str(e)})

    except Exception as e:
        await websocket.close(code=4000, reason=str(e))


@router.post("/v4/process-prompt")
async def process_promptv4(request: PromptRequest):
    try:
        user_wallet = "0x1234"
        session_id = str(uuid.uuid4())
        # user_wallet = auth_data["wallet_address"]
        # session_id = auth_data["session_id"]
        if not request.prompt.strip():
            raise HTTPException(status_code=400, detail="Prompt cannot be empty")
        logging.info(f"Processing prompt: {request.prompt}")
        logging.info(f"User wallet: {user_wallet}")
        await RateLimiter().check_rate_limit(session_id, "api")
        manager = AgentManager()
        return await manager.run(
            request.prompt, user_wallet, request.thread_id, session_id=session_id
        )
    except Exception as e:
        raise e


@router.post("/v3/process-prompt")
async def process_promptv3(
    request: PromptRequest, auth_data: dict = Depends(verify_auth)
):
    try:
        # user_wallet = '0x1234'
        user_wallet = auth_data["wallet_address"]
        if not request.prompt.strip():
            raise HTTPException(status_code=400, detail="Prompt cannot be empty")
        logging.info(f"Processing prompt: {request.prompt}")
        logging.info(f"User wallet: {user_wallet}")
        await RateLimiter().check_rate_limit(auth_data["session_id"], "api")
        thread_id = request.thread_id
        logging.info(f"Thread ID: {thread_id}")
        if thread_id == None or thread_id.strip() == None:
            thread_id = thread_service.create_thread(
                user_id=user_wallet, initial_message=request.prompt.strip()
            )
        else:
            thread_service.add_message(
                thread_id=thread_id, role="user", content=request.prompt
            )
        thread_messages = thread_service.get_thread_messages(thread_id=thread_id)
        agent_response, thread_messages, asset_data = agent_response_service.respond(
            thread_messages
        )
        thread_service.add_message(
            thread_id=thread_id, role="assistant", content=agent_response.output_text
        )
        agent_response, thread_messages, asset_data = agent_response_service.respond(
            thread_messages
        )
        thread_service.add_message(
            thread_id=thread_id, role="assistant", content=agent_response.output_text
        )
        metadata = None
        if asset_data and len(asset_data) > 0:
            if (
                isinstance(asset_data, list)
                and "data" in asset_data[0]
                and "metadata" in asset_data[0]["data"]
            ):
                metadata = TokenResponse.model_validate(
                    asset_data[0]["data"]["metadata"]
                )
            if (
                isinstance(asset_data, list)
                and "data" in asset_data[0]
                and "metadata" in asset_data[0]["data"]
            ):
                metadata = TokenResponse.model_validate(
                    asset_data[0]["data"]["metadata"]
                )
        return {
            "type": ResponseType.SUCCESS.value,
            "message": request.prompt,
            "metadata": metadata,
            "data": asset_data,
            "insight": agent_response.output_text,
            "thread_id": thread_id,
            "thread_id": thread_id,
        }
    except Exception as e:
        import traceback

        error_response = {
            "type": ResponseType.ERROR.value,
            "message": str(e),
            "metadata": None,
            "data": None,
            "thread_id": thread_id,
            "thread_id": thread_id,
        }
        insight = insight_service.generate(error_response, request.prompt)
        logging.error(f"Error processing prompt: {e}")
        logging.error(f"Stack trace: {traceback.format_exc()}")

        return {**error_response, "insight": insight}


@router.post("/v2/process-prompt")
async def process_promptv2(
    request: PromptRequest, auth_data: dict = Depends(verify_auth)
):
    try:
        if not request.prompt.strip():
            raise HTTPException(status_code=400, detail="Prompt cannot be empty")
        logging.info("Initiating check for rate limits")
        await RateLimiter().check_rate_limit(auth_data["session_id"], "api")
        logging.info("Initializing prompt analysis")
        promptAnalysis = await reasoning_service.analyze(
            prompt=request.prompt, session_id=auth_data["session_id"]
        )
        if promptAnalysis.type == PromptType.GENERAL_QUERY:
            logging.info("Returning insight for a GENERAL QUERY")
            insight = insight_service.generate_raw(request.prompt)
            return {
                "type": ResponseType.SUCCESS,
                "message": request.prompt,
                "metadata": None,
                "data": None,
                "insight": insight,
                "session_id": auth_data["session_id"],
            }
        logging.info(f"Processing the prompt")
        processed_prompt = prompt_processing_service.process(promptAnalysis)
        insight = insight_service.generate_for_processed_prompt(
            processed_prompt=processed_prompt,
            auth_data=auth_data,
            session_id=auth_data["session_id"],
        )
        logging.info("Generating insight")
        return {
            "type": ResponseType.SUCCESS,
            "message": request.prompt,
            "metadata": processed_prompt.metadata,
            "data": None,
            "insight": insight,
            "session_id": auth_data["session_id"],
        }
    except Exception as e:
        error_response = {
            "type": ResponseType.ERROR.value,
            "message": str(e),
            "metadata": None,
            "data": None,
        }
        insight = insight_service.generate(error_response, request.prompt)
        logging.error(f"Error processing prompt: {e}")
        return {**error_response, "insight": insight}


@router.get("/messages/history/session")
async def get_session_history(auth_data: dict = Depends(verify_auth)):
    """Get message history for current session"""
    message_service = MessageService()
    messages = message_service.get_session_history(auth_data["session_id"])
    return {"messages": messages}


@router.get("/messages/history/all")
async def get_all_history(auth_data: dict = Depends(verify_auth)):
    """Get all message history for the wallet"""
    message_service = MessageService()
    messages = message_service.get_all_wallet_messages(auth_data["wallet_address"])
    return {"sessions": messages}


@router.delete("/messages/history/session")
async def clear_session_history(auth_data: dict = Depends(verify_auth)):
    """Clear message history for current session"""
    message_service = MessageService()
    message_service.clear_session_history(auth_data["session_id"])
    return {"message": "Session history cleared"}


@router.delete("/messages/history/all")
async def clear_all_history(auth_data: dict = Depends(verify_auth)):
    """Clear all message history for the wallet"""
    message_service = MessageService()
    message_service.clear_wallet_history(auth_data["wallet_address"])
    return {"message": "All message history cleared"}


@router.get("/tokenmetrics/{symbol}")
async def handle_token_select(symbol: str, chain: Optional[str] = None):
    """
    Called when a user clicks a token from the bottom-left list in the UI.
    Fetches token metadata and triggers chart rebuild.
    """
    return await data_access_service.get_selected_token_metadata(symbol, chain)
