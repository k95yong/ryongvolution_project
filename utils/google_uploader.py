from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
import os

def upload_to_drive(file_path, folder_id, credentials):
    # 구글 인증
    SCOPES = ['https://www.googleapis.com/auth/drive.file']

    flow = InstalledAppFlow.from_client_secrets_file('google_credentials.json', SCOPES)
    creds = flow.run_local_server(port=0)

    service = build('drive', 'v3', credentials=creds)

    # 업로드할 파일 설정
    file_metadata = {
        'name': os.path.basename(file_path),
        'parents': [folder_id]  # 업로드할 폴더 ID
    }
    media = MediaFileUpload(file_path, mimetype='application/pdf')

    # 파일 업로드
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

    print(f"업로드 완료! 파일 ID: {file.get('id')}")
