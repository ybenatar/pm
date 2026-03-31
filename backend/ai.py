import os
import json
from typing import List, Dict, Any
from openai import OpenAI
from models import BoardRead, AIChatResponse

def get_client() -> OpenAI:
    return OpenAI(
        api_key=os.environ.get("OPENROUTER_API_KEY"),
        base_url="https://openrouter.ai/api/v1",
    )

MODEL = "openai/gpt-oss-120b"

def get_history_limit() -> int:
    try:
        return int(os.environ.get("AI_HISTORY_LIMIT", "10"))
    except ValueError:
        return 10

def minify_context(board: BoardRead) -> str:
    """Minifies the board context to save tokens."""
    context = []
    for col in board.columns:
        cards = [f"[{c.id}] {c.title}" for c in col.cards]
        context.append(f"Column: {col.name} (ID: {col.id})\nCards: " + (", ".join(cards) if cards else "None"))
    return "\n".join(context)

def get_system_prompt(board: BoardRead) -> str:
    board_context = minify_context(board)
    
    prompt = f"""You are an expert project management assistant for a Kanban board.
Your task is to help the user manage their cards.

CURRENT BOARD STATE:
{board_context}

CONSTRAINTS:
1. You can suggest creating new cards, moving existing cards, or deleting cards.
2. For 'create', you MUST provide a 'column_id', 'title', and optionally 'details'.
3. For 'move', you MUST provide the 'card_id' and the destination 'column_id'.
4. For 'delete', you MUST provide the 'card_id'.
5. ONLY use the provided IDs for cards and columns. If you refer to an ID that doesn't exist, it will be ignored and logged as an error.
6. RESPOND ONLY IN JSON.

RESPONSE FORMAT:
{{
  "text": "Your helpful response to the user here.",
  "actions": [
    {{ "action": "create", "column_id": "COL_ID", "title": "Buy groceries", "details": "Milk, eggs, bread" }},
    {{ "action": "move", "card_id": "CARD_ID", "column_id": "DEST_COL_ID", "order": 0 }},
    {{ "action": "delete", "card_id": "CARD_ID" }}
  ]
}}
"""
    return prompt
