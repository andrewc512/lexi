from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import interviews, ai, email, health
from app.core.config import settings

app = FastAPI(
    title="Lexi API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, tags=["health"])
app.include_router(interviews.router, prefix="/interviews", tags=["interviews"])
app.include_router(ai.router, prefix="/ai", tags=["ai"])
app.include_router(email.router, prefix="/email", tags=["email"])


@app.get("/")
async def root():
    return {"message": "Lexi API", "version": "0.1.0"}
