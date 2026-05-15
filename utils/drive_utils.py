import google.auth
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os

def get_drive_service():
    """
    Authenticates using Streamlit Secrets (Cloud) or Google Application Default Credentials (Local).
    """
    import streamlit as st
    from google.oauth2 import service_account

    # 1. Try Streamlit Secrets (for Cloud Deployment)
    # 1. Try Streamlit Secrets (for Cloud Deployment)
    try:
        if "gcp_service_account" in st.secrets:
            # Create credentials from the secrets dictionary
            service_account_info = st.secrets["gcp_service_account"]
            creds = service_account.Credentials.from_service_account_info(
                service_account_info,
                scopes=['https://www.googleapis.com/auth/drive.readonly']
            )
            service = build('drive', 'v3', credentials=creds)
            return service
    except (FileNotFoundError, Exception): 
        # StreamlitSecretNotFoundError inherits from FileNotFoundError in some versions or is a custom error.
        # Catching generic Exception here is safer for the local fallback to work reliably.
        pass

    # 2. Fallback to Local Environment (Environment Variable / JSON file)
    # Changed scope to readonly to search for existing files
    creds, _ = google.auth.default(scopes=['https://www.googleapis.com/auth/drive.readonly'])
    service = build('drive', 'v3', credentials=creds)
    return service

def search_file(file_name):
    """
    Searches for a file by name in Google Drive (exact match).
    Returns the webViewLink of the first match, or None if not found.
    """
    service = get_drive_service()
    
    # Escape single quotes in file name for the query
    escaped_name = file_name.replace("'", "\\'")
    
    query = f"name = '{escaped_name}' and trashed = false"
    
    results = service.files().list(
        q=query,
        pageSize=1,
        fields="files(id, name, webViewLink)"
    ).execute()
    
    files = results.get('files', [])
    
    if not files:
        return None
        
    return files[0].get('webViewLink')

def upload_file_to_drive(file_path):
    """
    Uploads a file to Google Drive and makes it viewable by anyone.
    Returns the file ID and WebViewLink.
    """
    service = get_drive_service()
    file_name = os.path.basename(file_path)
    
    file_metadata = {'name': file_name}
    media = MediaFileUpload(file_path, mimetype='application/pdf', resumable=True)
    
    print(f"Uploading {file_name} to Drive...")
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id, webViewLink'
    ).execute()
    
    file_id = file.get('id')
    web_view_link = file.get('webViewLink')
    
    # Set Permission: Anyone Reader
    permission = {
        'type': 'anyone',
        'role': 'reader',
    }
    service.permissions().create(
        fileId=file_id,
        body=permission,
    ).execute()
    
    return file_id, web_view_link
