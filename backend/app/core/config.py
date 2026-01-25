"""
Configuration Management Module

This module handles environment-based configuration using Pydantic Settings.
It loads configuration from environment variables with proper validation and type safety.

Key Features:
- Environment-based configuration (development, staging, production)
- Type-safe settings with Pydantic
- Automatic validation
- Support for .env files
"""

from typing import List, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application Settings
    
    Loads configuration from environment variables with the following priority:
    1. Environment variables
    2. .env file
    3. Default values
    
    All settings are validated and type-checked by Pydantic.
    """
    
    # Application Settings
    APP_NAME: str = "Clinic Management System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    
    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database Configuration (SQL Server)
    DB_DRIVER: str = "ODBC Driver 17 for SQL Server"
    DB_SERVER: str = "localhost"
    DB_PORT: int = 1433
    DB_NAME: str = "cliniccrmdb"
    DB_USER: str = ""
    DB_PASSWORD: str = ""
    DB_TRUSTED_CONNECTION: bool = False
    DB_ENCRYPT: bool = True
    DB_TRUST_SERVER_CERTIFICATE: bool = True
    
    # Database Connection Pool Settings
    DB_POOL_SIZE: int = Field(default=10, ge=1, le=100)
    DB_MAX_OVERFLOW: int = Field(default=20, ge=0)
    DB_POOL_PRE_PING: bool = True  # Verify connections before using
    DB_ECHO: bool = False  # Log SQL queries (set to True for debugging)
    
    # Security Settings
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS Settings
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]
    
    @property
    def database_url(self) -> str:
        """
        Construct SQL Server connection string.
        
        Returns:
            SQL Server connection string in SQLAlchemy format
        """
        if self.DB_TRUSTED_CONNECTION:
            # Windows Authentication
            return (
                f"mssql+pyodbc://@{self.DB_SERVER}/{self.DB_NAME}"
                f"?driver={self.DB_DRIVER.replace(' ', '+')}"
                f"&Trusted_Connection=yes"
                f"&Encrypt={'yes' if self.DB_ENCRYPT else 'no'}"
                f"&TrustServerCertificate={'yes' if self.DB_TRUST_SERVER_CERTIFICATE else 'no'}"
            )
        else:
            # SQL Server Authentication
            return (
                f"mssql+pyodbc://{self.DB_USER}:{self.DB_PASSWORD}@"
                f"{self.DB_SERVER}:{self.DB_PORT}/{self.DB_NAME}"
                f"?driver={self.DB_DRIVER.replace(' ', '+')}"
                f"&Encrypt={'yes' if self.DB_ENCRYPT else 'no'}"
                f"&TrustServerCertificate={'yes' if self.DB_TRUST_SERVER_CERTIFICATE else 'no'}"
            )
    
    @property
    def database_url_async(self) -> str:
        """
        Construct async SQL Server connection string.
        
        Note: For true async with SQL Server, consider using aioodbc or
        asyncpg with a PostgreSQL database. The current setup uses
        SQLAlchemy's async engine which works with pyodbc.
        
        Returns:
            Async SQL Server connection string
        """
        # Replace mssql+pyodbc with mssql+aioodbc for true async (requires aioodbc)
        # For now, using SQLAlchemy's async support with pyodbc
        base_url = self.database_url.replace("mssql+pyodbc://", "mssql+aioodbc://")
        return base_url
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"  # Ignore extra environment variables
    )


# Global settings instance
# This will be initialized when the module is imported
settings = Settings()
