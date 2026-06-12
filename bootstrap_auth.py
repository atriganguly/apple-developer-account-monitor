import os
import time
from playwright.sync_api import sync_playwright
from pathlib import Path
from dotenv import load_dotenv

# Load configuration paths dynamically
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(dotenv_path=BASE_DIR / ".env")

session_path = Path(os.getenv("APPLE_STORAGE_STATE_PATH", "session/auth.json"))
session_path.parent.mkdir(parents=True, exist_ok=True)

apple_email = os.getenv("APPLE_EMAIL", "")
apple_password = os.getenv("APPLE_PASSWORD", "")

with sync_playwright() as p:
    print("Launching visible browser for semi-automated login setup...")
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://developer.apple.com/account")
    
    try:
        # Apple hosts its login form inside an iframe for security. Let's locate it.
        print("Waiting for Apple Sign-In Widget...")
        page.wait_for_selector("#aid-auth-widget-iFrame", timeout=15000)
        auth_frame = page.frame_locator("#aid-auth-widget-iFrame")
        
        if apple_email and apple_password:
            print(f"Auto-filling credentials for: {apple_email}")
            
            # Type email and submit using the ENTER key (Bypasses disabled buttons)
            email_input = auth_frame.locator("#account_name_text_field")
            email_input.focus()
            email_input.fill(apple_email)
            email_input.press("Enter")
            
            # Wait for password field to slide in via animation
            time.sleep(3)
            
            # Type password and submit using the ENTER key
            password_input = auth_frame.locator("#password_text_field")
            password_input.focus()
            password_input.fill(apple_password)
            password_input.press("Enter")
        else:
            print("Warning: APPLE_EMAIL or APPLE_PASSWORD missing in .env file. Please type manually.")
            
    except Exception as e:
        print(f"\nNote: Auto-fill helper timed out or element structure shifted. Please type manually in the window.\nError Context: {str(e)}")

    print("\n==================================================================")
    print("[ACTION REQUIRED]: Complete the 2FA prompt on your device right now.")
    print("Once your device code is entered and the main Developer Account")
    print("Home Dashboard finishes loading completely, come back here and press ENTER...")
    print("==================================================================\n")
    
    input()
    
    context.storage_state(path=str(session_path))
    print(f"\nSuccess! Authentication cookie context saved safely to: {session_path}")
    browser.close()