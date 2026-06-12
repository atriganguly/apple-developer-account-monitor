import logging
import time
from playwright.sync_api import BrowserContext, Page

from config.settings import settings
from config.selectors import selectors

logger = logging.getLogger("apple_automation.services.keep_alive")

def run_keep_alive(context: BrowserContext) -> bool:
    """
    Executes a session validation and renewal cycle. Opens a new page inside 
    the current authenticated context, accesses the account workspace, 
    and saves the freshly updated background session cookies back to disk.

    Args:
        context (BrowserContext): The currently initialized browser context.
    Returns:
        bool: True if the session was successfully refreshed, False otherwise.
    """
    page: Page = context.new_page()
    try:
        logger.info("Executing periodic session maintenance sequence...")
        logger.info(f"Targeting ping validation endpoint: {settings.APPLE_PORTAL_URL}")
        
        # 1. Access the main page with a robust network settlement wait time
        page.goto(settings.APPLE_PORTAL_URL, wait_until="networkidle")
        
        # 2. Hard structural checkpoint to guarantee we are past any authentication walls
        page.wait_for_selector(selectors.ACCOUNT_CONTAINER, timeout=10000)
        logger.info("Dashboard verification anchor found. Account session is completely active.")
        
        # 3. Graceful rest period to let asynchronous background OAuth tokens or telemetry cookies settle
        logger.info("Resting page context for 5 seconds to ensure backend auth handshakes complete...")
        time.sleep(5)
        
        # 4. Save the refreshed state directly back to your persistent disk layer
        logger.info(f"Updating sliding cookie window on disk: {settings.STORAGE_STATE_PATH}")
        context.storage_state(path=str(settings.STORAGE_STATE_PATH))
        logger.info("Session state file written cleanly. Keep-alive execution finished successfully.")
        return True
        
    except Exception as e:
        logger.error(
            f"Keep-alive pipeline encountered a processing failure during session ping: {str(e)}. "
            f"The session state may be corrupted or expired."
        )
        return False
        
    finally:
        page.close()