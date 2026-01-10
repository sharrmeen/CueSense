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
    description: Optional[str] = "No description available"
    keywords: List[str] = []
    mood: Optional[str] = "unknown"

class Project(Document):
    project_id: Indexed(str, unique=True) = Field(default_factory=lambda: str(uuid.uuid4().hex[:6]).upper())
    name:str
    status: str = "DRAFT"
    status_message: str = ""
    a_roll: Optional[ARoll] = None
    b_rolls: List[BRoll] = []
    edit_plan: List[dict] = []
    final_video_path:str=""
    
    class Settings:
        name = "projects" 