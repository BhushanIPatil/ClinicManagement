"""
Security Dependencies

FastAPI dependencies for authentication and authorization.
Provides current user and role-based access control.

Note: These are placeholders for when async database is implemented.
"""

from typing import Optional, List
from uuid import UUID
from fastapi import HTTPException, status, Header

# Placeholder User class for type hints
class User:
    """Placeholder User class."""
    id: UUID
    username: str
    email: str
    is_active: bool
    role_names: List[str] = []


def get_current_user_placeholder() -> dict:
    """
    Placeholder for getting current user.
    
    In production, implement proper JWT verification.
    
    Returns:
        dict: User info placeholder
    """
    return {
        "message": "Implement JWT authentication",
        "hint": "Pass Authorization: Bearer <token> header"
    }


def require_roles(*required_roles: str):
    """
    Dependency factory for role-based access control.
    
    Creates a dependency that checks if the current user has at least one
    of the required roles.
    
    Args:
        *required_roles: One or more role names required for access
        
    Returns:
        Dependency function that validates user roles
        
    Example:
        @router.get("/admin-only")
        def admin_endpoint(
            user = Depends(require_roles("ADMIN"))
        ):
            ...
    """
    def role_checker() -> dict:
        """
        Check if user has required roles.
        
        Note: This is a placeholder. Implement proper JWT validation.
        
        Returns:
            dict: Placeholder response
        """
        return {
            "message": f"Role check placeholder for roles: {required_roles}",
            "required_roles": list(required_roles)
        }
    
    return role_checker


def require_any_role(*roles: str):
    """
    Alias for require_roles (for clarity).
    
    Args:
        *roles: Role names
        
    Returns:
        Dependency function
    """
    return require_roles(*roles)


def require_all_roles(*required_roles: str):
    """
    Dependency factory that requires user to have ALL specified roles.
    
    Args:
        *required_roles: All role names required for access
        
    Returns:
        Dependency function
    """
    def role_checker() -> dict:
        """Check if user has all required roles."""
        return {
            "message": f"All roles check placeholder: {required_roles}",
            "required_roles": list(required_roles)
        }
    
    return role_checker
