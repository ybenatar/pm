import logging
import pytest
from fastapi.testclient import TestClient
from main import app
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.pool import StaticPool
from database import get_session
import crud
import json

from conftest import make_mock_openai

engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)

def override_get_session():
    with Session(engine) as session:
        yield session

@pytest.fixture(name="client")
def client_fixture(monkeypatch):
    import database
    monkeypatch.setattr(database, "engine", engine)
    app.dependency_overrides[get_session] = override_get_session
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        crud.create_default_user_and_board(session)
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.pop(get_session, None)
    SQLModel.metadata.drop_all(engine)


def test_ai_chat_create_card(client: TestClient, monkeypatch):
    with Session(engine) as session:
        board = crud.get_board_for_user(session, "user")
        todo_col = next(c for c in board.columns if c.name == "To Do")
        col_id = todo_col.id

    import ai
    monkeypatch.setattr(ai, "get_client", lambda: make_mock_openai({
        "text": "Sure, I've added the card.",
        "actions": [{"action": "create", "column_id": col_id, "title": "Test AI Card", "details": "Created by AI"}]
    }))

    response = client.post("/api/ai/chat", json={"message": "Add a card Test AI Card to To Do"})
    assert response.status_code == 200
    data = response.json()
    assert data["text"] == "Sure, I've added the card."

    todo_col_data = next(c for c in data["board"]["columns"] if c["name"] == "To Do")
    assert any(card["title"] == "Test AI Card" for card in todo_col_data["cards"])


def test_ai_chat_move_card(client: TestClient, monkeypatch):
    with Session(engine) as session:
        board = crud.get_board_for_user(session, "user")
        card = board.columns[0].cards[0]
        card_id = card.id
        done_col = next(c for c in board.columns if c.name == "Done")
        dest_col_id = done_col.id

    import ai
    monkeypatch.setattr(ai, "get_client", lambda: make_mock_openai({
        "text": "Moved the card.",
        "actions": [{"action": "move", "card_id": card_id, "column_id": dest_col_id}]
    }))

    response = client.post("/api/ai/chat", json={"message": "Move card to Done"})
    assert response.status_code == 200
    data = response.json()

    done_col_data = next(c for c in data["board"]["columns"] if c["name"] == "Done")
    assert any(c["id"] == card_id for c in done_col_data["cards"])


def test_ai_hallucination_logging(client: TestClient, monkeypatch, caplog):
    import ai
    monkeypatch.setattr(ai, "get_client", lambda: make_mock_openai({
        "text": "I tried to move a non-existent card.",
        "actions": [{"action": "move", "card_id": "99999", "column_id": "invalid_col"}]
    }))

    with caplog.at_level(logging.ERROR):
        response = client.post("/api/ai/chat", json={"message": "Move a ghost card"})

    assert response.status_code == 200
    assert "Card ID 99999 does not exist" in caplog.text
