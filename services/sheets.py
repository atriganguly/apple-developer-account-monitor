import logging
from typing import List, Dict, Any
from google.oauth2 import service_account
from googleapiclient.discovery import build

from config.settings import settings
from core.exceptions import GoogleSheetsSyncError

logger = logging.getLogger("apple_automation.services.sheets")

TARGET_FIELDS = [
    "Entity name",
    "Team ID",
    "Program",
    "Enrolled as",
    "Phone",
    "Street address",
    "Account Holder",
    "Your role",
    "Renewal date",
    "Annual fee",
    "Device reset date"
]

def initialize_google_sheets() -> List[str]:
    """
    Initializes the target spreadsheet matrix layout by writing structural 
    headers to Row 1 before data ingestion routines begin.

    Returns:
        List[str]: Uniform header sequence keys used for row vector alignment.
    """
    if not settings.GOOGLE_SHEET_ID:
        logger.error("Initialization failed: GOOGLE_SHEET_ID is not configured in settings.")
        return []

    headers = [
        "Scrape Index", 
        "Team Dropdown Name", 
        "Account Alerts / Warnings",
        "Entity name",
        "Team ID",
        "Program",
        "Enrolled as",
        "Phone",
        "Street address",
        "Account Holder",
        "Account Holder Email",
        "Your role",
        "Renewal date",
        "Annual fee",
        "Device reset date"
    ]

    try:
        logger.info(f"Authenticating with Google Sheets API via token: {settings.GOOGLE_CREDS_PATH}")
        credentials = service_account.Credentials.from_service_account_file(
            str(settings.GOOGLE_CREDS_PATH),
            scopes=["https://www.googleapis.com/auth/spreadsheets"]
        )
        
        service = build("sheets", "v4", credentials=credentials, cache_discovery=False)
        sheet_client = service.spreadsheets()

        base_sheet_name = settings.GOOGLE_SHEET_RANGE.split("!")[0]
        full_range = f"{base_sheet_name}!A1:Z1000"

        logger.info(f"Clearing historical sheet payload data inside: {full_range}")
        sheet_client.values().clear(
            spreadsheetId=settings.GOOGLE_SHEET_ID,
            range=full_range
        ).execute()

        logger.info(f"Writing structured header row into baseline workspace: {base_sheet_name}!A1")
        sheet_client.values().update(
            spreadsheetId=settings.GOOGLE_SHEET_ID,
            range=f"{base_sheet_name}!A1",
            valueInputOption="RAW",
            body={"values": [headers]}
        ).execute()

        return headers

    except Exception as e:
        error_msg = f"Failed to initialize master Google Sheets workspace headers: {str(e)}"
        logger.error(error_msg)
        raise GoogleSheetsSyncError(error_msg, context={"sheet_id": settings.GOOGLE_SHEET_ID})


def sync_row_to_google_sheets(record: Dict[str, Any], headers: List[str]) -> None:
    """
    Streams a single scraped team record object directly into its allocated row position 
    in real-time while scraping operations are running.
    Target row location is computed deterministically via: Scrape Index + 1.
    """
    if not settings.GOOGLE_SHEET_ID:
        return

    try:
        scrape_index = record.get("Scrape Index", 1)
        target_row = scrape_index + 1
        
        base_sheet_name = settings.GOOGLE_SHEET_RANGE.split("!")[0]
        target_range = f"{base_sheet_name}!A{target_row}"

        row_values = [str(record.get(header, "N/A")) for header in headers]

        credentials = service_account.Credentials.from_service_account_file(
            str(settings.GOOGLE_CREDS_PATH),
            scopes=["https://www.googleapis.com/auth/spreadsheets"]
        )
        
        service = build("sheets", "v4", credentials=credentials, cache_discovery=False)
        sheet_client = service.spreadsheets()

        logger.info(f"[Real-Time Sync] Streaming data matrix row {target_row} for team: '{record.get('Team Dropdown Name')}'")
        sheet_client.values().update(
            spreadsheetId=settings.GOOGLE_SHEET_ID,
            range=target_range,
            valueInputOption="RAW",
            body={"values": [row_values]}
        ).execute()

    except Exception as e:
        error_msg = f"Incremental real-time record synchronization pipeline failed: {str(e)}"
        logger.error(error_msg)
        raise GoogleSheetsSyncError(error_msg, context={"sheet_id": settings.GOOGLE_SHEET_ID, "record": record})