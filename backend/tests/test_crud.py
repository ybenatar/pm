import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from main import app
from database import get_session
import crud
from sqlalchemy.pool import StaticPool

# Natively use extremely rapid in-memory SQLite avoiding hard-drive I/O for tests
sqlite_url = "sqlite:///:memory:"
engine = create_engine(
    sqlite_url, 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

def get_session_override():
    with Session(engine) as session:
        yield session

@pytest.fixture(name="client")
def client_fixture():
    app.dependency_overrides[get_session] = get_session_override
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        crud.create_default_user_and_board(session)
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.pop(get_session, None)
    SQLModel.metadata.drop_all(engine)


def test_health_check(client: TestClient):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_fetch_board(client: TestClient):
    response = client.get("/api/board")
    assert response.status_code == 200
    data = response.json()
    
    assert data["owner_id"] is not None
    assert len(data["columns"]) == 5
    
    # Check default seeded column names
    col_names = [col["name"] for col in data["columns"]]
    assert "To Do" in col_names
    assert "In Progress" in col_names
    assert "Done" in col_names


def test_card_crud_workflow(client: TestClient):
    # 1. Fetch Board to find valid column context
    board_data = client.get("/api/board").json()
    first_col_id = board_data["columns"][0]["id"]
    second_col_id = board_data["columns"][1]["id"]
    
    # 2. Add precisely 1 generic Card
    add_response = client.post("/api/card", json={
        "column_id": first_col_id,
        "title": "Test CRUD Task",
        "details": "Description block testing payload",
        "order": 1
    })
    
    assert add_response.status_code == 200
    card_data = add_response.json()
    assert card_data["title"] == "Test CRUD Task"
    card_id = card_data["id"]
    
    # 3. Simulate complex drag-and-drop Move Event
    move_response = client.put(f"/api/card/{card_id}/move", json={
        "new_column_id": second_col_id,
        "new_order": 0
    })
    
    assert move_response.status_code == 200
    moved_card = move_response.json()
    assert moved_card["column_id"] == second_col_id
    assert moved_card["order"] == 0
    
    # 4. Prove the object persisted accurately by refetching natively
    final_board = client.get("/api/board").json()
    
    second_column = next(c for c in final_board["columns"] if c["id"] == second_col_id)
    assert any(c["id"] == card_id for c in second_column["cards"])
    
    # 5. Destroy the target
    delete_response = client.delete(f"/api/card/{card_id}")
    assert delete_response.status_code == 200
    assert delete_response.json()["status"] == "deleted"
