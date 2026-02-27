import subprocess
from typing import List, Optional

class GitRunner:
    @staticmethod
    def run(args: List[str], cwd: Optional[str] = None) -> str:
        try:
            result = subprocess.run(
                ["git"] + args,
                capture_output=True,
                text=True,
                check=True,
                cwd=cwd
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            # For some git commands, non-zero exit is expected (e.g. git rev-parse)
            return e.stdout.strip() if e.stdout else ""
        except FileNotFoundError:
            raise RuntimeError("Git is not installed or not in PATH")

    @staticmethod
    def is_repo(path: str = ".") -> bool:
        try:
            subprocess.run(
                ["git", "rev-parse", "--is-inside-work-tree"],
                capture_output=True,
                cwd=path,
                check=True
            )
            return True
        except:
            return False
