import click

from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from pydrive2.files import GoogleDriveFile

from thought_log.utils import make_datetime, generate_hash_from_string
from .filesystem import import_data, prepare_data

FOLDER_MIMETYPE = "application/vnd.google-apps.folder"


def authenticate():
    # You need client_secrets.json
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()  # Creates local webserver and auto handles authentication.


def import_from_file(selected_file: GoogleDriveFile):
    created_date = selected_file["createdDate"]
    text = selected_file.GetContentString()
    datetime_obj = make_datetime(created_date, fmt="isoformat")
    selected_file.FetchMetadata()
    data = {
        "text": text,
        "date": datetime_obj,
    }
    _hash = generate_hash_from_string(text)
    data = prepare_data(data, _hash)
    return import_data(data)


def init_drive():
    return GoogleDrive(GoogleAuth())


def walk(
    folder_id: str = "root", content_type: str = None, drive=None, process_fn=None
):
    # Start at the root
    contents = list_contents(folder_id=folder_id, drive=drive)
    contents.sort(key=lambda d: d["title"])
    for idx, directory in enumerate(contents):
        title = directory["title"]
        click.echo(f"{idx}: {title}")

    selected_idx = click.prompt("Select", type=int)
    selected_content = contents[selected_idx]

    if selected_content.get("mimeType") != FOLDER_MIMETYPE:
        return process_fn(selected_content) if process_fn else None

    walk(
        contents[selected_idx]["id"],
        drive=drive,
        content_type=content_type,
        process_fn=process_fn,
    )


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
