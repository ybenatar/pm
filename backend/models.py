import uuid
from typing import List, Optional
from sqlmodel import Field, Relationship, SQLModel

def generate_uuid():
    # Use standard 8 character hashes mimicking our Vue frontend 'uid()' helper
    return uuid.uuid4().hex[:8]

class User(SQLModel, table=True):
    id: str = Field(default_factory=generate_uuid, primary_key=True)
    username: str = Field(unique=True, index=True)
    password_hash: str
    
    boards: List["Board"] = Relationship(back_populates="owner")

class Board(SQLModel, table=True):
    id: str = Field(default_factory=generate_uuid, primary_key=True)
    owner_id: str = Field(foreign_key="user.id")
    
    owner: User = Relationship(back_populates="boards")
    columns: List["Column"] = Relationship(back_populates="board")

class Column(SQLModel, table=True):
    id: str = Field(default_factory=generate_uuid, primary_key=True)
    board_id: str = Field(foreign_key="board.id")
    name: str
    order: int
    
    board: Board = Relationship(back_populates="columns")
    cards: List["Card"] = Relationship(back_populates="column_relation")

class Card(SQLModel, table=True):
    id: str = Field(default_factory=generate_uuid, primary_key=True)
    column_id: str = Field(foreign_key="column.id")
    title: str
    details: str
    order: int
    
    column_relation: Column = Relationship(back_populates="cards")

# --- READ MODELS FOR API SERIALIZATION ---
class CardRead(SQLModel):
    id: str
    column_id: str
    title: str
    details: str
    order: int

class ColumnRead(SQLModel):
    id: str
    board_id: str
    name: str
    order: int
    cards: List[CardRead] = []

class BoardRead(SQLModel):
    id: str
    owner_id: str
    columns: List[ColumnRead] = []

# --- AI CHAT MODELS ---
class KanbanAction(SQLModel):
    action: str  # "create", "move", "delete"
    card_id: Optional[str] = None
    column_id: Optional[str] = None
    title: Optional[str] = None
    details: Optional[str] = None
    order: Optional[int] = 0

class AIChatResponse(SQLModel):
    text: str
    actions: List[KanbanAction]
    board: Optional[BoardRead] = None
