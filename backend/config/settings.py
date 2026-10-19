"""
Application configuration settings
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Monday.com Configuration
    monday_api_token: str = Field(..., env='MONDAY_API_TOKEN')
    monday_deals_board_id: str = Field(..., env='MONDAY_DEALS_BOARD_ID')
    monday_work_orders_board_id: str = Field(..., env='MONDAY_WORK_ORDERS_BOARD_ID')
    monday_api_url: str = Field(default='https://api.monday.com/v2', env='MONDAY_API_URL')
    monday_api_rate_limit: int = Field(default=100, env='MONDAY_API_RATE_LIMIT')
    monday_api_rate_period: int = Field(default=60, env='MONDAY_API_RATE_PERIOD')
    
    # LLM Configuration
    llm_api_key: str = Field(..., env='LLM_API_KEY')
    llm_provider: str = Field(default='openai', env='LLM_PROVIDER')
    llm_model: Optional[str] = Field(default=None, env='LLM_MODEL')
    
    # Application Configuration
    frontend_url: str = Field(default='http://localhost:3000', env='FRONTEND_URL')
    log_level: str = Field(default='INFO', env='LOG_LEVEL')
    
    # API Configuration
    api_host: str = Field(default='0.0.0.0', env='API_HOST')
    api_port: int = Field(default=8000, env='API_PORT')
    
    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        case_sensitive = False


# Global settings instance
settings = Settings()
