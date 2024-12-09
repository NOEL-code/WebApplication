import pathlib
from flask import current_app

def photo_filename(photo):
    path = (
        pathlib.Path(current_app.root_path)
        / "static"
        / "photos"
        / f"photo-{photo.id}.{photo.file_extension}"
    )
    return path