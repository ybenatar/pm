import os
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session
from pydantic import BaseModel

from database import init_db, get_session
import crud, models, ai
import json
import logging

# Set up error logging for AI hallucinations
error_logger = logging.getLogger("ai_errors")
error_logger.setLevel(logging.ERROR)
fh = logging.FileHandler("error.log")
fh.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
error_logger.addHandler(fh)

# In-memory history (Server-side)
CHAT_HISTORY = [] # List of {"role": "user/assistant", "content": "..."}

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

class AIChatRequest(BaseModel):
    message: str

# --- REST ENDPOINTS ---
@app.get("/api/hello")
def read_hello():
    return {"message": "hello world"}

@app.get("/api/health")
def read_health():
    return {"status": "ok"}

@app.get("/api/ai/test")
def test_ai():
    client = ai.get_client()
    response = client.chat.completions.create(
        model=ai.MODEL,
        messages=[{"role": "user", "content": "What is 2+2? Reply with just the number."}],
    )
    answer = response.choices[0].message.content
    return {"model": ai.MODEL, "answer": answer}

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

def clean_ai_response(raw: str) -> str:
    """Extracts and repairs JSON from markdown fences or noise."""
    import re
    # 1. Handle common markdown code block
    if "```json" in raw:
        raw = raw.split("```json")[1].split("```")[0]
    elif "```" in raw:
        raw = raw.split("```")[1].split("```")[0]
        
    # 2. Try to find the first { and last }
    start = raw.find("{")
    end = raw.rfind("}")
    if start != -1 and end != -1:
        raw = raw[start:end+1]
        
    # 3. Aggressive "Repair" for common AI mistakes
    # Remove trailing commas before closing braces/brackets
    raw = re.sub(r',\s*([\]}])', r'\1', raw)
    # Ensure keys are double-quoted if they aren't (basic)
    # raw = re.sub(r'(?<!")(\b\w+\b)(?=\s*:)', r'"\1"', raw) # Risky, but good for some models
    
    return raw.strip()

@app.post("/api/ai/chat", response_model=models.AIChatResponse)
async def ai_chat(req: AIChatRequest, session: Session = Depends(get_session)):
    global CHAT_HISTORY
    
    # 1. Get current board state
    board = crud.get_board_for_user(session, "user")
    if not board:
        raise HTTPException(status_code=404, detail="No board found for AI context")
    
    # 2. Build system prompt
    system_prompt = ai.get_system_prompt(board)
    
    # 3. Manage History
    limit = ai.get_history_limit()
    if len(CHAT_HISTORY) > limit * 2: # roles: user + assistant
        CHAT_HISTORY = CHAT_HISTORY[-(limit * 2):]
        
    messages = [{"role": "system", "content": system_prompt}] + CHAT_HISTORY + [{"role": "user", "content": req.message}]
    
    # 4. Call AI
    try:
        client = ai.get_client()
        response = client.chat.completions.create(
            model=ai.MODEL,
            messages=messages,
            response_format={ "type": "json_object" }
        )
        raw_content = response.choices[0].message.content or ""
        
        # 4b. Clean Response (Models like gpt-oss-120b sometimes fail strict JSON mode)
        cleaned_content = clean_ai_response(raw_content)
        
        try:
            ai_data = json.loads(cleaned_content)
        except json.JSONDecodeError:
            # Fallback for malformed JSON
            error_logger.error(f"Malformed JSON from AI (Cleaned): {cleaned_content} | Raw: {raw_content}")
            return models.AIChatResponse(
                text="I had trouble formatting the response correctly. Try being more specific.",
                actions=[],
                board=board
            )
        
    except Exception as e:
        error_msg = f"AI call failed: {str(e)}"
        error_logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)
    
    # 5. Process Actions & Handle Hallucinations
    actions = ai_data.get("actions", [])
    valid_actions_applied = []
    id_mapping_notes = [] # To feed back to history
    
    for act_data in actions:
        action_type = act_data.get("action")
        try:
            if action_type == "create":
                new_card = crud.create_card(session, act_data["column_id"], act_data["title"], act_data.get("details", ""), act_data.get("order", 0))
                valid_actions_applied.append(act_data)
                id_mapping_notes.append(f"Card '{act_data['title']}' created with ID: {new_card.id}")
            elif action_type == "move":
                # Validate card existence
                card = session.get(models.Card, act_data["card_id"])
                if not card:
                    raise Exception(f"Card ID {act_data['card_id']} does not exist.")
                crud.move_card(session, act_data["card_id"], act_data["column_id"], act_data.get("order", 0))
                valid_actions_applied.append(act_data)
            elif action_type == "edit":
                # Validate card existence
                card = session.get(models.Card, act_data["card_id"])
                if not card:
                    raise Exception(f"Card ID {act_data['card_id']} does not exist.")
                crud.update_card(
                    session, 
                    act_data["card_id"], 
                    title=act_data.get("title"), 
                    details=act_data.get("details"),
                    column_id=act_data.get("column_id"),
                    order=act_data.get("order")
                )
                valid_actions_applied.append(act_data)
            elif action_type == "delete":
                # Validate card existence
                card = session.get(models.Card, act_data["card_id"])
                if not card:
                    raise Exception(f"Card ID {act_data['card_id']} does not exist.")
                crud.delete_card(session, act_data["card_id"])
                valid_actions_applied.append(act_data)
        except Exception as e:
            # Log hallucination/error
            log_entry = {
                "error": str(e),
                "action_attempted": act_data,
                "ai_full_response": raw_content
            }
            error_logger.error(json.dumps(log_entry))
            
    # Add to history (including ID mappings for 'memory')
    assistant_memory = raw_content
    if id_mapping_notes:
        assistant_memory += f"\n\n[SYSTEM NOTE: {'; '.join(id_mapping_notes)}]"
        
    CHAT_HISTORY.append({"role": "user", "content": req.message})
    CHAT_HISTORY.append({"role": "assistant", "content": assistant_memory})
            
    # 6. Return response + fresh board state
    # Robust re-fetch with deep refresh
    session.expire_all()
    refreshed_board = crud.get_board_for_user(session, "user")
    
    # Debug trace
    cols_count = len(refreshed_board.columns) if refreshed_board else 0
    print(f"AI Success. Returning refreshed board with {cols_count} columns.")

    return models.AIChatResponse(
        text=ai_data.get("text", "Done."),
        actions=valid_actions_applied,
        board=refreshed_board
    )

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
