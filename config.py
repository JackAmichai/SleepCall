"""
Configuration module for Meeting Sentinel
Loads environment variables and provides configuration settings
"""
import os
from dotenv import load_dotenv
from typing import List

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration class for Meeting Sentinel"""
    
    # Target names to detect
    TARGET_NAMES: List[str] = os.getenv("TARGET_NAMES", "Jack,Amichai").split(",")
    TARGET_NAMES = [name.strip() for name in TARGET_NAMES if name.strip()]
    
    # Detection settings
    FUZZ_THRESHOLD: int = int(os.getenv("FUZZ_THRESHOLD", "88"))
    ROLLING_BUFFER_MINUTES: int = int(os.getenv("ROLLING_BUFFER_MINUTES", "10"))
    SUMMARY_WINDOW_MINUTES: int = int(os.getenv("SUMMARY_WINDOW_MINUTES", "5"))
    TRIGGER_COOLDOWN_SECONDS: int = int(os.getenv("TRIGGER_COOLDOWN_SECONDS", "90"))
    
    # Azure Speech Service
    AZURE_SPEECH_KEY: str = os.getenv("AZURE_SPEECH_KEY", "")
    AZURE_SPEECH_REGION: str = os.getenv("AZURE_SPEECH_REGION", "")
    
    # LLM Configuration
    USE_AZURE_OPENAI: bool = os.getenv("USE_AZURE_OPENAI", "True").lower() == "true"
    
    # Azure OpenAI
    AZURE_OPENAI_ENDPOINT: str = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    AZURE_OPENAI_API_KEY: str = os.getenv("AZURE_OPENAI_API_KEY", "")
    AZURE_OPENAI_DEPLOYMENT: str = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini")
    
    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    # Alerting
    TEAMS_WEBHOOK_URL: str = os.getenv("TEAMS_WEBHOOK_URL", "")
    SLACK_WEBHOOK_URL: str = os.getenv("SLACK_WEBHOOK_URL", "")
    MEETING_JOIN_URL: str = os.getenv("MEETING_JOIN_URL", "")
    
    @classmethod
    def validate(cls) -> List[str]:
        """Validate required configuration and return list of missing items"""
        missing = []
        
        if not cls.AZURE_SPEECH_KEY:
            missing.append("AZURE_SPEECH_KEY")
        if not cls.AZURE_SPEECH_REGION:
            missing.append("AZURE_SPEECH_REGION")
        
        if cls.USE_AZURE_OPENAI:
            if not cls.AZURE_OPENAI_ENDPOINT:
                missing.append("AZURE_OPENAI_ENDPOINT")
            if not cls.AZURE_OPENAI_API_KEY:
                missing.append("AZURE_OPENAI_API_KEY")
            if not cls.AZURE_OPENAI_DEPLOYMENT:
                missing.append("AZURE_OPENAI_DEPLOYMENT")
        else:
            if not cls.OPENAI_API_KEY:
                missing.append("OPENAI_API_KEY")
        
        if not cls.TARGET_NAMES:
            missing.append("TARGET_NAMES")
        
        return missing
    
    @classmethod
    def print_config(cls):
        """Print current configuration (masked sensitive values)"""
        print("=== Meeting Sentinel Configuration ===")
        print(f"Target Names: {', '.join(cls.TARGET_NAMES)}")
        print(f"Fuzz Threshold: {cls.FUZZ_THRESHOLD}")
        print(f"Rolling Buffer: {cls.ROLLING_BUFFER_MINUTES} minutes")
        print(f"Summary Window: {cls.SUMMARY_WINDOW_MINUTES} minutes")
        print(f"Cooldown: {cls.TRIGGER_COOLDOWN_SECONDS} seconds")
        print(f"Azure Speech Region: {cls.AZURE_SPEECH_REGION}")
        print(f"Use Azure OpenAI: {cls.USE_AZURE_OPENAI}")
        if cls.USE_AZURE_OPENAI:
            print(f"Azure OpenAI Deployment: {cls.AZURE_OPENAI_DEPLOYMENT}")
        else:
            print(f"OpenAI Model: {cls.OPENAI_MODEL}")
        print(f"Teams Webhook: {'Configured' if cls.TEAMS_WEBHOOK_URL else 'Not configured'}")
        print(f"Slack Webhook: {'Configured' if cls.SLACK_WEBHOOK_URL else 'Not configured'}")
        print("=" * 40)


# Create a singleton instance
config = Config()
