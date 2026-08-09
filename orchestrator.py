"""Vernacular Bridge — FastAPI application entry point.

This module is intentionally thin (<100 lines). All business logic
lives in the services/, core/, parsers/, api/, and models/ packages.

Application lifecycle:
    1. Create FastAPI app with CORS middleware.
    2. Mount all route modules from api/.
    3. On startup, data is lazy-loaded by services/retrieval_service.
"""

import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from core.config import settings
from core.audit import AuditMiddleware

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(name)s %(levelname)s %(message)s',
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------
load_dotenv()

api_key = settings.google_api_key
print(
    f"DEBUG_API_KEY: {'Loaded' if api_key else 'None'} | "
    f"Length: {len(api_key) if api_key else 0}"
)

# ---------------------------------------------------------------------------
# FastAPI App
# ---------------------------------------------------------------------------
app = FastAPI()

ALLOWED_ORIGINS = settings.allowed_origins.split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(AuditMiddleware)

# ---------------------------------------------------------------------------
# Mount Route Modules
# ---------------------------------------------------------------------------
from api.learn import router as learn_router
from api.coach import router as coach_router
from api.navigator import router as navigator_router
from api.full_flow import router as full_flow_router
from api.retrieval import router as retrieval_router
from api.health import router as health_router

app.include_router(learn_router)
app.include_router(coach_router)
app.include_router(navigator_router)
app.include_router(full_flow_router)
app.include_router(retrieval_router)
app.include_router(health_router)

# ---------------------------------------------------------------------------
# Development Server
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
