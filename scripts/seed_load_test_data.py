import sqlite3

from app.database import DATABASE_PATH, init_db


TARGET_ASSETS = 1000
CATEGORIES = ["Electronics", "Furniture", "Accessories", "Networking"]


def main():
    init_db()

    connection = sqlite3.connect(DATABASE_PATH)

    try:
        existing_codes = {
            row[0]
            for row in connection.execute(
                "SELECT asset_code FROM assets"
            ).fetchall()
        }

        inserted = 0
        candidate = 1

        while inserted < TARGET_ASSETS and candidate <= 999999:
            asset_code = f"LOAD-{candidate:06d}"
            candidate += 1

            if asset_code in existing_codes:
                continue

            category = CATEGORIES[inserted % len(CATEGORIES)]
            asset_name = f"Synthetic Load Test Asset {inserted + 1:04d}"

            connection.execute(
                """
                INSERT INTO assets (asset_code, name, category)
                VALUES (?, ?, ?)
                """,
                (asset_code, asset_name, category),
            )

            existing_codes.add(asset_code)
            inserted += 1

        if inserted != TARGET_ASSETS:
            connection.rollback()
            raise RuntimeError(
                f"Only inserted {inserted} of {TARGET_ASSETS} assets"
            )

        connection.commit()

        total = connection.execute(
            "SELECT COUNT(*) FROM assets"
        ).fetchone()[0]

        print(f"Database: {DATABASE_PATH}")
        print(f"New synthetic assets inserted: {inserted}")
        print(f"Total assets in database: {total}")

    finally:
        connection.close()


if __name__ == "__main__":
    main()