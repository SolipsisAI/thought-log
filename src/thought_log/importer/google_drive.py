import click

from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

FOLDER_MIMETYPE = "application/vnd.google-apps.folder"


def authenticate():
    # You need client_secrets.json
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()  # Creates local webserver and auto handles authentication.


def init_drive():
    return GoogleDrive(GoogleAuth())


def walk(folder_id: str = "root", content_type: str = None, drive=None):
    # Start at the root
    contents = list_contents(folder_id=folder_id, drive=drive)
    contents.sort(key=lambda d: d["title"])
    for idx, directory in enumerate(contents):
        title = directory["title"]
        click.echo(f"{idx}: {title}")

    selected_idx = click.prompt("Select", type=int)
    selected_content = contents[selected_idx]

    if selected_content.get("mimeType") != FOLDER_MIMETYPE:
        print(selected_content["title"], "is a file")
        return

    walk(contents[selected_idx]["id"], drive=drive, content_type=content_type)


def list_contents(*, folder_id: str = "root", content_type: str = None, drive=None):
    if not drive:
        drive = init_drive()

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
