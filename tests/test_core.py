import unittest
from git_detox.core.models import GitCommit, RecoverableItem
from datetime import datetime

class TestModels(unittest.TestCase):
    def test_commit_model(self):
        commit = GitCommit(
            hash="abc1234",
            author="Test",
            email="test@example.com",
            timestamp=datetime.now(),
            subject="Test commit"
        )
        self.assertEqual(commit.hash, "abc1234")

    def test_recoverable_item(self):
        commit = GitCommit(
            hash="abc1234",
            author="Test",
            email="test@example.com",
            timestamp=datetime.now(),
            subject="Test commit"
        )
        item = RecoverableItem(
            id="test_1",
            type="deleted_branch",
            commit=commit,
            description="Test description"
        )
        self.assertEqual(item.type, "deleted_branch")
        self.assertEqual(item.risk_level, "low")

if __name__ == "__main__":
    unittest.main()
