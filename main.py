import sys
import argparse
import logging
from config.settings import settings
from core.browser import get_browser_context
from core.exceptions import SessionExpiredError, GoogleSheetsSyncError, AppleAutomationError
from services.scraper import scrape_all_teams
from services.keep_alive import run_keep_alive
from services.sheets import initialize_google_sheets, sync_row_to_google_sheets

# Configure production-ready unified logging pipeline
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("apple_automation.main")


def parse_arguments() -> argparse.Namespace:
    """
    Parses CLI runtime input control vectors to alter execution frameworks dynamically.
    """
    parser = argparse.ArgumentParser(
        description="Bulletproof Apple Developer Portal Multi-Team Scraping & Session Automation Engine."
    )
    parser.add_argument(
        "--mode",
        type=str,
        required=True,
        choices=["scrape", "keep-alive"],
        help="Specify 'scrape' for multi-team data collection, or 'keep-alive' to execute cookie sliding renewals."
    )
    parser.add_argument(
        "--headed",
        action="store_true",
        default=False,
        help="If flagged, forces the browser to run visibly for testing, localization setups, or interactive demos."
    )
    parser.add_argument(
        "--dev",
        action="store_true",
        default=False,
        help="If enabled, boots in development throttling mode, processing only the first 5 discovered team workspaces."
    )
    return parser.parse_args()


def main() -> None:
    """
    Master orchestrator managing lifecycle routines, pipeline injections, and exception boundaries.
    """
    args = parse_arguments()

    # Runtime configuration injection via argument overrides
    if args.headed:
        logger.info("CLI Override: Forcing browser execution environment into HEADED visual display mode.")
        # Modify the environment configuration cleanly at instantiation runtime boundaries
        object.__setattr__(settings, "HEADLESS", False)

    logger.info(f"Starting Apple Automation Core Engine Workspace in [Mode: {args.mode.upper()}]")

    try:
        # Initialize managed browser stack lifecycle context
        with get_browser_context() as context:
            # Provision primary operational sheet layer page pointer
            page = context.new_page()

            if args.mode == "scrape":
                logger.info("Executing comprehensive team data capture matrix pipeline...")
                
                # Real-Time Synchronous Sheets Pipeline Integration
                logger.info("Initializing Google Sheets layout schema configuration and header allocations...")
                headers = initialize_google_sheets()

                # Construct row real-time streaming pipeline writer callback
                def stream_row_callback(record: dict) -> None:
                    if headers:
                        sync_row_to_google_sheets(record, headers)

                scraped_data = scrape_all_teams(
                    page, 
                    dev_mode=args.dev, 
                    on_team_scraped=stream_row_callback
                )
                
                logger.info(f"Scrape loop concluded. Extracted records count: {len(scraped_data)}")
                logger.info("Data scraping and real-time sheet storage synchronization completed successfully.")

            elif args.mode == "keep-alive":
                logger.info("Initiating lightweight verification pulse operation...")
                success = run_keep_alive(context)
                if success:
                    logger.info("Keep-alive infrastructure run executed successfully.")
                else:
                    logger.error("Keep-alive processing script completed with underlying internal validation warnings.")
                    sys.exit(1)

    except SessionExpiredError as e:
        logger.critical(f"FATAL AUTHENTICATION FAILURE: {e.message}")
        logger.critical("ACTION REQUIRED: Run a local headed environment instance to perform interactive 2FA verification updates.")
        sys.exit(2)

    except GoogleSheetsSyncError as e:
        logger.error(f"INTEGRATION API FAILURE: {e.message}")
        logger.error("SCROLLBACK SAFE STATE: Scraped execution state records were successfully handled locally but dropped at sheets upload.")
        sys.exit(3)

    except AppleAutomationError as e:
        logger.error(f"DOMAIN RUNTIME EXCEPTION HANDLED CLEANLY: {e.message} - Context: {e.context}")
        sys.exit(4)

    except Exception as e:
        logger.critical(f"UNHANDLED SYSTEM ERROR: {str(e)}", exc_info=True)
        sys.exit(5)


if __name__ == "__main__":
    main()