import os
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session
from pydantic import BaseModel

from database import init_db, get_session
import crud, models

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    # Safely seed default user and MVP Board upon startup
    try:
        session = next(get_session())
        crud.create_default_user_and_board(session)
    except Exception as e:
        print(f"Error seeding database: {e}")
    yield

app = FastAPI(lifespan=lifespan)

# --- MODELS FOR API REQUESTS ---
class AddCardRequest(BaseModel):
    column_id: str
    title: str
    details: str
    order: int

class MoveCardRequest(BaseModel):
    new_column_id: str
    new_order: int

class RenameColumnRequest(BaseModel):
    name: str

# --- REST ENDPOINTS ---
@app.get("/api/hello")
def read_hello():
    return {"message": "hello world"}

@app.get("/api/health")
def read_health():
    return {"status": "ok"}

@app.get("/api/board", response_model=models.BoardRead)
def get_board(session: Session = Depends(get_session)):
    board = crud.get_board_for_user(session, "user")
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    return board

@app.put("/api/column/{column_id}", response_model=models.Column)
def rename_column(column_id: str, req: RenameColumnRequest, session: Session = Depends(get_session)):
    col = crud.rename_column(session, column_id, req.name)
    if not col:
        raise HTTPException(status_code=404, detail="Column not found")
    return col

@app.post("/api/card", response_model=models.Card)
def add_card(req: AddCardRequest, session: Session = Depends(get_session)):
    return crud.create_card(session, req.column_id, req.title, req.details, req.order)

@app.put("/api/card/{card_id}/move", response_model=models.Card)
def move_card(card_id: str, req: MoveCardRequest, session: Session = Depends(get_session)):
    card = crud.move_card(session, card_id, req.new_column_id, req.new_order)
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    return card

@app.delete("/api/card/{card_id}")
def delete_card(card_id: str, session: Session = Depends(get_session)):
    success = crud.delete_card(session, card_id)
    if not success:
        raise HTTPException(status_code=404, detail="Card not found")
    return {"status": "deleted"}

# --- FRONTEND ROUTING ---
BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend" / ".output" / "public"

if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
else:
    print(f"WARNING: Frontend static directory not found at {FRONTEND_DIR}")

@app.exception_handler(404)
async def spa_fallback(request: Request, exc):
    if request.url.path.startswith("/api/"):
        return JSONResponse(status_code=404, content={"detail": "API Route Not Found"})
    
    index_file = FRONTEND_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    
    return JSONResponse(status_code=404, content={"detail": "Frontend not compiled or found."})
