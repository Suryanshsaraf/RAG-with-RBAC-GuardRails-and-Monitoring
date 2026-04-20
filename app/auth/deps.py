"""
Auth Dependencies.

FastAPI dependencies for securing endpoints and extracting user roles.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

from app.auth.handler import decode_access_token

# Token URL for OAuth2 (will be implemented in main.py)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class UserSession(BaseModel):
    username: str
    role: str


async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserSession:
    """
    Dependency to validate the JWT and return user session data.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    username: str = payload.get("sub")
    role: str = payload.get("role", "general")
    
    if username is None:
        raise credentials_exception
    
    return UserSession(username=username, role=role)


def role_required(required_role: str):
    """
    Dependency factory to enforce a specific role requirement.
    """
    async def role_checker(user: UserSession = Depends(get_current_user)):
        # Admin can access everything
        if user.role.lower() == "admin":
            return user
            
        if user.role.lower() != required_role.lower():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation not permitted for role: {user.role}. Required: {required_role}"
            )
        return user
        
    return role_checker
