import sqlite3
from config import DATABASE_URL


class DB:
    def __init__(self):
        self.connection = None
        self.create_tables()

    def create_connection(self):
        if self.connection is None:
            self.connection = sqlite3.connect(DATABASE_URL)
            self.connection.row_factory = sqlite3.Row

    def create_tables(self):
        create_users_table_query = """
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                username TEXT NOT NULL,
                password TEXT NOT NULL
            );
        """
        create_gifts_table_query = """
            CREATE TABLE IF NOT EXISTS gifts (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                cost REAL NOT NULL,
                link TEXT NOT NULL,
                photo TEXT,
                is_reserved BOOLEAN NOT NULL,
                reserve_owner TEXT,
                user_id TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            );
        """

        self.create_connection()
        cursor = self.connection.cursor()

        cursor.execute(create_users_table_query)
        cursor.execute(create_gifts_table_query)

        cursor.connection.commit()

    def get_all_gifts(self) -> list[dict]:
        query = "SELECT * FROM gifts"

        self.create_connection()
        cursor = self.connection.cursor()

        try:
            cursor.execute(query)
            gifts = cursor.fetchall()
            return [dict(gift) for gift in gifts]
        finally:
            cursor.close()

    def get_gifts_by_user_id(self, user_id: str) -> list[dict]:
        query = "SELECT * FROM gifts WHERE user_id = ?"
        self.create_connection()
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, (user_id,))
            gifts = cursor.fetchall()
            return [dict(gift) for gift in gifts]
        finally:
            cursor.close()

    def get_gift_by_id(self, gift_id: str) -> dict | None:
        query = "SELECT * FROM gifts WHERE id = ?"
        self.create_connection()
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, (gift_id,))
            gift = cursor.fetchone()
            if gift:
                return dict(gift)
            return None
        finally:
            cursor.close()

    def add_gift(self, new_gift: dict):
        query = """
                INSERT INTO gifts (id, name, cost, link, photo, is_reserved, reserve_owner, user_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
        self.create_connection()
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                query,
                (
                    new_gift["id"],
                    new_gift["name"],
                    new_gift["cost"],
                    new_gift["link"],
                    new_gift["photo"],
                    new_gift["is_reserved"],
                    new_gift["reserve_owner"],
                    new_gift["user_id"],
                ),
            )
            self.connection.commit()
        finally:
            cursor.close()

    def update_gift(self, gift_id: str, updated_gift: dict):
        query = """
                UPDATE gifts
                SET name = ?, cost = ?, link = ?, photo = ?, is_reserved = ?, reserve_owner = ?, user_id = ?
                WHERE id = ?
            """
        self.create_connection()
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                query,
                (
                    updated_gift["name"],
                    updated_gift["cost"],
                    updated_gift["link"],
                    updated_gift["photo"],
                    updated_gift["is_reserved"],
                    updated_gift["reserve_owner"],
                    updated_gift["user_id"],
                    gift_id,
                ),
            )
            self.connection.commit()
        finally:
            cursor.close()

    def delete_gift(self, gift_id: str):
        query = "DELETE FROM gifts WHERE id = ?"
        self.create_connection()
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, (gift_id,))
            self.connection.commit()
        finally:
            cursor.close()

    def create_user(self, user: dict):
        query = "INSERT INTO users (id, username, password) VALUES (?, ?, ?)"
        self.create_connection()
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                query,
                (user["user_id"], user["username"], user["password"]),
            )
            self.connection.commit()
        finally:
            cursor.close()

    def get_user_by_username(self, username: str):
        query = "SELECT * FROM users WHERE username = ?"
        self.create_connection()
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, (username,))
            user = cursor.fetchone()
            if user:
                return {"user_id": user[0], "username": user[1], "password": user[2]}
            return None
        finally:
            cursor.close()

    def get_user_by_id(self, user_id: str):
        query = "SELECT * FROM users WHERE id = ?"
        self.create_connection()
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, (user_id,))
            user = cursor.fetchone()
            if user:
                return {"user_id": user[0], "username": user[1], "password": None}
            return None
        finally:
            cursor.close()

    def get_all_users(self):
        query = "SELECT * FROM users"
        self.create_connection()
        cursor = self.connection.cursor()
        try:
            cursor.execute(query)
            users = cursor.fetchall()
            return [
                {
                    "user_id": user[0],
                    "username": user[1],
                    "password": user[2],
                }
                for user in users
            ]
        finally:
            cursor.close()

    def close(self):
        if self.connection:
            self.connection.close()
