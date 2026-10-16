import pytest
from fastapi.testclient import TestClient

import app.database as database
from app.main import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DATABASE_PATH", tmp_path / "test.db")
    database.init_db()
    with TestClient(app) as test_client:
        yield test_client


def create_asset(client, code="LAP001"):
    return client.post("/assets", json={
        "asset_code": code,
        "name": "Laptop",
        "category": "Electronics",
    })


def create_employee(client, code="EMP001"):
    return client.post("/employees", json={
        "employee_code": code,
        "name": "Sam",
        "department": "IT",
    })


def test_assignment_and_current_assets(client):
    asset = create_asset(client)
    employee = create_employee(client)
    assert asset.status_code == 201
    assert employee.status_code == 201

    asset_id = asset.json()["id"]
    employee_id = employee.json()["id"]

    assignment = client.post("/assignments", json={
        "asset_id": asset_id,
        "employee_id": employee_id,
    })
    assert assignment.status_code == 201

    current = client.get(f"/employees/{employee_id}/assets")
    assert current.status_code == 200
    assert any(item["id"] == asset_id for item in current.json())


def test_duplicate_assignment_is_rejected(client):
    asset = create_asset(client)
    employee = create_employee(client)
    data = {
        "asset_id": asset.json()["id"],
        "employee_id": employee.json()["id"],
    }

    assert client.post("/assignments", json=data).status_code == 201
    duplicate = client.post("/assignments", json=data)
    assert duplicate.status_code == 409

    current = client.get(
        f"/employees/{employee.json()['id']}/assets"
    )
    assert len(current.json()) == 1


def test_missing_assignment_references_return_404(client):
    employee = create_employee(client)
    asset = create_asset(client)

    missing_asset = client.post("/assignments", json={
        "asset_id": 99999,
        "employee_id": employee.json()["id"],
    })
    assert missing_asset.status_code == 404

    missing_employee = client.post("/assignments", json={
        "asset_id": asset.json()["id"],
        "employee_id": 99999,
    })
    assert missing_employee.status_code == 404


def test_assigned_asset_cannot_be_deleted(client):
    asset = create_asset(client)
    employee = create_employee(client)

    assigned = client.post("/assignments", json={
        "asset_id": asset.json()["id"],
        "employee_id": employee.json()["id"],
    })
    assert assigned.status_code == 201

    response = client.delete(f"/assets/{asset.json()['id']}")
    assert response.status_code == 409
    assert client.get(f"/assets/{asset.json()['id']}").status_code == 200


def test_employee_can_have_multiple_assets(client):
    first = create_asset(client, "LAP001")
    second = create_asset(client, "LAP002")
    employee = create_employee(client)
    employee_id = employee.json()["id"]

    for asset in (first, second):
        response = client.post("/assignments", json={
            "asset_id": asset.json()["id"],
            "employee_id": employee_id,
        })
        assert response.status_code == 201

    current = client.get(f"/employees/{employee_id}/assets")
    assert current.status_code == 200
    assert len(current.json()) == 2


def test_employee_without_assets_gets_empty_list(client):
    employee = create_employee(client)
    response = client.get(
        f"/employees/{employee.json()['id']}/assets"
    )
    assert response.status_code == 200
    assert response.json() == []


def test_unknown_employee_returns_404(client):
    assert client.get("/employees/99999").status_code == 404
    assert client.get("/employees/99999/assets").status_code == 404

def test_missing_employee_assignment_does_not_insert_row(client):
    asset = create_asset(client)

    response = client.post("/assignments", json={
        "asset_id": asset.json()["id"],
        "employee_id": 99999,
    })

    assert response.status_code == 404

    connection = database.get_connection()
    try:
        count = connection.execute(
            "SELECT COUNT(*) FROM assignments"
        ).fetchone()[0]
        assert count == 0
    finally:
        connection.close()


def test_employee_assets_are_isolated(client):
    asset = create_asset(client)
    first_employee = create_employee(client, "EMP001")
    second_employee = create_employee(client, "EMP002")

    response = client.post("/assignments", json={
        "asset_id": asset.json()["id"],
        "employee_id": first_employee.json()["id"],
    })
    assert response.status_code == 201

    first_assets = client.get(
        f"/employees/{first_employee.json()['id']}/assets"
    )
    second_assets = client.get(
        f"/employees/{second_employee.json()['id']}/assets"
    )

    assert len(first_assets.json()) == 1
    assert second_assets.json() == []