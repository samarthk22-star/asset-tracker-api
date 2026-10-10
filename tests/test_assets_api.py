import pytest
from fastapi.testclient import TestClient

import app.database as database
from app.main import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    test_database = tmp_path / "test_assets.db"
    monkeypatch.setattr(database, "DATABASE_PATH", test_database)
    database.init_db()

    with TestClient(app) as test_client:
        yield test_client


def create_asset(client, code="LAP001", name="Dell Laptop", category="Electronics"):
    return client.post(
        "/assets",
        json={
            "asset_code": code,
            "name": name,
            "category": category,
        },
    )


def test_create_and_list_assets(client):
    response = create_asset(client)

    assert response.status_code == 201
    assert response.json()["asset_code"] == "LAP001"

    listed = client.get("/assets")
    assert listed.status_code == 200
    assert len(listed.json()) == 1
    assert listed.json()[0]["name"] == "Dell Laptop"


def test_duplicate_asset_code_returns_conflict(client):
    assert create_asset(client).status_code == 201

    duplicate = create_asset(client, name="Another Laptop")
    assert duplicate.status_code == 409


def test_invalid_asset_input_returns_422(client):
    response = client.post(
        "/assets",
        json={
            "asset_code": "BAD001",
            "name": "   ",
            "category": "Electronics",
        },
    )
    assert response.status_code == 422


def test_missing_asset_returns_404(client):
    assert client.get("/assets/99999").status_code == 404

    assert client.patch(
        "/assets/99999",
        json={"name": "Updated Laptop"},
    ).status_code == 404

    assert client.delete("/assets/99999").status_code == 404


def test_partial_update_preserves_other_fields(client):
    created = create_asset(client)
    asset_id = created.json()["id"]

    response = client.patch(
        f"/assets/{asset_id}",
        json={"name": "Updated Laptop"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": asset_id,
        "asset_code": "LAP001",
        "name": "Updated Laptop",
        "category": "Electronics",
    }


def test_delete_asset_returns_no_content(client):
    created = create_asset(client)
    asset_id = created.json()["id"]

    response = client.delete(f"/assets/{asset_id}")

    assert response.status_code == 204
    assert response.content == b""
    assert client.get(f"/assets/{asset_id}").status_code == 404


def test_asset_list_pagination(client):
    for code in ("LAP001", "LAP002", "LAP003"):
        response = create_asset(client, code=code)
        assert response.status_code == 201

    response = client.get("/assets", params={"limit": 2, "offset": 1})

    assert response.status_code == 200
    assert [asset["asset_code"] for asset in response.json()] == [
        "LAP002",
        "LAP003",
    ]
