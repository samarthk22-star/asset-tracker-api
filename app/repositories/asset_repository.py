from app.database import get_connection


def create_asset(asset_code, name, category):
    connection = get_connection()
    try:
        cursor = connection.execute(
            "INSERT INTO assets (asset_code, name, category) VALUES (?, ?, ?)",
            (asset_code, name, category)
        )
        connection.commit()
        asset_id = cursor.lastrowid
    finally:
        connection.close()
    return get_asset_by_id(asset_id)


def get_all_assets(limit=20, offset=0):
    connection = get_connection()
    try:
        rows = connection.execute(
            "SELECT id, asset_code, name, category FROM assets ORDER BY id LIMIT ? OFFSET ?",
            (limit, offset)
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        connection.close()


def get_asset_by_id(asset_id):
    connection = get_connection()
    try:
        row = connection.execute(
            "SELECT id, asset_code, name, category FROM assets WHERE id = ?",
            (asset_id,)
        ).fetchone()
        return dict(row) if row else None
    finally:
        connection.close()


def update_asset(asset_id, fields):
    allowed = {"asset_code", "name", "category"}
    fields = {k: v for k, v in fields.items() if k in allowed}

    if not fields:
        return get_asset_by_id(asset_id)

    columns = ", ".join(f"{key} = ?" for key in fields)
    values = list(fields.values()) + [asset_id]

    connection = get_connection()
    try:
        connection.execute(
            f"UPDATE assets SET {columns} WHERE id = ?", values
        )
        connection.commit()
    finally:
        connection.close()
    return get_asset_by_id(asset_id)


def delete_asset(asset_id):
    connection = get_connection()
    try:
        cursor = connection.execute(
            "DELETE FROM assets WHERE id = ?", (asset_id,)
        )
        connection.commit()
        return cursor.rowcount > 0
    finally:
        connection.close()
