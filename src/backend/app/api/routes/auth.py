from datetime import datetime
import logging
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer

from app.lib.address import validate_wallet_address
from app.models.auth import WalletAuth, Token
from app.services.auth_service import WalletAuthService
from app.middleware.auth_middleware import verify_auth

router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()
auth_service = WalletAuthService()

logger = logging.getLogger(__name__)


@router.get("/nonce/{wallet_address}")
async def get_nonce(wallet_address: str):
    """Get a nonce for wallet signing"""
    logger.info("Generating nonce")
    if not validate_wallet_address(wallet_address):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid wallet address"
        )

    nonce = auth_service.generate_nonce(wallet_address)

    return {"nonce": nonce}


@router.post("/verify-wallet", response_model=Token)
async def verify_wallet(wallet_auth: WalletAuth, request: Request):
    """Verify wallet signature and issue token"""
    logging.info(f"verifying wallet with address: {wallet_auth.address}")
    is_valid, chain_type = validate_wallet_address(wallet_auth.address)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid wallet address"
        )

    device_info = {
        "user_agent": request.headers.get("user-agent", "Unknown"),
        "ip_address": request.client.host,
        "device_type": "Browser",
        "chain_type": chain_type,
        "timestamp": datetime.now().isoformat(),
    }

    try:
        auth_result = await auth_service.authenticate_wallet(wallet_auth, device_info)
        if not auth_result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid signature"
            )
        logging.info(f"{wallet_auth.address} is authenticated")
        return auth_result
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=(
                e.status_code
                if isinstance(e, HTTPException)
                else status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=str(e),
        )


@router.get("/me")
async def read_users_me(token: str = Depends(verify_auth)):
    return {"wallet_address": token["sub"]}


@router.get("/sessions")
async def get_user_sessions(token: dict = Depends(verify_auth)):
    """Get all active sessions for current user"""
    sessions = await auth_service.session_service.get_user_sessions(token["sub"])
    return {"sessions": sessions}


@router.post("/sessions/{session_id}/revoke")
async def revoke_session(session_id: str, token: dict = Depends(verify_auth)):
    """Revoke a specific session"""
    session = await auth_service.session_service.get_session(session_id)
    if not session or session["wallet_address"] != token["sub"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
        )

    await auth_service.session_service.invalidate_session(session_id)
    return {"message": "Session revoked successfully"}


@router.post("/sessions/revoke-all")
async def revoke_all_sessions(token: dict = Depends(verify_auth)):
    """Revoke all sessions for current user"""
    sessions = await auth_service.session_service.get_user_sessions(token["sub"])
    for session in sessions:
        await auth_service.session_service.invalidate_session(session["session_id"])
    return {"message": "All sessions revoked successfully"}
