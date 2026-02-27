import re
from datetime import datetime
from typing import List, Optional
from git_detox.utils.git_runner import GitRunner
from git_detox.core.models import GitCommit, RecoverableItem

class Scanner:
    def __init__(self):
        self.git = GitRunner()

    def get_commit_details(self, commit_hash: str) -> Optional[GitCommit]:
        # Format: hash|author|email|timestamp|subject|body
        fmt = "%H|%an|%ae|%at|%s|%b"
        output = self.git.run(["show", "-s", f"--format={fmt}", commit_hash])
        if not output:
            return None
            
        parts = output.split("|", 5)
        if len(parts) < 5:
            return None
        
        try:
            return GitCommit(
                hash=parts[0],
                author=parts[1],
                email=parts[2],
                timestamp=datetime.fromtimestamp(int(parts[3])),
                subject=parts[4],
                body=parts[5] if len(parts) > 5 else ""
            )
        except (ValueError, IndexError):
            return None

    def scan_deleted_branches(self) -> List[RecoverableItem]:
        items = []
        # Look for branch deletions in reflog
        reflog = self.git.run(["reflog", "--date=iso"])
        
        # Pattern 1: HEAD@{<date>}: branch: Deleted branch <name> (was <hash>)
        pattern1 = r"HEAD@\{(.+)\}: branch: Deleted branch (.+) \(was ([0-9a-f]+)\)"
        # Pattern 2: <hash> HEAD@{<date>}: branch: Deleted <name>
        pattern2 = r"([0-9a-f]+) HEAD@\{(.+)\}: branch: Deleted (.+)"
        
        seen_hashes = set()

        for line in reflog.splitlines():
            # Try Pattern 1 first (more specific)
            match1 = re.search(pattern1, line)
            if match1:
                date_str, branch_name, commit_hash = match1.groups()
                if commit_hash not in seen_hashes:
                    exists = self.git.run(["rev-parse", "--verify", branch_name])
                    if not exists:
                        commit = self.get_commit_details(commit_hash)
                        if commit:
                            items.append(RecoverableItem(
                                id=f"del_{commit_hash[:7]}",
                                type="deleted_branch",
                                commit=commit,
                                source_ref=branch_name,
                                description=f"Deleted branch: {branch_name}"
                            ))
                            seen_hashes.add(commit_hash)
                continue

            # Try Pattern 2
            match2 = re.search(pattern2, line)
            if match2:
                commit_hash, date_str, branch_name = match2.groups()
                if commit_hash not in seen_hashes:
                    exists = self.git.run(["rev-parse", "--verify", branch_name])
                    if not exists:
                        commit = self.get_commit_details(commit_hash)
                        if commit:
                            items.append(RecoverableItem(
                                id=f"del_{commit_hash[:7]}",
                                type="deleted_branch",
                                commit=commit,
                                source_ref=branch_name,
                                description=f"Deleted branch: {branch_name}"
                            ))
                            seen_hashes.add(commit_hash)
        return items

    def scan_dangling_commits(self) -> List[RecoverableItem]:
        items = []
        fsck_output = self.git.run(["fsck", "--lost-found"])
        for line in fsck_output.splitlines():
            if line.startswith("dangling commit"):
                commit_hash = line.split()[-1]
                commit = self.get_commit_details(commit_hash)
                if commit:
                    items.append(RecoverableItem(
                        id=f"dan_{commit_hash[:7]}",
                        type="dangling_commit",
                        commit=commit,
                        description="Dangling commit (not reachable from any branch)"
                    ))
        return items

    def scan_dropped_stashes(self) -> List[RecoverableItem]:
        items = []
        fsck_output = self.git.run(["fsck", "--lost-found"])
        for line in fsck_output.splitlines():
            if line.startswith("dangling commit"):
                commit_hash = line.split()[-1]
                # Stashes are usually merge commits with 2 or 3 parents
                parents = self.git.run(["rev-list", "--parents", "-n", "1", commit_hash]).split()
                # parents[0] is the commit itself, parents[1:] are parents
                if len(parents) >= 3: # At least 2 parents
                    show_output = self.git.run(["show", "-s", "--format=%s", commit_hash])
                    if show_output.startswith("WIP on ") or show_output.startswith("index on "):
                        commit = self.get_commit_details(commit_hash)
                        if commit:
                            items.append(RecoverableItem(
                                id=f"sta_{commit_hash[:7]}",
                                type="dropped_stash",
                                commit=commit,
                                description="Dropped stash (WIP commit)"
                            ))
        return items

    def calculate_risk(self, item: RecoverableItem):
        days_old = (datetime.now() - item.commit.timestamp).days
        if item.type in ["dangling_commit", "dropped_stash"]:
            if days_old > 14:
                item.risk_level = "high"
            elif days_old > 7:
                item.risk_level = "medium"
        return item

    def scan_all(self) -> List[RecoverableItem]:
        all_items = self.scan_deleted_branches() + self.scan_dangling_commits() + self.scan_dropped_stashes()
        seen_hashes = set()
        unique_items = []
        for item in all_items:
            if item.commit.hash not in seen_hashes:
                seen_hashes.add(item.commit.hash)
                unique_items.append(self.calculate_risk(item))
        return unique_items
