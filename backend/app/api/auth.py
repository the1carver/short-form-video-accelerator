from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any
from ..services.auth import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register")
async def register_user(
    email: str = Body(...),
    password: str = Body(...),
    display_name: str = Body(None)
) -> Dict[str, Any]:
    """Register a new user."""
    try:
        user = await auth_service.create_user(email, password, display_name)
        return {"message": "User registered successfully", "user": user}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/verify-token")
async def verify_token(token: str = Body(...)) -> Dict[str, Any]:
    """Verify a Firebase ID token."""
    try:
        decoded_token = await auth_service.verify_token({"credentials": token})
        return {"valid": True, "user": decoded_token}
    except HTTPException as e:
        return {"valid": False, "error": e.detail}
