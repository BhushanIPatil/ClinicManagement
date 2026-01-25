"""
User Service

Business logic for user management including registration, 
authentication, and profile management.
"""

from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, or_

from app.infrastructure.database.models.user import User
from app.infrastructure.database.models.user_clinic_role import UserClinicRole
from app.application.dto.user_dto import UserCreateRequest, UserUpdateRequest
from app.core.security.password import get_password_hash, verify_password


class UserService:
    """Service class for user-related operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_user(self, user_data: UserCreateRequest) -> User:
        """
        Create a new user.
        
        Args:
            user_data: User creation data
            
        Returns:
            User: Created user object
            
        Raises:
            ValueError: If email or username already exists
        """
        # Check if email already exists
        existing_email = self.db.query(User).filter(
            User.email == user_data.email,
            User.is_deleted == False
        ).first()
        
        if existing_email:
            raise ValueError("Email already registered")
        
        # Check if username already exists
        existing_username = self.db.query(User).filter(
            User.username == user_data.username,
            User.is_deleted == False
        ).first()
        
        if existing_username:
            raise ValueError("Username already taken")
        
        # Create user with hashed password
        user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=get_password_hash(user_data.password),
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            phone=user_data.phone,
            is_active=True,
            is_superuser=False
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """
        Get user by ID.
        
        Args:
            user_id: User UUID
            
        Returns:
            User or None
        """
        return self.db.query(User).filter(
            User.id == user_id,
            User.is_deleted == False
        ).first()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email.
        
        Args:
            email: User email
            
        Returns:
            User or None
        """
        return self.db.query(User).filter(
            User.email == email,
            User.is_deleted == False
        ).first()
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Get user by username.
        
        Args:
            username: Username
            
        Returns:
            User or None
        """
        return self.db.query(User).filter(
            User.username == username,
            User.is_deleted == False
        ).first()
    
    def get_user_by_username_or_email(self, identifier: str) -> Optional[User]:
        """
        Get user by username or email.
        Eager-loads roles and clinic_role_assignments.role for use after session close (e.g. login).
        """
        return (
            self.db.query(User)
            .options(
                joinedload(User.clinic_role_assignments).options(
                    joinedload(UserClinicRole.role),
                    joinedload(UserClinicRole.clinic),
                ),
            )
            .filter(
                or_(User.email == identifier, User.username == identifier),
                User.is_deleted == False,
            )
            .first()
        )
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """
        Authenticate user with username/email and password.
        
        Args:
            username: Username or email
            password: Plain text password
            
        Returns:
            User if authenticated, None otherwise
        """
        user = self.get_user_by_username_or_email(username)
        
        if not user:
            return None
        
        if not user.is_active:
            return None
        
        if not verify_password(password, user.hashed_password):
            return None
        
        return user
    
    def update_user(self, user_id: UUID, user_data: UserUpdateRequest) -> Optional[User]:
        """
        Update user data.
        
        Args:
            user_id: User UUID
            user_data: Update data
            
        Returns:
            Updated user or None
        """
        user = self.get_user_by_id(user_id)
        
        if not user:
            return None
        
        # Update fields if provided
        update_data = user_data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            if value is not None:
                setattr(user, field, value)
        
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def change_password(self, user_id: UUID, current_password: str, new_password: str) -> bool:
        """
        Change user password.
        
        Args:
            user_id: User UUID
            current_password: Current password
            new_password: New password
            
        Returns:
            bool: True if successful
            
        Raises:
            ValueError: If current password is incorrect
        """
        user = self.get_user_by_id(user_id)
        
        if not user:
            raise ValueError("User not found")
        
        if not verify_password(current_password, user.hashed_password):
            raise ValueError("Current password is incorrect")
        
        user.hashed_password = get_password_hash(new_password)
        self.db.commit()
        
        return True

    def reset_password(self, username_or_email: str, new_password: str) -> bool:
        """
        Set a new password for a user without requiring the current password.
        Use for "forgot password" flows. Identifies user by username or email.

        Args:
            username_or_email: Username or email of the user
            new_password: New plain-text password (will be hashed)

        Returns:
            bool: True if password was reset

        Raises:
            ValueError: If user not found
        """
        user = self.get_user_by_username_or_email(username_or_email)
        if not user:
            raise ValueError("User not found")
        user.hashed_password = get_password_hash(new_password)
        self.db.commit()
        return True

    def delete_user(self, user_id: UUID) -> bool:
        """
        Soft delete a user.
        
        Args:
            user_id: User UUID
            
        Returns:
            bool: True if successful
        """
        user = self.get_user_by_id(user_id)
        
        if not user:
            return False
        
        user.soft_delete()
        self.db.commit()
        
        return True
    
    def list_users(
        self,
        skip: int = 0,
        limit: int = 10,
        is_active: Optional[bool] = None
    ) -> tuple[List[User], int]:
        """
        List users with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            is_active: Filter by active status
            
        Returns:
            Tuple of (list of users, total count)
        """
        query = self.db.query(User).filter(User.is_deleted == False)
        
        if is_active is not None:
            query = query.filter(User.is_active == is_active)
        
        total = query.count()
        users = query.offset(skip).limit(limit).all()
        
        return users, total
