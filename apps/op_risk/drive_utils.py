import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import re

def extract_folder_id(drive_url):
    """
    Extracts the folder ID from a Google Drive folder URL.
    Example: https://drive.google.com/drive/folders/1WEBGx335hqb3xPTF4Nb_jEeIO9oPwNhs?usp=sharing
    """
    match = re.search(r'/folders/([a-zA-Z0-9_-]+)', drive_url)
    if match:
        return match.group(1)
    return None

def upload_to_drive(local_file_path, drive_url):
    """
    Uploads a local file to the specified Google Drive folder URL.
    Returns the webViewLink of the uploaded file.
    Requires credentials.json in the project root.
    """
    folder_id = extract_folder_id(drive_url)
    if not folder_id:
        return None

    # Resolve credentials path
    # Assuming credentials.json is in the root directory (parent of apps)
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    creds_path = os.path.join(base_dir, 'credentials.json')

    if not os.path.exists(creds_path):
        print(f"No credentials.json found at {creds_path}")
        return None

    try:
        # Authenticate
        SCOPES = ['https://www.googleapis.com/auth/drive.file']
        creds = service_account.Credentials.from_service_account_file(
            creds_path, scopes=SCOPES)

        service = build('drive', 'v3', credentials=creds)

        file_name = os.path.basename(local_file_path)

        file_metadata = {
            'name': file_name,
            'parents': [folder_id]
        }

        # MediaFileUpload requires the actual path
        media = MediaFileUpload(local_file_path, resumable=True)

        # Upload the file
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webViewLink'
        ).execute()

        return file.get('webViewLink')

    except Exception as e:
        print(f"Error interacting with Google Drive API: {e}")
        return None
