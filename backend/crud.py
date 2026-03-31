from sqlmodel import Session, select
from typing import Optional, List
from models import User, Board, Column, Card

def get_user_by_username(session: Session, username: str) -> Optional[User]:
    return session.exec(select(User).where(User.username == username)).first()

def create_default_user_and_board(session: Session):
    user = get_user_by_username(session, "user")
    if not user:
        user = User(username="user", password_hash="dummy_hash")
        session.add(user)
        session.commit()
        session.refresh(user)
        
        board = Board(owner_id=user.id)
        session.add(board)
        session.commit()
        session.refresh(board)
        
        col_backlog = Column(board_id=board.id, name="Backlog", order=0)
        col_todo = Column(board_id=board.id, name="To Do", order=1)
        col_progress = Column(board_id=board.id, name="In Progress", order=2)
        col_review = Column(board_id=board.id, name="In Review", order=3)
        col_done = Column(board_id=board.id, name="Done", order=4)
        
        session.add_all([col_backlog, col_todo, col_progress, col_review, col_done])
        session.commit()

        cards = [
            Card(column_id=col_backlog.id, title="Design system tokens", details="Define color palette, spacing, and typography variables.", order=0),
            Card(column_id=col_backlog.id, title="Set up CI pipeline", details="Configure GitHub Actions to run unit and E2E tests on every PR.", order=1),
            Card(column_id=col_backlog.id, title="Write API spec", details="Draft OpenAPI 3.0 specification for the user management endpoints.", order=2),
            
            Card(column_id=col_todo.id, title="Build login page", details="Email + password login with form validation and error handling.", order=0),
            Card(column_id=col_todo.id, title="Integrate auth tokens", details="Store JWT in httpOnly cookie and refresh on expiry.", order=1),
            
            Card(column_id=col_progress.id, title="Kanban drag-and-drop", details="Implement card drag between columns using vue-draggable-plus.", order=0),
            Card(column_id=col_progress.id, title="Responsive layout", details="Ensure the board is usable on tablet-width viewports.", order=1),
            
            Card(column_id=col_review.id, title="Accessibility audit", details="Run axe-core and fix all critical WCAG AA violations.", order=0),
            
            Card(column_id=col_done.id, title="Project scaffolding", details="Nuxt 3 app initialised with TypeScript, Vitest, and Playwright.", order=0),
            Card(column_id=col_done.id, title="Color scheme defined", details="Navy, yellow, purple, blue, and gray tokens agreed with the team.", order=1),
        ]
        session.add_all(cards)
        session.commit()

def get_board_for_user(session: Session, username: str) -> Optional[Board]:
    user = get_user_by_username(session, username)
    if not user or not user.boards:
        return None
    return user.boards[0]

def rename_column(session: Session, column_id: str, new_name: str) -> Optional[Column]:
    col = session.get(Column, column_id)
    if col:
        col.name = new_name
        session.add(col)
        session.commit()
        session.refresh(col)
    return col

def create_card(session: Session, column_id: str, title: str, details: str, order: int) -> Card:
    card = Card(column_id=column_id, title=title, details=details, order=order)
    session.add(card)
    session.commit()
    session.refresh(card)
    return card

def delete_card(session: Session, card_id: str) -> bool:
    card = session.get(Card, card_id)
    if card:
        session.delete(card)
        session.commit()
        return True
    return False

def move_card(session: Session, card_id: str, new_column_id: str, new_order: int) -> Optional[Card]:
    card = session.get(Card, card_id)
    if not card:
        return None

    # Shift cards in target column to make room safely
    target_cards = session.exec(
        select(Card)
        .where(Card.column_id == new_column_id)
        .where(Card.order >= new_order)
        .where(Card.id != card_id)
    ).all()
    
    for t_card in target_cards:
        t_card.order += 1
        session.add(t_card)
        
    card.column_id = new_column_id
    card.order = new_order
    session.add(card)
    
    session.commit()
    session.refresh(card)
    return card
