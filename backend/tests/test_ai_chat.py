import pytest
from fastapi.testclient import TestClient
from main import app
from sqlmodel import Session, SQLModel, create_engine
from database import get_session
import models, crud
import json
import os

# Setup test DB
engine = create_engine("sqlite://")

def override_get_session():
    with Session(engine) as session:
        yield session

app.dependency_overrides[get_session] = override_get_session

@pytest.fixture(autouse=True)
def setup_db():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        crud.create_default_user_and_board(session)
    yield
    SQLModel.metadata.drop_all(engine)

client = TestClient(app)

def test_ai_chat_create_card(monkeypatch):
    # Mock AI response
    class MockChoice:
        def __init__(self, content):
            self.message = type('obj', (object,), {'content': content})

    class MockResponse:
        def __init__(self, content):
            self.choices = [MockChoice(content)]

    def mock_create(*args, **kwargs):
        # Find the Todo column ID
        with Session(engine) as session:
            board = crud.get_board_for_user(session, "user")
            todo_col = next(c for c in board.columns if c.name == "To Do")
            col_id = todo_col.id
            
        return MockResponse(json.dumps({
            "text": "Sure, I've added the card.",
            "actions": [
                {"action": "create", "column_id": col_id, "title": "Test AI Card", "details": "Created by AI"}
            ]
        }))

    # We need to mock the client instance returned by ai.get_client()
    import ai
    class MockOpenAI:
        def __init__(self, *args, **kwargs):
            self.chat = type('obj', (object,), {'completions': type('obj', (object,), {'create': mock_create})})

    monkeypatch.setattr(ai, "get_client", lambda: MockOpenAI())

    response = client.post("/api/ai/chat", json={"message": "Add a card Test AI Card to To Do"})
    assert response.status_code == 200
    data = response.json()
    assert data["text"] == "Sure, I've added the card."
    
    # Verify card exists in DB
    board_data = data["board"]
    todo_col = next(c for c in board_data["columns"] if c["name"] == "To Do")
    assert any(card["title"] == "Test AI Card" for card in todo_col["cards"])

def test_ai_chat_move_card(monkeypatch):
    # Get a card ID first
    with Session(engine) as session:
        board = crud.get_board_for_user(session, "user")
        card = board.columns[0].cards[0]
        card_id = card.id
        done_col = next(c for c in board.columns if c.name == "Done")
        dest_col_id = done_col.id

    class MockChoice:
        def __init__(self, content):
            self.message = type('obj', (object,), {'content': content})

    class MockResponse:
        def __init__(self, content):
            self.choices = [MockChoice(content)]

    def mock_create(*args, **kwargs):
        return MockResponse(json.dumps({
            "text": "Moved the card.",
            "actions": [
                {"action": "move", "card_id": card_id, "column_id": dest_col_id}
            ]
        }))

    import ai
    class MockOpenAI:
        def __init__(self, *args, **kwargs):
            self.chat = type('obj', (object,), {'completions': type('obj', (object,), {'create': mock_create})})

    monkeypatch.setattr(ai, "get_client", lambda: MockOpenAI())

    response = client.post("/api/ai/chat", json={"message": "Move card to Done"})
    assert response.status_code == 200
    data = response.json()
    
    # Verify move
    board_data = data["board"]
    done_col = next(c for c in board_data["columns"] if c["name"] == "Done")
    assert any(card["id"] == card_id for card in done_col["cards"])

def test_ai_hallucination_logging(monkeypatch):
    # Ensure error.log is clean or we can check its end
    if os.path.exists("error.log"):
        os.remove("error.log")

    class MockChoice:
        def __init__(self, content):
            self.message = type('obj', (object,), {'content': content})

    class MockResponse:
        def __init__(self, content):
            self.choices = [MockChoice(content)]

    def mock_create(*args, **kwargs):
        return MockResponse(json.dumps({
            "text": "I tried to move a non-existent card.",
            "actions": [
                {"action": "move", "card_id": "99999", "column_id": "invalid_col"}
            ]
        }))

    import ai
    class MockOpenAI:
        def __init__(self, *args, **kwargs):
            self.chat = type('obj', (object,), {'completions': type('obj', (object,), {'create': mock_create})})

    monkeypatch.setattr(ai, "get_client", lambda: MockOpenAI())

    response = client.post("/api/ai/chat", json={"message": "Move a ghost card"})
    assert response.status_code == 200
    
    # Check error.log
    assert os.path.exists("error.log")
    with open("error.log", "r") as f:
        log_content = f.read()
        assert "Card ID 99999 does not exist" in log_content
