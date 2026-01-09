from typing import List, Optional
from beanie import Document, Indexed
from pydantic import BaseModel, Field
import uuid


class ARoll(BaseModel):
    file_id: str
    path: str
    duration:float
    transcript: Optional[List[dict]] = None 

class BRoll(BaseModel):
    broll_id: str
    path: str
    duration: float
    description: Optional[str] = None 

class Project(Document):
    project_id: Indexed(str, unique=True) = Field(default_factory=lambda: str(uuid.uuid4().hex[:6]).upper())
    name:str
    status: str = "DRAFT"  # DRAFT, TRANSCRIBING, ANALYZING, COMPLETED
    a_roll: Optional[ARoll] = None
    b_rolls: List[BRoll] = []
    final_plan: Optional[dict] = None

    class Settings:
        name = "projects" 