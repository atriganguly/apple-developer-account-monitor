import io
import logging
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

from config.settings import settings

logger = logging.getLogger("apple_automation.services.drive_sync")

def _get_drive_client():
    """Initializes and returns an authenticated Google Drive V3 API Service Client."""
    credentials = service_account.Credentials.from_service_account_file(
        str(settings.GOOGLE_CREDS_PATH),
        scopes=["https://www.googleapis.com/auth/drive"]
    )
    return build("drive", "v3", credentials=credentials, cache_discovery=False)


def download_state_from_drive() -> bool:
    """
    Queries your secure Google Drive shared folder for a stored 'auth.json' file.
    If located, downloads and overwrites the local tracking cache path.
    """
    if not settings.GOOGLE_DRIVE_FOLDER_ID:
        logger.warning("Google Drive Synchronization skipped: GOOGLE_DRIVE_FOLDER_ID not set.")
        return False

    try:
        drive = _get_drive_client()
        query = f"'{settings.GOOGLE_DRIVE_FOLDER_ID}' in parents and name='auth.json' and trashed=false"
        
        response = drive.files().list(q=query, fields="files(id, name)").execute()
        files = response.get("files", [])

        if not files:
            logger.warning("No existing 'auth.json' file found in Google Drive folder container. Initial download skipped.")
            return False

        file_id = files[0]["id"]
        logger.info(f"Downloading state file from Google Drive (File ID: {file_id})...")
        
        request = drive.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        
        done = False
        while not done:
            status, done = downloader.next_chunk()
            
        # Ensure local folder context structures exist before writing disk blocks
        settings.STORAGE_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(settings.STORAGE_STATE_PATH, "wb") as f:
            f.write(fh.getvalue())
            
        logger.info(f"Successfully synchronized cloud state cache to: {settings.STORAGE_STATE_PATH}")
        return True

    except Exception as e:
        logger.error(f"Error downloading session cookie array from Google Drive: {str(e)}")
        return False


def upload_state_to_drive() -> bool:
    """
    Saves the locally updated 'auth.json' tracking configuration array up to the cloud.
    Performs an in-place update if the file already exists, or constructs a fresh one if missing.
    """
    if not settings.GOOGLE_DRIVE_FOLDER_ID:
        return False

    if not settings.STORAGE_STATE_PATH.exists() or settings.STORAGE_STATE_PATH.stat().st_size == 0:
        logger.error("Upload aborted: Local state tracking file is missing or contains empty definitions.")
        return False

    try:
        drive = _get_drive_client()
        query = f"'{settings.GOOGLE_DRIVE_FOLDER_ID}' in parents and name='auth.json' and trashed=false"
        
        response = drive.files().list(q=query, fields="files(id, name)").execute()
        files = response.get("files", [])

        media = MediaFileUpload(str(settings.STORAGE_STATE_PATH), mimetype="application/json", resumable=True)

        if files:
            # Overwrite the existing cloud file entry
            file_id = files[0]["id"]
            logger.info(f"Updating existing cloud state file entries in Google Drive (ID: {file_id})...")
            drive.files().update(fileId=file_id, media_body=media).execute()
        else:
            # Create a completely fresh cloud file entry inside your target folder
            logger.info("Writing fresh session authentication parameters to Google Drive storage...")
            file_metadata = {
                "name": "auth.json",
                "parents": [settings.GOOGLE_DRIVE_FOLDER_ID]
            }
            drive.files().create(body=file_metadata, media_body=media, fields="id").execute()

        logger.info("Cloud synchronization file uploads completed successfully.")
        return True

    except Exception as e:
        logger.error(f"Error uploading cookie definitions to Google Drive: {str(e)}")
        return False