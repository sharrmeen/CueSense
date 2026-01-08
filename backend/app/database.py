from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.models.project import Project

async def init_db():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    await init_beanie(database=client.cuesens_db, document_models=[Project])