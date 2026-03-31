# Database Schema

This document outlines the strictly simplified SQLite relational schema powering the Antigravity Kanban MVP. It favors strict integer-based arrays over hyper-optimized systems (like Lexicographical strings) in accordance to the `AGENTS.md` project requirement dictating: `"Keep it simple - NEVER over-engineer, ALWAYS simplify"`.

## High-Level Architecture
Because we utilize Python's `SQLModel` ORM heavily in **Part 6**, these definitions strictly conform exactly to how Pydantic maps data out to the Nuxt frontend naturally.

> [!NOTE] 
> All primary identifiers (`id`) in this database architecture are treated securely as `UUID4` strings natively generated programmatically by the Vue Frontend or Python Backend prior to database insertion.

---

### 1. `User`
The root table required to ensure the system natively supports scaling to multiple real-world users in the future perfectly securely. For the local MVP deployment, this will be seeded silently behind the scenes with exactly one row (`username="user"`, `password_hash="your_hashed_MVP_password"`).

| Field Name      | Data Type | PK / FK      | Description |
| :-------------- | :-------- | :----------- | :---------- |
| `id`            | `String`  | Primary Key  | Unique UUID securely identifying a specific user. |
| `username`      | `String`  | None         | Unique login identity string. |
| `password_hash` | `String`  | None         | Cryptographic representation of the user password. |

---

### 2. `Board`
Acts as the global spatial container. Establishing a Board table uniquely segregates a specific user's column layout logically shielding it safely away from any other future users.

| Field Name | Data Type | PK / FK         | Description |
| :--------- | :-------- | :-------------- | :---------- |
| `id`       | `String`  | Primary Key     | System generated UUID explicitly representing this board instance. |
| `owner_id` | `String`  | FK -> `User.id` | Natively points to the owner to ensure strict multi-tenant data safety. |

---

### 3. `Column`
Represents the fixed states/bins on your Kanban horizontally ("To Do", "In Progress", etc.).

| Field Name | Data Type | PK / FK           | Description |
| :--------- | :-------- | :---------------- | :---------- |
| `id`       | `String`  | Primary Key       | Unique string identifier for this column. |
| `board_id` | `String`  | FK -> `Board.id`  | Points explicitly to the parent Board ensuring compartmentalization. |
| `name`     | `String`  | None              | The visual string headline title (e.g., "Backlog" or "Done"). |
| `order`    | `Integer` | None              | Simple mathematical number determining visual left-to-right rendering priority (e.g., `0`, `1`, `2`). |

---

### 4. `Card`
The core atomic item of the entire Kanban board holding specific task details and state layout priorities.

| Field Name  | Data Type | PK / FK            | Description |
| :---------- | :-------- | :----------------- | :---------- |
| `id`        | `String`  | Primary Key        | Unique card string identification. |
| `column_id` | `String`  | FK -> `Column.id`  | Hard-maps this card physically securely inside its specific parent container. |
| `title`     | `String`  | None               | The bold headline text of the card. |
| `details`   | `String`  | None               | The longer descriptive payload data outlining subtasks. |
| `order`     | `Integer` | None               | **CRITICAL**. Represents vertical prioritization safely mathematically inside a column. `0` = absolute top. Dropping a card recalculates this cluster natively. |
