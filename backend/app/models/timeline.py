from pydantic import BaseModel
from typing import List, Optional

class BrollInsertion(BaseModel):
    start_sec: float
    duration_sec: float
    broll_id: str
    confidence: float
    reason: str

class TimelinePlan(BaseModel):
    a_roll_id: str
    insertions: List[BrollInsertion]

class JobStatus(BaseModel):
    job_id: str
    status: str  # PENDING, PROCESSING, COMPLETED, FAILED
    result: Optional[TimelinePlan] = None