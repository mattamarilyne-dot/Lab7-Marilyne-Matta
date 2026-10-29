import sqlite3
import pytest
import app as user_app


@pytest.fixture
def test_database(tmp_path, monkeypatch):
    
    database_path = tmp_path / "test_database.db"

    def connect_to_test_db():
        return sqlite3.connect(database_path)

    monkeypatch.setattr(user_app, "connect_to_db", connect_to_test_db)

    user_app.create_db_table()

    return database_path


def test_database_creation(test_database):
    conn = sqlite3.connect(test_database)

    cursor = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='users'"
    )

    assert cursor.fetchone() is not None

    columns = [
        row[1]
        for row in conn.execute("PRAGMA table_info(users)")
    ]

    assert columns == [
        "user_id",
        "name",
        "email",
        "phone",
        "address",
        "country"
    ]

    conn.close()

def test_insert_user(test_database):
    new_user = {
        "name": "Marilyne Matta",
        "email": "marilyne@example.com",
        "phone": "12345678",
        "address": "Beirut",
        "country": "Lebanon"
    }

    inserted_user = user_app.insert_user(new_user)

    assert inserted_user["name"] == "Marilyne Matta"
    assert inserted_user["email"] == "marilyne@example.com"
    assert inserted_user["phone"] == "12345678"
    assert inserted_user["address"] == "Beirut"
    assert inserted_user["country"] == "Lebanon"

    assert "user_id" in inserted_user

    users = user_app.get_users()
    assert len(users) == 1
    assert users[0]["user_id"] == inserted_user["user_id"]

def test_get_users(test_database):
    user1 = {
        "name": "Marilyne Matta",
        "email": "marilyne@example.com",
        "phone": "12345678",
        "address": "Beirut",
        "country": "Lebanon"
    }

    user2 = {
        "name": "John Smith",
        "email": "john@example.com",
        "phone": "87654321",
        "address": "Tripoli",
        "country": "Lebanon"
    }

    user_app.insert_user(user1)
    user_app.insert_user(user2)

    users = user_app.get_users()

    assert len(users) == 2
    assert users[0]["name"] == "Marilyne Matta"
    assert users[0]["email"] == "marilyne@example.com"
    assert users[1]["name"] == "John Smith"
    assert users[1]["email"] == "john@example.com"

def test_get_user_by_id(test_database):
    user1 = {
        "name": "Marilyne Matta",
        "email": "marilyne@example.com",
        "phone": "12345678",
        "address": "Beirut",
        "country": "Lebanon"
    }

    user2 = {
        "name": "John Smith",
        "email": "john@example.com",
        "phone": "87654321",
        "address": "Tripoli",
        "country": "Lebanon"
    }

    user_app.insert_user(user1)
    inserted_user2 = user_app.insert_user(user2)

    user_id = inserted_user2["user_id"]

    retrieved_user = user_app.get_user_by_id(user_id)

    assert retrieved_user["user_id"] == user_id
    assert retrieved_user["name"] == "John Smith"
    assert retrieved_user["email"] == "john@example.com"
    assert retrieved_user["phone"] == "87654321"
    assert retrieved_user["address"] == "Tripoli"
    assert retrieved_user["country"] == "Lebanon"

def test_update_user(test_database):
    user = {
        "name": "John Smith",
        "email": "john@example.com",
        "phone": "12345678",
        "address": "Tripoli",
        "country": "Lebanon"
    }

    inserted_user = user_app.insert_user(user)

    updated_data = {
        "user_id": inserted_user["user_id"],
        "name": "John Johnson",
        "email": "johnjohnson@example.com",
        "phone": "87654321",
        "address": "Beirut",
        "country": "Lebanon"
    }

    updated_user = user_app.update_user(updated_data)

    assert updated_user["user_id"] == inserted_user["user_id"]
    assert updated_user["name"] == "John Johnson"
    assert updated_user["email"] == "johnjohnson@example.com"
    assert updated_user["phone"] == "87654321"
    assert updated_user["address"] == "Beirut"
    assert updated_user["country"] == "Lebanon"

    saved_user = user_app.get_user_by_id(inserted_user["user_id"])

    assert saved_user == updated_data

def test_delete_user(test_database):
    user = {
        "name": "John Smith",
        "email": "john@example.com",
        "phone": "12345678",
        "address": "Beirut",
        "country": "Lebanon"
    }

    inserted_user = user_app.insert_user(user)
    user_id = inserted_user["user_id"]

    assert user_app.get_user_by_id(user_id)["name"] == "John Smith"

    result = user_app.delete_user(user_id)

    assert result["status"] == "User deleted successfully"

    deleted_user = user_app.get_user_by_id(user_id)
    assert deleted_user == {}

    assert len(user_app.get_users()) == 0

def test_api_get_user(test_database):
    user = {
        "name": "John Smith",
        "email": "john@example.com",
        "phone": "12345678",
        "address": "Beirut",
        "country": "Lebanon"
    }

    inserted_user = user_app.insert_user(user)
    user_id = inserted_user["user_id"]

    client = user_app.app.test_client()

    response = client.get(f"/api/users/{user_id}")

    assert response.status_code == 200

    data = response.get_json()

    assert data["user_id"] == user_id
    assert data["name"] == "John Smith"
    assert data["email"] == "john@example.com"
    assert data["phone"] == "12345678"
    assert data["address"] == "Beirut"
    assert data["country"] == "Lebanon"

def test_api_add_user(test_database):
    user = {
        "name": "John Smith",
        "email": "john@example.com",
        "phone": "12345678",
        "address": "Beirut",
        "country": "Lebanon"
    }

    client = user_app.app.test_client()

    response = client.post("/api/users/add", json=user)

    assert response.status_code == 200

    data = response.get_json()

    assert data["name"] == "John Smith"
    assert data["email"] == "john@example.com"
    assert data["phone"] == "12345678"
    assert data["address"] == "Beirut"
    assert data["country"] == "Lebanon"
    assert "user_id" in data

    saved_user = user_app.get_user_by_id(data["user_id"])

    assert saved_user == data

def test_api_update_user(test_database):
    user = {
        "name": "John Smith",
        "email": "john@example.com",
        "phone": "12345678",
        "address": "Tripoli",
        "country": "Lebanon"
    }

    inserted_user = user_app.insert_user(user)

    updated_data = {
        "user_id": inserted_user["user_id"],
        "name": "John Johnson",
        "email": "johnjohnson@example.com",
        "phone": "87654321",
        "address": "Beirut",
        "country": "Lebanon"
    }

    client = user_app.app.test_client()

    response = client.put("/api/users/update", json=updated_data)

    assert response.status_code == 200

    data = response.get_json()

    assert data["user_id"] == inserted_user["user_id"]
    assert data["name"] == "John Johnson"
    assert data["email"] == "johnjohnson@example.com"
    assert data["phone"] == "87654321"
    assert data["address"] == "Beirut"
    assert data["country"] == "Lebanon"

    saved_user = user_app.get_user_by_id(inserted_user["user_id"])

    assert saved_user == updated_data

def test_api_delete_user(test_database):
    user = {
        "name": "John Smith",
        "email": "john@example.com",
        "phone": "12345678",
        "address": "Beirut",
        "country": "Lebanon"
    }

    inserted_user = user_app.insert_user(user)
    user_id = inserted_user["user_id"]

    client = user_app.app.test_client()

    response = client.delete(f"/api/users/delete/{user_id}")

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "User deleted successfully"

    deleted_user = user_app.get_user_by_id(user_id)

    assert deleted_user == {}
    assert len(user_app.get_users()) == 0

