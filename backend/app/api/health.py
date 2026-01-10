from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "lexi-api",
    }


@router.get("/ready")
async def readiness_check():
    # TODO: Check database connection
    # TODO: Check external service availability
    return {
        "status": "ready",
        "checks": {
            "database": "ok",
            "storage": "ok",
        },
    }
