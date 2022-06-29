from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

QUERY = "'{folder_id}' in parents and trashed=false"
FOLDER_MIMETYPE = "application/vnd.google-apps.folder"


def authenticate():
    # You need client_secrets.json
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()  # Creates local webserver and auto handles authentication.


def list_contents(*, folder_id: str = "root", content_type: str = None):
    drive = GoogleDrive(GoogleAuth())

    cond = "!=" if content_type == "file" else "="
    mimetype = f"and mimetype {cond} {FOLDER_MIMETYPE}" if content_type else ""

    return drive.ListFile(
        {"q": QUERY.format(folder_id=folder_id, mimetype=mimetype)},
    ).GetList()


def build_query(
    *, folder_id: str = "root", content_type: str = None, trashed: str = "false"
):
    query_parts = [f"'{folder_id}' in parents", f"trashed={trashed}"]

    if content_type:
        cond = "=" if content_type == "dir" else "!="
        query_parts.append(f"mimetype {cond} '{FOLDER_MIMETYPE}'")

    return " and ".join(query_parts)
