import base64
import os
import sys
from email.message import EmailMessage
import google.auth
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

from http.server import BaseHTTPRequestHandler, HTTPServer


sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from mediflow.settings import BASE_DIR
import urllib.parse

def authenticate(user_id):
    try:
        SCOPES = ['https://www.googleapis.com/auth/gmail.send', 'openid']
        google_credentials = None
        user_credentials_path = os.path.join(BASE_DIR, 'google_auth/user_credentials', f'{user_id}_credentials.json')
        mediflow_credentials_path = os.path.join(BASE_DIR, 'google_auth', 'mediflow_credentials.json')

        if os.path.exists(user_credentials_path):
            google_credentials = Credentials.from_authorized_user_file(user_credentials_path, SCOPES)

        if google_credentials is None:
            flow = InstalledAppFlow.from_client_secrets_file(mediflow_credentials_path, SCOPES)
            google_credentials = flow.run_local_server(port=8080)

        if google_credentials and google_credentials.expired and google_credentials.refresh_token:
                google_credentials.refresh(Request())

        if google_credentials:
            with open(user_credentials_path, 'w') as credentials:
                credentials.write(google_credentials.to_json())
        return {"status": "success", "credentials": google_credentials}
    except Exception as e:
        return {"status": "error", "message": str(e)} # Desarrollo
        #return {"status": "error", "message": "Error al autenticar"} # Producción

def send_email(user_id, recipient, subject, body, attachment_path = None):
    if recipient is None :
        return {"status": "error", "message": "Recipient email is required"}
    try:
        google_credentials = authenticate(user_id)

        if google_credentials["status"] == "error":
            return google_credentials

        google_credentials = google_credentials["credentials"]

        service = build('gmail', 'v1', credentials=google_credentials)
        message = EmailMessage()

        userinfo_service = build('oauth2', 'v2', credentials=google_credentials)
        user_info = userinfo_service.userinfo().get().execute()
        from_email = user_info.get('email')

        message.set_content(body)

        message['Subject'] = subject
        message['From'] = from_email
        message['To'] = recipient

        if attachment_path is not None:
            file_name = attachment_path.split("/")[-1]
            file_type = attachment_path.split("/")[-1].split(".")[1]

            if file_type != "pdf":
                return {"status": "error", "message": "Attachment must be a pdf file"}

            with open(attachment_path, "rb") as file:
                file_content = file.read()
                message.add_attachment(file_content, maintype="application", subtype="pdf", filename=file_name)

        encoded = base64.urlsafe_b64encode(message.as_bytes()).decode()
        message = {'raw': encoded}

        send_message = service.users().messages().send(userId='me', body=message).execute()
        return {"status": "success", "message_id": send_message["id"]}
    except Exception as e:
        return {"status": "error", "message": str(e)} # Desarrollo
        #return {"status": "error", "message":"Error al enviar el correo"}