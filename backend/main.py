import os
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()

@app.get("/api/hello")
def read_hello():
    return {"message": "hello world"}

@app.get("/api/health")
def read_health():
    return {"status": "ok"}

# --- FRONTEND ROUTING ---
# Calculate the dynamic path to the compiled Nuxt output
BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend" / ".output" / "public"

# Serve backend first, but mount the static files gracefully
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
else:
    print(f"WARNING: Frontend static directory not found at {FRONTEND_DIR}")

# Smart 404 Handler for SPA Routing fallback
@app.exception_handler(404)
async def spa_fallback(request: Request, exc):
    # Let standard API 404s pass through normally
    if request.url.path.startswith("/api/"):
        return JSONResponse(status_code=404, content={"detail": "API Route Not Found"})
    
    # Catch everything else and feed it to the Nuxt Vue Router!
    index_file = FRONTEND_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    
    return JSONResponse(status_code=404, content={"detail": "Frontend not compiled or found."})
