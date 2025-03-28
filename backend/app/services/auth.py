import logging
import json
from typing import Dict, Any, Optional
from fastapi import HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import firebase_admin
from firebase_admin import credentials, auth
from ..config import settings

# Configure logging
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

class AuthService:
    def __init__(self):
        self.firebase_app = None
        self.initialized = False
        self.initialize_firebase()
    
    def initialize_firebase(self):
        """Initialize Firebase Admin SDK"""
        try:
            # Check if Firebase credentials file exists
            if settings.firebase_credentials:
                try:
                    # Initialize Firebase Admin SDK
                    cred = credentials.Certificate(settings.firebase_credentials)
                    if not firebase_admin._apps:
                        self.firebase_app = firebase_admin.initialize_app(cred)
                    else:
                        self.firebase_app = firebase_admin.get_app()
                    
                    self.initialized = True
                    logger.info("Firebase Admin SDK initialized successfully")
                except Exception as e:
                    logger.error(f"Error initializing Firebase Admin SDK: {str(e)}")
                    # Continue without Firebase for development
                    self.initialized = False
            else:
                logger.warning("Firebase credentials not provided, authentication will be simulated")
                self.initialized = False
        except Exception as e:
            logger.error(f"Error in initialize_firebase: {str(e)}")
            self.initialized = False
    
    async def create_user(self, email: str, password: str, display_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new user in Firebase Authentication
        
        Args:
            email: User's email address
            password: User's password
            display_name: User's display name (optional)
            
        Returns:
            User data dictionary
        """
        if not self.initialized:
            logger.warning("Firebase not initialized, simulating user creation")
            # Simulate user creation for development
            return {
                "uid": f"simulated-uid-{email.replace('@', '-').replace('.', '-')}",
                "email": email,
                "displayName": display_name or email.split('@')[0],
                "emailVerified": False
            }
        
        try:
            # Create user in Firebase
            user_record = auth.create_user(
                email=email,
                password=password,
                display_name=display_name
            )
            
            logger.info(f"User created in Firebase: {user_record.uid}")
            
            # Convert UserRecord to dict
            user_data = {
                "uid": user_record.uid,
                "email": user_record.email,
                "displayName": user_record.display_name,
                "emailVerified": user_record.email_verified
            }
            
            return user_data
        except Exception as e:
            logger.error(f"Error creating user in Firebase: {str(e)}")
            raise HTTPException(
                status_code=400,
                detail=f"Error creating user: {str(e)}"
            )
    
    async def verify_token(self, credentials: Dict[str, str]) -> Dict[str, Any]:
        """
        Verify Firebase ID token
        
        Args:
            credentials: Dictionary containing the token
            
        Returns:
            Decoded token data
        """
        if not self.initialized:
            logger.warning("Firebase not initialized, simulating token verification")
            # Simulate token verification for development
            return {
                "uid": "simulated-uid",
                "email": "dev@example.com",
                "name": "Development User"
            }
        
        try:
            token = credentials.get("credentials")
            if not token:
                raise HTTPException(
                    status_code=401,
                    detail="No authentication token provided"
                )
            
            # Verify the token
            decoded_token = auth.verify_id_token(token)
            
            logger.info(f"Token verified for user: {decoded_token.get('uid')}")
            
            return decoded_token
        except Exception as e:
            logger.error(f"Error verifying token: {str(e)}")
            raise HTTPException(
                status_code=401,
                detail=f"Invalid authentication token: {str(e)}"
            )

# Create security scheme for token authentication
security = HTTPBearer()

# Create global auth service instance
auth_service = AuthService()

async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """
    Dependency to get the current authenticated user
    
    Args:
        request: FastAPI request object
        credentials: HTTP Bearer token credentials
        
    Returns:
        User data from the decoded token
    """
    # For development/testing, allow bypassing authentication
    if settings.debug:
        # Check for a special header that indicates we're in development mode
        dev_mode = request.headers.get("X-Development-Mode")
        if dev_mode == "true":
            logger.warning("Using development mode authentication bypass")
            return {
                "uid": "dev-user-id",
                "email": "dev@example.com",
                "name": "Development User"
            }
    
    try:
        user = await auth_service.verify_token({"credentials": credentials.credentials})
        return user
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error in get_current_user: {str(e)}")
        raise HTTPException(
            status_code=401,
            detail=f"Authentication error: {str(e)}"
        )
