from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer
from app.services.session_service import SessionService
import jwt
from app.core.config import settings

security = HTTPBearer()


async def verify_auth(request: Request, token: str = Depends(security)) -> dict:
    """Verify both JWT token and session"""
    try:
        # Verify JWT token
        payload = jwt.decode(
            token.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )

        # Get session ID from headers
        session_id = request.headers.get("X-Session-ID")
        if not session_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session ID is required",
            )

        # Verify session exists and is active
        session_service = SessionService()
        session = await session_service.get_session(session_id)

        if not session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired session",
            )

        if not session["is_active"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Session is inactive"
            )

        # Verify token matches session
        if session["token"] != token.credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Token mismatch"
            )

        # Update session activity
        await session_service.update_session_activity(session_id)

        return {"wallet_address": payload["sub"], "session_id": session_id}

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired"
        )
    except jwt.DecodeError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
