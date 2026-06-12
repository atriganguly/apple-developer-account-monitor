import logging
from contextlib import contextmanager
from typing import Generator
from playwright.sync_api import sync_playwright, BrowserContext, Page

from config.settings import settings
from config.selectors import selectors
from core.exceptions import SessionExpiredError

logger = logging.getLogger("apple_automation.core.browser")

@contextmanager
def get_browser_context() -> Generator[BrowserContext, None, None]:
    """
    Context manager that provisions a cleanly managed Playwright browser and 
    context environment. Automatically applies headless toggles, loading timeouts, 
    and session state preservation schemas. Handles downstream closure gracefully.

    Yields:
        BrowserContext: An active, authenticated Playwright browser context instance.

    Raises:
        SessionExpiredError: If the session file is missing or contains invalid credentials.
    """
    # Defensive path preparation: Ensure session directory structures exist
    if not settings.STORAGE_STATE_PATH.exists():
        settings.STORAGE_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        logger.warning(f"Session tracking state not found at target: {settings.STORAGE_STATE_PATH}")

    with sync_playwright() as p:
        # 1. Initialize browser instance using unified global settings
        logger.info(f"Launching browser (Headless: {settings.HEADLESS})...")
        browser = p.chromium.launch(headless=settings.HEADLESS)
        
        try:
            # 2. Check for existence of auth state file before context instantiation
            context_kwargs = {}
            if settings.STORAGE_STATE_PATH.exists() and settings.STORAGE_STATE_PATH.stat().st_size > 0:
                context_kwargs["storage_state"] = str(settings.STORAGE_STATE_PATH)
                logger.info("Injecting authenticated storage state into browser context.")
            else:
                logger.error("Automation execution stopped. Storage state file is missing or unpopulated.")
                raise SessionExpiredError(
                    f"Authentication storage context file is missing at path: {settings.STORAGE_STATE_PATH}. "
                    f"Please execute the initial headed login routine to populate the required session state tokens."
                )

            # 3. Create fully configured tracking context
            context = browser.new_context(**context_kwargs)
            context.set_default_timeout(settings.TIMEOUT_MS)
            
            # 4. Proactively verify session state validity before running operational routines
            if not verify_session_state(context):
                raise SessionExpiredError(
                    "The active storage state tokens have been explicitly rejected or invalidated by Apple's "
                    "portal gateways. Manual 2FA intervention is required."
                )

            yield context

        finally:
            # 5. Clean up open processes and release resources definitively
            logger.info("Closing active browser engine contexts safely.")
            browser.close()


def verify_session_state(context: BrowserContext) -> bool:
    """
    Navigates to the base portal dashboard endpoint to evaluate if the loaded 
    storage state accurately bypasses authentication boundaries.

    Args:
        context (BrowserContext): The active target browser context to assess.
    Returns:
        bool: True if context successfully authenticates, False if rejected or redirected to login.
    """
    page: Page = context.new_page()
    try:
        logger.info(f"Probing connection validation status at: {settings.APPLE_PORTAL_URL}")
        page.goto(settings.APPLE_PORTAL_URL, wait_until="domcontentloaded")
        
        # Monitor for successful dashboard landing container elements
        page.wait_for_selector(selectors.ACCOUNT_CONTAINER, timeout=30000)
        logger.info("Session context verified successfully. Access granted.")
        return True
    except Exception as e:
        logger.warning(f"Session probe verification check failed: {str(e)}")
        # Check if page context has redirected away or if a sign-in wall element is present
        if "sign-in" in page.url or "login" in page.url:
            logger.error(f"Active session rejected. Browser redirected to auth page: {page.url}")
        return False
    finally:
        page.close()