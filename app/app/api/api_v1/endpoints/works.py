from typing import List

from fastapi import APIRouter, HTTPException
from git import Repo
from openpecha.storages import GithubStorage, commit_and_push, setup_auth_for_old_repo
from openpecha.work import Instance, Work

router = APIRouter()


@router.get("/{work_id}", response_model=Work)
def read_work(work_id: str):
    """Return OpenPecha work"""
    work = Work.from_id(work_id)
    return work


def commit(path, message):
    storage = GithubStorage()
    repo = Repo(path)
    repo = setup_auth_for_old_repo(repo)


@router.post("/", response_model=Work)
def create_work(work: Work):
    """Create OpenPecha Work"""
    work_fn = work.save_to_yaml(output_dir=None)
    git_commit(
        repo_path=work_fn.parent,
        message=f"Added {work_fn.name}",
        not_includes=[],
        branch="main",
    )
    return work


@router.put("/{work_id}")
def update_work(work_id: str, work: Work):
    """Update OpenPecha Work"""
    raise HTTPException(status_code=501, detail="Endpoint not functional yet")


@router.delete("/{work_id}")
def delete_work(work_id: str):
    """Delete OpenPecha Work"""
    raise HTTPException(status_code=501, detail="Endpoint not functional yet")


@router.get("/{work_id}/instances", response_model=List[Instance])
def get_all_instances(work_id: str):
    """Retrieve all instances of a Work"""
    work = Work.from_id(work_id)
    return work.instances


@router.get("/{work_id}/instances/{instance_id}", response_model=Instance)
def get_instance(work_id: str, instance_id: str):
    """Retrieve a specific instance of a Work"""
    work = Work.from_id(work_id)
    return work.instances[instance_id]


@router.post("/{work_id}/instances")
def create_instance(work_id: str, instance: Instance):
    """Create a new instance of a Work"""
    work = Work.from_id(work_id)
    work.add_instance(instance)


@router.put("/{work_id}/instances/{instance_id}")
def update_instance(work_id: str, instance_id: str, instance: Instance):
    """Update a specific instance of a Work"""
    raise HTTPException(status_code=501, detail="Endpoint not functional yet")


@router.delete("/{work_id}/instances/{instance_id}")
def delete_instance(work_id: str, instance_id: str):
    """Delete a specific instance of a Work"""
    work = Work.from_id(work_id)
    work.delete_instance(instance_id)
    work.save_to_yaml()
