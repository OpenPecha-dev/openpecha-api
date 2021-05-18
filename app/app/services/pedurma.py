import re
import shutil
import tempfile
from pathlib import Path
from typing import Dict

from github.GithubException import UnknownObjectException
from github.Repository import Repository as Repo
from openpecha.github_utils import get_github_repo

from app.core.config import settings


def zip_text(text_id: str, text_preview: Dict[str, str], tempdir: Path):
    text_dir = tempdir / text_id
    text_dir.mkdir(exist_ok=True, parents=True)
    text_fn = text_dir / f"{text_id}.txt"
    content_all = ""
    for _, content in text_preview.items():
        content_all += content
    text_fn.write_text(content_all)
    shutil.make_archive(text_dir, "zip", text_dir)
    return f"{text_dir}.zip"


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


def release_text_preview(text_id: str, text_preview: Dict[str, str]):
    repo = get_github_repo(settings.PEDURMA_PECHA, "OpenPecha", settings.GITHUB_TOKEN)
    with tempfile.TemporaryDirectory() as tempdir:
        zipped_text_fn = zip_text(text_id, text_preview, Path(tempdir))
        release = create_empty_release(repo, text_id)
        text_asset = release.upload_asset(str(zipped_text_fn))
        return text_asset.browser_download_url
