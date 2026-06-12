import sys
import json
import time
import argparse
import logging
from config.settings import settings
from core.browser import get_browser_context
from core.exceptions import SessionExpiredError, GoogleSheetsSyncError, AppleAutomationError
from services.scraper import scrape_all_teams
from services.keep_alive import run_keep_alive
from services.sheets import initialize_google_sheets, sync_row_to_google_sheets
from services.drive_sync import download_state_from_drive, upload_state_to_drive

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("apple_automation.main")

def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Bulletproof Apple Developer Portal Smart Monitoring Engine.")
    parser.add_argument(
        "--mode", type=str, required=True,
        choices=["scrape", "keep-alive", "scheduled"],
        help="Specify processing execution profile variant"
    )
    parser.add_argument("--headed", action="store_true", default=False)
    parser.add_argument("--dev", action="store_true", default=False)
    parser.add_argument("--keep-alive-days", type=int, default=3)
    parser.add_argument("--scrape-days", type=int, default=14)
    return parser.parse_args()

def main() -> None:
    args = parse_arguments()

    if args.headed:
        logger.info("CLI Override: Forcing browser execution environment into HEADED visual display mode.")
        object.__setattr__(settings, "HEADLESS", False)

    # 1. Download active configurations from Google Drive
    logger.info("Synchronizing data configurations matrix from Google Drive storage...")
    download_state_from_drive()

    # 2. Initialize default parameters inside config.json if missing
    config_data = {"last_keep_alive": 0, "last_scrape": 0, "keep_alive_interval": args.keep_alive_days, "scrape_interval": args.scrape_days}
    if settings.CONFIG_STATE_PATH.exists() and settings.CONFIG_STATE_PATH.stat().st_size > 0:
        try:
            with open(settings.CONFIG_STATE_PATH, "r") as f:
                config_data = json.load(f)
        except Exception:
            pass

    # Override intervals if manual dashboard parameters are provided
    if args.mode != "scheduled":
        config_data["keep_alive_interval"] = args.keep_alive_days
        config_data["scrape_interval"] = args.scrape_days

    current_time = int(time.time())
    target_mode = args.mode

    # 3. Dynamic Filtering: Evaluate the Daily Smart Guard Loop Pattern
    if args.mode == "scheduled":
        logger.info("Daily Schedule Pulse Triggered. Evaluating interval timing thresholds...")
        
        seconds_since_scrape = current_time - config_data.get("last_scrape", 0)
        seconds_since_keep_alive = current_time - config_data.get("last_keep_alive", 0)
        
        scrape_threshold = config_data.get("scrape_interval", 14) * 86400
        keep_alive_threshold = config_data.get("keep_alive_interval", 3) * 86400

        if seconds_since_scrape >= scrape_threshold:
            logger.info(f"Threshold Met: {config_data.get('scrape_interval')} days passed since last data capture. Starting Full Scrape.")
            target_mode = "scrape"
        elif seconds_since_keep_alive >= keep_alive_threshold:
            logger.info(f"Threshold Met: {config_data.get('keep_alive_interval')} days passed since last token renewal. Starting Keep-Alive.")
            target_mode = "keep-alive"
        else:
            logger.info("Adaptive Guard Filter: Timing intervals not reached. Terminating runner context safely to save resources.")
            sys.exit(0)

    logger.info(f"Starting Apple Automation Workspace Loop in [Mode: {target_mode.upper()}]")

    try:
        with get_browser_context() as context:
            page = context.new_page()

            if target_mode == "scrape":
                headers = initialize_google_sheets()
                def stream_row_callback(record: dict) -> None:
                    if headers:
                        sync_row_to_google_sheets(record, headers)

                scrape_all_teams(page, dev_mode=args.dev, on_team_scraped=stream_row_callback)
                config_data["last_scrape"] = current_time
                config_data["last_keep_alive"] = current_time # Full scrape refreshes session cookies implicitly

            elif target_mode == "keep-alive":
                success = run_keep_alive(context)
                if success:
                    config_data["last_keep_alive"] = current_time
                else:
                    sys.exit(1)

        # 4. Save and synchronize configuration metrics to Google Drive upon run success
        with open(settings.CONFIG_STATE_PATH, "w") as f:
            json.dump(config_data, f, indent=2)
        upload_state_to_drive()
        logger.info("Automation run finished successfully. Cloud tracking telemetry updated.")

    except SessionExpiredError as e:
        logger.critical(f"FATAL AUTHENTICATION FAILURE: {e.message}")
        sys.exit(2)
    except GoogleSheetsSyncError as e:
        logger.error(f"INTEGRATION API FAILURE: {e.message}")
        sys.exit(3)
    except Exception as e:
        logger.critical(f"UNHANDLED SYSTEM ERROR: {str(e)}", exc_info=True)
        sys.exit(5)

if __name__ == "__main__":
    main()