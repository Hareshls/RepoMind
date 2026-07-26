import os
import stat
import shutil
from git import Repo

def _remove_readonly(func, path, exc_info):
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except Exception:
        pass

class GitService:
    def clone_repository(self, repo_url: str, destination: str):
        repo_url = str(repo_url)
        destination = str(destination)
        if os.path.exists(destination):
            try:
                repo = Repo(destination)
                if repo.remotes.origin.url.rstrip(".git") == repo_url.rstrip(".git"):
                    return repo
            except Exception:
                pass
            try:
                shutil.rmtree(destination, onexc=_remove_readonly)
            except TypeError:
                shutil.rmtree(destination, onerror=_remove_readonly)
        return Repo.clone_from(repo_url, destination)

