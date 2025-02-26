import sqlite3
import json
import bcrypt


class DB:
    def __init__(self):
        self.db = sqlite3.connect("gifts.db")
        self.db.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                username TEXT NOT NULL,
                password TEXT NOT NULL
            );
        """
        )
        self.db.execute(
            """
            CREATE TABLE IF NOT EXISTS gifts (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                cost REAL NOT NULL,
                link TEXT NOT NULL,
                photo TEXT,
                is_reserved BOOLEAN NOT NULL,
                user_id TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            );
        """
        )
        self.db.commit()

    def get_all_gifts(self) -> list[dict]:
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM gifts")
        gifts = cursor.fetchall()
        cursor.close()

        gifts_list = [
            {
                "id": gift[0],
                "name": gift[1],
                "cost": gift[2],
                "link": gift[3],
                "photo": gift[4],
                "is_reserved": gift[5],
                "user_id": gift[6],
            }
            for gift in gifts
        ]
        return gifts_list

    def get_gifts_by_user_id(self, user_id: str) -> list[dict]:
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM gifts WHERE user_id = ?", (user_id,))
        gifts = cursor.fetchall()
        cursor.close()

        gifts_list = [
            {
                "id": gift[0],
                "name": gift[1],
                "cost": gift[2],
                "link": gift[3],
                "photo": gift[4],
                "is_reserved": gift[5],
                "user_id": gift[6],
            }
            for gift in gifts
        ]
        return gifts_list

    def get_gift_by_id(self, gift_id: str) -> dict | None:
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM gifts WHERE id = ?", (gift_id,))
        gift = cursor.fetchone()
        cursor.close()

        if gift:
            return {
                "id": gift[0],
                "name": gift[1],
                "cost": gift[2],
                "link": gift[3],
                "photo": gift[4],
                "is_reserved": gift[5],
                "user_id": gift[6],
            }
        return None

    def add_gift(self, new_gift: dict):
        cursor = self.db.cursor()
        cursor.execute(
            """
            INSERT INTO gifts (id, name, cost, link, photo, is_reserved, user_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                new_gift["id"],
                new_gift["name"],
                new_gift["cost"],
                new_gift["link"],
                new_gift["photo"],
                new_gift["is_reserved"],
                new_gift["user_id"],
            ),
        )
        self.db.commit()
        cursor.close()

    def update_gift(self, gift_id: str, updated_gift: dict):
        cursor = self.db.cursor()
        cursor.execute(
            """
            UPDATE gifts
            SET name = ?, cost = ?, link = ?, photo = ?, is_reserved = ?, user_id = ?
            WHERE id = ?
        """,
            (
                updated_gift["name"],
                updated_gift["cost"],
                updated_gift["link"],
                updated_gift["photo"],
                updated_gift["is_reserved"],
                updated_gift["user_id"],
                gift_id,
            ),
        )
        self.db.commit()
        cursor.close()

    def delete_gift(self, gift_id: str):
        cursor = self.db.cursor()
        cursor.execute("DELETE FROM gifts WHERE id = ?", (gift_id,))
        self.db.commit()
        cursor.close()

    def create_user(self, user: dict):
        hashed_password = bcrypt.hashpw(
            user["password"].encode("utf-8"), bcrypt.gensalt()
        )
        cursor = self.db.cursor()
        cursor.execute(
            "INSERT INTO users (id, username, password) VALUES (?, ?, ?)",
            (user["id"], user["username"], hashed_password.decode("utf-8")),
        )
        self.db.commit()
        cursor.close()

    def get_user_by_username(self, username: str):
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        cursor.close()
        return user

    def close(self):
        self.db.close()
