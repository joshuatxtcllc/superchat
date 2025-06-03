
import os
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class AppConfig:
    """Application configuration"""
    
    # API Configuration
    openai_api_key: str = os.environ.get('OPENAI_API_KEY', '')
    anthropic_api_key: str = os.environ.get('ANTHROPIC_API_KEY', '')
    
    # Rate Limiting
    max_messages_per_session: int = 20
    min_time_between_messages: float = 2.0
    max_message_length: int = 10000
    
    # Model Configuration
    default_model: str = "gpt-4o"
    max_tokens: int = 1000
    temperature: float = 0.7
    
    # Storage
    conversation_history_dir: str = "conversation_history"
    logs_dir: str = "logs"
    
    # Features
    enable_mcp: bool = True
    enable_model_comparison: bool = True
    enable_conversation_starters: bool = True
    
    # Security
    enable_input_sanitization: bool = True
    enable_rate_limiting: bool = True
    
    @classmethod
    def load(cls) -> 'AppConfig':
        """Load configuration from environment"""
        return cls()
    
    def validate(self) -> Dict[str, Any]:
        """Validate configuration and return status"""
        issues = []
        
        if not self.openai_api_key:
            issues.append("OpenAI API key not configured")
            
        if not self.anthropic_api_key:
            issues.append("Anthropic API key not configured")
            
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "api_keys_configured": bool(self.openai_api_key or self.anthropic_api_key)
        }
