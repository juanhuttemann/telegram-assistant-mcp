import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_env_var(var_name: str, var_type=str):
    """Get environment variable with validation."""
    value = os.getenv(var_name)
    if not value:
        raise ValueError(f"{var_name} environment variable is required")
    
    if var_type == int:
        try:
            return int(value)
        except ValueError:
            raise ValueError(f"{var_name} must be a valid integer")
    
    return value

# Load configuration
TOKEN = get_env_var('TELEGRAM_BOT_TOKEN')
CHAT_ID = get_env_var('TELEGRAM_CHAT_ID', int)

# Message formatting constants
STATUS_EMOJIS = {
    "started": "🚀",
    "in_progress": "⏳",
    "completed": "✅",
    "error": "❌"
}

PRIORITY_EMOJIS = {
    "low": "💬",
    "normal": "📝",
    "high": "⚠️",
    "urgent": "🚨"
}
