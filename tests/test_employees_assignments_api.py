
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


def create_employee(client, code="EMP001", email=None):
    if email is None:
        email = f"{code.lower()}@example.com"

    return client.post("/employees", json={
        "employee_code": code,
        "name": "Sam",
        "email": email,
        "department": "IT",
    })


# Existing assignment and employee asset tests

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
    assert client.post("/assignments", json=data).status_code == 409

    current = client.get(f"/employees/{employee.json()['id']}/assets")
    assert len(current.json()) == 1


def test_missing_assignment_references_return_404(client):
    employee = create_employee(client)
    asset = create_asset(client)

    assert client.post("/assignments", json={
        "asset_id": 99999,
        "employee_id": employee.json()["id"],
    }).status_code == 404

    assert client.post("/assignments", json={
        "asset_id": asset.json()["id"],
        "employee_id": 99999,
    }).status_code == 404


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

    for asset in (first, second):
        response = client.post("/assignments", json={
            "asset_id": asset.json()["id"],
            "employee_id": employee.json()["id"],
        })
        assert response.status_code == 201

    current = client.get(f"/employees/{employee.json()['id']}/assets")
    assert current.status_code == 200
    assert len(current.json()) == 2


def test_employee_without_assets_gets_empty_list(client):
    employee = create_employee(client)
    response = client.get(f"/employees/{employee.json()['id']}/assets")
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
    first = create_employee(client, "EMP001")
    second = create_employee(client, "EMP002")

    response = client.post("/assignments", json={
        "asset_id": asset.json()["id"],
        "employee_id": first.json()["id"],
    })
    assert response.status_code == 201

    first_assets = client.get(
        f"/employees/{first.json()['id']}/assets"
    )
    second_assets = client.get(
        f"/employees/{second.json()['id']}/assets"
    )

    assert len(first_assets.json()) == 1
    assert second_assets.json() == []


# New Day 1 employee management tests

def test_list_employees_with_pagination(client):
    create_employee(client, "EMP001")
    create_employee(client, "EMP002")
    create_employee(client, "EMP003")

    response = client.get("/employees?limit=2&offset=1")
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert [item["employee_code"] for item in response.json()] == [
        "EMP002", "EMP003"
    ]


def test_employee_list_rejects_invalid_pagination(client):
    assert client.get("/employees?limit=0").status_code == 422
    assert client.get("/employees?limit=101").status_code == 422
    assert client.get("/employees?offset=-1").status_code == 422


def test_partial_update_preserves_omitted_fields(client):
    employee = create_employee(client)
    employee_id = employee.json()["id"]

    response = client.patch(
        f"/employees/{employee_id}",
        json={"name": "Alex"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Alex"
    assert data["employee_code"] == "EMP001"
    assert data["email"] == "emp001@example.com"
    assert data["department"] == "IT"


def test_duplicate_employee_email_returns_409(client):
    create_employee(client, "EMP001", "same@example.com")

    response = create_employee(client, "EMP002", "same@example.com")
    assert response.status_code == 409


def test_duplicate_email_on_update_returns_409(client):
    first = create_employee(client, "EMP001", "first@example.com")
    second = create_employee(client, "EMP002", "second@example.com")

    response = client.patch(
        f"/employees/{second.json()['id']}",
        json={"email": "first@example.com"},
    )
    assert response.status_code == 409

    unchanged = client.get(f"/employees/{second.json()['id']}").json()
    assert unchanged["email"] == "second@example.com"


def test_invalid_employee_input_returns_422(client):
    response = client.post("/employees", json={
        "employee_code": "EMP003",
        "name": "Sam",
        "email": "not-an-email",
        "department": "IT",
    })
    assert response.status_code == 422


def test_update_unknown_employee_returns_404(client):
    response = client.patch("/employees/99999", json={"name": "Alex"})
    assert response.status_code == 404


def test_delete_employee_returns_204_with_empty_body(client):
    employee = create_employee(client)
    response = client.delete(f"/employees/{employee.json()['id']}")

    assert response.status_code == 204
    assert response.content == b""


def test_employee_with_assignment_history_cannot_be_deleted(client):
    asset = create_asset(client)
    employee = create_employee(client)

    assignment = client.post("/assignments", json={
        "asset_id": asset.json()["id"],
        "employee_id": employee.json()["id"],
    })
    assert assignment.status_code == 201

    response = client.delete(f"/employees/{employee.json()['id']}")
    assert response.status_code == 409

    assert client.get(f"/employees/{employee.json()['id']}").status_code == 200
