import io
import logging
from pathlib import Path
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
    """Queries your secure Google Drive folder to download both auth.json and config.json."""
    if not settings.GOOGLE_DRIVE_FOLDER_ID:
        logger.warning("Google Drive Synchronization skipped: GOOGLE_DRIVE_FOLDER_ID not set.")
        return False

    success = True
    for filename, local_path in [("auth.json", settings.STORAGE_STATE_PATH), ("config.json", settings.CONFIG_STATE_PATH)]:
        try:
            drive = _get_drive_client()
            query = f"'{settings.GOOGLE_DRIVE_FOLDER_ID}' in parents and name='{filename}' and trashed=false"
            
            response = drive.files().list(q=query, fields="files(id, name)").execute()
            files = response.get("files", [])

            if not files:
                logger.warning(f"No existing '{filename}' file found in Google Drive. Sync skipped for this asset.")
                continue

            file_id = files[0]["id"]
            logger.info(f"Downloading {filename} from Google Drive (File ID: {file_id})...")
            
            request = drive.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            
            done = False
            while not done:
                status, done = downloader.next_chunk()
                
            local_path.parent.mkdir(parents=True, exist_ok=True)
            with open(local_path, "wb") as f:
                f.write(fh.getvalue())
                
            logger.info(f"Successfully synchronized cloud state cache to: {local_path}")
        except Exception as e:
            logger.error(f"Error downloading {filename} from Google Drive: {str(e)}")
            success = False
            
    return success


def upload_state_to_drive() -> bool:
    """Saves locally updated auth.json and config.json configurations back up to Google Drive."""
    if not settings.GOOGLE_DRIVE_FOLDER_ID:
        return False

    success = True
    for filename, local_path in [("auth.json", settings.STORAGE_STATE_PATH), ("config.json", settings.CONFIG_STATE_PATH)]:
        if not local_path.exists() or local_path.stat().st_size == 0:
            continue

        try:
            drive = _get_drive_client()
            query = f"'{settings.GOOGLE_DRIVE_FOLDER_ID}' in parents and name='{filename}' and trashed=false"
            
            response = drive.files().list(q=query, fields="files(id, name)").execute()
            files = response.get("files", [])

            media = MediaFileUpload(str(local_path), mimetype="application/json", resumable=True)

            if files:
                file_id = files[0]["id"]
                logger.info(f"Updating existing cloud '{filename}' entries in Google Drive (ID: {file_id})...")
                drive.files().update(fileId=file_id, media_body=media).execute()
            else:
                logger.info(f"Writing fresh '{filename}' parameters to Google Drive storage...")
                file_metadata = {
                    "name": filename,
                    "parents": [settings.GOOGLE_DRIVE_FOLDER_ID]
                }
                drive.files().create(body=file_metadata, media_body=media, fields="id").execute()
        except Exception as e:
            logger.error(f"Error uploading {filename} to Google Drive: {str(e)}")
            success = False
            
    return success