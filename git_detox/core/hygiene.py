from typing import List, Dict
from git_detox.utils.git_runner import GitRunner

class HygieneAnalyzer:
    def __init__(self):
        self.git = GitRunner()

    def get_merged_branches(self) -> List[str]:
        # Branches merged into current HEAD
        output = self.git.run(["branch", "--merged"])
        branches = []
        for line in output.splitlines():
            branch = line.strip().replace("* ", "")
            if branch not in ["main", "master", "develop"]:
                branches.append(branch)
        return branches

    def get_stale_branches(self, days: int = 30) -> List[Dict]:
        # Branches with no commits in X days
        fmt = "%(refname:short)|%(committerdate:unix)|%(subject)"
        output = self.git.run(["for-each-ref", "--sort=-committerdate", f"--format={fmt}", "refs/heads/"])
        import time
        now = time.time()
        stale = []
        for line in output.splitlines():
            name, ts, subject = line.split("|")
            age_days = (now - int(ts)) / 86400
            if age_days > days and name not in ["main", "master", "develop"]:
                stale.append({"name": name, "age": int(age_days), "subject": subject})
        return stale

    def get_health_score(self) -> Dict:
        merged = self.get_merged_branches()
        stale = self.get_stale_branches()
        
        score = 100
        score -= len(merged) * 5
        score -= len(stale) * 2
        
        return {
            "score": max(0, score),
            "merged_count": len(merged),
            "stale_count": len(stale),
            "recommendations": [
                f"Delete {len(merged)} merged branches" if merged else None,
                f"Review {len(stale)} stale branches" if stale else None
            ]
        }
