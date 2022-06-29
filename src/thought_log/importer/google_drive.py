from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive


def authenticate():
    # You need client_secrets.json
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()  # Creates local webserver and auto handles authentication.


def list_dirs(folder_name: str = None, subfolder_name: str = None):
    gauth = GoogleAuth()
    drive = GoogleDrive(gauth)

    folder_type = "mimeType = 'application/vnd.google-apps.folder'"
    file_type = "mimeType != 'application/vnd.google-apps.folder'"

    query = "'{folder_id}' in parents and trashed=false and {mimetype}"
    folders = drive.ListFile(
        {"q": query.format(folder_id="root", mimetype=folder_type)}
    ).GetList()

    if not folder_name:
        return folders

    for folder in folders:
        if folder["title"] == folder_name:
            break

    folder_id = folder["id"]
    subfolders = drive.ListFile(
        {"q": query.format(folder_id=folder_id, mimetype=folder_type)}
    ).GetList()

    if not subfolder_name:
        return subfolders

    for subfolder in subfolders:
        if subfolder["title"] == subfolder_name:
            break

    subfolder_id = subfolder["id"]
    return drive.ListFile(
        {"q": query.format(folder_id=subfolder_id, mimetype=file_type)}
    ).GetList()
