from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

class GitCommit(BaseModel):
    hash: str
    author: str
    email: str
    timestamp: datetime
    subject: str
    body: Optional[str] = ""

class RecoverableItem(BaseModel):
    id: str
    type: str  # 'deleted_branch', 'dangling_commit', 'dropped_stash'
    commit: GitCommit
    source_ref: Optional[str] = None
    discovery_date: datetime = Field(default_factory=datetime.now)
    risk_level: str = "low"  # low, medium, high
    description: str
