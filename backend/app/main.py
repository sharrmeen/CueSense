from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.models.project import Project
from app.api import uploads

@asynccontextmanager
async def lifespan(app: FastAPI):
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    await init_beanie(database=client.cuesens_db, document_models=[Project])
    
    print("Database connected and Beanie initialized")
    yield
    client.close()
    print("Database connection closed")

app = FastAPI(
    title="Cuesens Smart B-Roll Inserter",
    description="Automated B-Roll planning and insertion for UGC videos",
    version="1.0.0",
    lifespan=lifespan
)

#CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#include routers
app.include_router(uploads.router, prefix="/api/uploads", tags=["Uploads"])
# app.include_router(jobs.router, prefix="/api/jobs", tags=["Jobs"])

@app.get("/")
async def root():
    return {
        "message": "Cuesens API is running",
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)