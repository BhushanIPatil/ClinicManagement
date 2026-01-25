"""
JWT Token Service

This module handles JWT token creation and verification for authentication.
"""

from datetime import datetime, timedelta
from typing import Any, Optional
from jose import JWTError, jwt

from app.core.config import settings


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Data to encode in the token
        expires_delta: Optional expiration time delta
        
    Returns:
        str: Encoded JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """
    Verify and decode a JWT token.
    
    Args:
        token: JWT token to verify
        
    Returns:
        dict: Decoded token payload or None if invalid
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None


def get_token_data(token: str, key: str) -> Optional[Any]:
    """
    Get specific data from a token.
    
    Args:
        token: JWT token
        key: Key to extract from payload
        
    Returns:
        Any: Value for the key or None
    """
    payload = verify_token(token)
    if payload:
        return payload.get(key)
    return None
