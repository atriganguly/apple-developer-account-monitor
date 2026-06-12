import os
from pathlib import Path
from dataclasses import dataclass, field
from dotenv import load_dotenv

# Dynamically resolve root project directory to ensure paths work from any execution context
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from the .env file if it exists
load_dotenv(dotenv_path=BASE_DIR / ".env")

def _parse_bool(val: str) -> bool:
    """Helper to convert environment variable strings safely to boolean values."""
    if isinstance(val, bool):
        return val
    return str(val).lower() in ("true", "1", "yes", "on")

@dataclass(frozen=True)
class AutomationSettings:
    """
    Unified Application Settings Registry.
    Loads values from system environment variables with robust fallback defaults.
    Implements a frozen dataclass to prevent runtime state mutations.
    """
    # Framework Execution Flags
    HEADLESS: bool = field(
        default_factory=lambda: _parse_bool(os.getenv("PLAYWRIGHT_HEADLESS", "True"))
    )
    TIMEOUT_MS: int = field(
        default_factory=lambda: int(os.getenv("PLAYWRIGHT_TIMEOUT_MS", "30000"))
    )
    
    # State Persistence Paths
    STORAGE_STATE_PATH: Path = field(
        default_factory=lambda: Path(os.getenv("APPLE_STORAGE_STATE_PATH", BASE_DIR / "session" / "auth.json"))
    )
    
    # Apple Developer Portal Targets
    APPLE_PORTAL_URL: str = "https://developer.apple.com/account"
    
    # Google Sheets Integration Settings
    GOOGLE_SHEET_ID: str = field(
        default_factory=lambda: os.getenv("GOOGLE_SHEET_ID", "")
    )
    GOOGLE_CREDS_PATH: Path = field(
        default_factory=lambda: Path(os.getenv("GOOGLE_CREDS_PATH", BASE_DIR / "creds.json"))
    )
    GOOGLE_SHEET_RANGE: str = field(
        default_factory=lambda: os.getenv("GOOGLE_SHEET_RANGE", "'Apple Developer Account Monitor'!A2")
    )
    
    # Google Drive Persistence Configuration (Phase 1 Expansion)
    GOOGLE_DRIVE_FOLDER_ID: str = field(
        default_factory=lambda: os.getenv("GOOGLE_DRIVE_FOLDER_ID", "")
    )
    
    # Apple Account Credentials
    APPLE_EMAIL: str = field(
        default_factory=lambda: os.getenv("APPLE_EMAIL", "")
    )
    APPLE_PASSWORD: str = field(
        default_factory=lambda: os.getenv("APPLE_PASSWORD", "")
    )
    
    # Execution Windows (Interval metadata trackers for runtime checks)
    KEEP_ALIVE_DAYS: int = 5
    SCRAPE_INTERVAL_DAYS: int = 30

# Initialize a single immutable instance to be imported across all components
settings = AutomationSettings()