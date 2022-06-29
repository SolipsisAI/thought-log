from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive


def authenticate():
    # You need client_secrets.json
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()  # Creates local webserver and auto handles authentication.


def list_dirs():
    drive = GoogleDrive(GoogleAuth())
    dirs = drive.ListFile(
        {
            "q": "'root' in parents and trashed=false and mimeType = 'application/vnd.google-apps.folder'"
        }
    ).GetList()
    return dirs
