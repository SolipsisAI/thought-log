from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive


def authenticate():
    # You need client_secrets.json
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()  # Creates local webserver and auto handles authentication.


def list_dirs(folder_name: str = None, subfolder_name: str = None):
    gauth = GoogleAuth()
    drive = GoogleDrive(gauth)
    folders = drive.ListFile(
        {
            "q": "'root' in parents and trashed=false and mimeType = 'application/vnd.google-apps.folder'"
        }
    ).GetList()

    if not folder_name:
        return folders

    for folder in folders:
        if folder["title"] == folder_name:
            break

    folder_id = folder["id"]
    subfolders = drive.ListFile(
        {"q": f"parents in '{folder_id}' and trashed = false"}
    ).GetList()

    if not subfolder_name:
        return subfolders

    for subfolder in subfolders:
        if subfolder["title"] == subfolder_name:
            break

    subfolder_id = subfolder["id"]
    return drive.ListFile({"q": f"'{subfolder_id}' in parents"}).GetList()
