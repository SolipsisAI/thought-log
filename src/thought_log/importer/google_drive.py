from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive


def authenticate():
    # You need client_secrets.json
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()  # Creates local webserver and auto handles authentication.


def list_dirs(title: str = None):
    gauth = GoogleAuth()
    drive = GoogleDrive(gauth)
    dirs = drive.ListFile(
        {
            "q": "'root' in parents and trashed=false and mimeType = 'application/vnd.google-apps.folder'"
        }
    ).GetList()

    if not title:
        return dirs

    for d in dirs:
        if d["title"] == title:
            break

    folder_id = d["id"]
    results = drive.ListFile({"q": f"parents in '{folder_id}' and trashed = false"})

    return results.GetList()
