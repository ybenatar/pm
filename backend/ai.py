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
    """Minifies the board context to save tokens while keeping descriptions."""
    context = []
    for col in board.columns:
        cards = []
        for c in col.cards:
            desc = f" | Description: {c.details}" if c.details.strip() else " | (No description)"
            cards.append(f"[{c.id}] {c.title}{desc}")
        
        context.append(f"Column: {col.name} (ID: {col.id})\nCards:\n  " + ("\n  ".join(cards) if cards else "None"))
    return "\n".join(context)

def get_system_prompt(board: BoardRead) -> str:
    board_context = minify_context(board)
    
    # Using a simple replacement approach to avoid all f-string/brace escaping issues
    template = """You are an expert project management assistant for a Kanban board.
Your task is to help the user manage their cards.

CURRENT BOARD STATE:
{BOARD_CONTEXT}

CONSTRAINTS:
1. You can suggest 'create', 'move', 'delete', or 'edit' actions.
2. For 'create', you MUST provide 'column_id', 'title', and ALWAYS include a 'details' string (description).
3. For 'edit', you can update 'title', 'details', and 'column_id' for an existing 'card_id'.
4. For 'move', you MUST provide the 'card_id' and the destination 'column_id'.
5. For 'delete', you MUST provide the 'card_id'.
6. Use ONLY the provided IDs from the CURRENT BOARD STATE.
7. RESPOND ONLY IN STRICT VALID JSON. Start your response with '{' and end with '}'.

RESPONSE FORMAT:
{
  "text": "Your helpful response here.",
  "actions": [
    { "action": "move", "card_id": "card_id_abc", "column_id": "col_id_xyz", "order": 0 }
  ]
}

EXAMPLE:
User: "Move Write API spec to DONE"
Response:
{
  "text": "Moving the 'Write API spec' card to the DONE column.",
  "actions": [
    { "action": "move", "card_id": "e7286e13", "column_id": "5570654e", "order": 0 }
  ]
}
"""
    return template.replace("{BOARD_CONTEXT}", board_context)
