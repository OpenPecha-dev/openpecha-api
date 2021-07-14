import re
import shutil
import tempfile
from pathlib import Path
from typing import Dict

from github.GithubException import UnknownObjectException
from github.Repository import Repository as Repo
from openpecha.github_utils import get_github_repo
from pedurma.reconstruction import get_docx_text, get_preview_text

from app.core.config import settings


def save_preview(text_id: str, text_preview: Dict[str, str], path: Path):
    text_fn = path / f"{text_id}.txt"
    content_all = ""
    for _, content in text_preview.items():
        content_all += content
    text_fn.write_text(content_all)
    return text_fn


def create_zip_file(path: Path):
    shutil.make_archive(path, "zip", path)
    return f"{str(path)}.zip"


def create_empty_release(repo: Repo, text_id: str):
    try:
        release = repo.get_release(text_id)
    except UnknownObjectException:
        pass
    else:
        release.delete_release()
    finally:
        release = repo.create_git_release(text_id, text_id, f"{text_id} release")
    return release


def make_text_dir(text_id: str, path: Path):
    text_dir = Path(path) / text_id
    text_dir.mkdir(exist_ok=True, parents=True)
    return text_dir


def create_text_release(text_id: str):
    repo = get_github_repo(settings.PEDURMA_PECHA, "OpenPecha", settings.GITHUB_TOKEN)
    with tempfile.TemporaryDirectory() as tempdir:
        text_dir = make_text_dir(text_id, tempdir)

        text_preview = get_preview_text(text_id)
        save_preview(text_id, text_preview, path=text_dir)
        get_docx_text(text_id, output_path=text_dir)

        zipped_text_fn = create_zip_file(path=text_dir)
        release = create_empty_release(repo, text_id)
        text_asset = release.upload_asset(str(zipped_text_fn))
        return text_asset.browser_download_url
