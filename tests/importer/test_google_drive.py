from thought_log.importer import google_drive

FOLDER_MIMETYPE = "application/vnd.google-apps.folder"


def test_query():
    assert (
        google_drive.build_query(folder_id="1234")
        == "'1234' in parents and trashed=false"
    )

    assert (
        google_drive.build_query(folder_id="1234", content_type="dir")
        == f"'1234' in parents and trashed=false and mimeType = '{FOLDER_MIMETYPE}'"
    )

    assert (
        google_drive.build_query(folder_id="1234", content_type="file")
        == f"'1234' in parents and trashed=false and mimeType != '{FOLDER_MIMETYPE}'"
    )
