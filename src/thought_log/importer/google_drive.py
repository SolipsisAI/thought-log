from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

FOLDER_MIMETYPE = "application/vnd.google-apps.folder"


def authenticate():
    # You need client_secrets.json
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()  # Creates local webserver and auto handles authentication.


def list_contents(*, folder_id: str = "root", content_type: str = None):
    drive = GoogleDrive(GoogleAuth())

    return drive.ListFile(
        {"q": build_query(folder_id=folder_id, content_type=content_type)},
    ).GetList()


def build_query(
    *, folder_id: str = "root", content_type: str = None, trashed: str = "false"
):
    query_parts = [f"'{folder_id}' in parents", f"trashed={trashed}"]

    if content_type:
        cond = "=" if content_type == "dir" else "!="
        query_parts.append(f"mimeType {cond} '{FOLDER_MIMETYPE}'")

    return " and ".join(query_parts)
