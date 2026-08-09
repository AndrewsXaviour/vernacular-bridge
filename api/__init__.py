"""API route layer — thin controllers for FastAPI endpoints.

Each module defines one or more FastAPI route handlers that parse
the request, call the corresponding service, and return the response.
No business logic lives here.

Routes:
    learn: POST /learn, POST /generate
    coach: POST /coach
    navigator: POST /navigator/explain
    full_flow: POST /full-flow
    retrieval: GET /entitlements, GET /processes
    health: GET /health
"""
